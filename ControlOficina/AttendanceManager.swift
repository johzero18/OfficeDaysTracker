import Foundation
import AppKit
import Network
import ServiceManagement

struct DayRecord: Codable, Identifiable {
    let id: UUID
    let date: Date
    
    init(date: Date) {
        self.id = UUID()
        self.date = Calendar.current.startOfDay(for: date)
    }
}

struct Feriado: Codable {
    let fecha: String
    let nombre: String
    let tipo: String
}

class AttendanceManager: ObservableObject {
    @Published var isConnectedToOffice = false
    @Published var daysThisMonth: Int = 0
    @Published var todayRegistered: Bool = false
    @Published var workdaysRemaining: Int = 0
    @Published var launchAtLogin: Bool = false {
        didSet {
            setLaunchAtLogin(launchAtLogin)
        }
    }
    @Published private(set) var officeGateways: [String] = []
    @Published var checkInterval: Int = 3600 {
        didSet {
            userDefaults.set(checkInterval, forKey: "checkInterval")
            restartMonitoring()
        }
    }
    
    let monthlyGoal = 8
    private var holidays: [String] = []
    @Published var currentGateway: String?
    
    // Cache
    private var cachedRecords: [DayRecord]?
    private var lastRecordsLoad: Date?
    private var lastHolidaysFetch: (month: Int, year: Int)?
    
    private var timer: DispatchSourceTimer?
    private let pathMonitor = NWPathMonitor()
    private let userDefaults = UserDefaults.standard
    private let recordsKey = "attendanceRecords"
    private let holidaysCacheKey = "cachedHolidays"
    private let officeGatewaysKey = "officeGateways"
    private let queue = DispatchQueue(label: "com.controloficina.background", qos: .utility)
    
    init() {
        // Cargar configuraciones
        if let savedGateways = userDefaults.stringArray(forKey: officeGatewaysKey) {
            officeGateways = savedGateways
        } else if let savedGateway = userDefaults.string(forKey: "officeGateway") {
            officeGateways = [savedGateway]
            userDefaults.set(officeGateways, forKey: officeGatewaysKey)
        } else {
            officeGateways = ["10.15.16.1"]
            userDefaults.set(officeGateways, forKey: officeGatewaysKey)
        }
        checkInterval = userDefaults.integer(forKey: "checkInterval")
        if checkInterval == 0 {
            checkInterval = 3600 // Default 1 hora
        }
        
        loadMonthData()
        fetchHolidays()
        startMonitoring()
        startNetworkMonitoring()
        loadLaunchAtLoginState()
    }
    
    private func loadLaunchAtLoginState() {
        launchAtLogin = userDefaults.bool(forKey: "launchAtLogin")
    }
    
    private func setLaunchAtLogin(_ enabled: Bool) {
        userDefaults.set(enabled, forKey: "launchAtLogin")
        
        if #available(macOS 13.0, *) {
            do {
                if enabled {
                    try SMAppService.mainApp.register()
                } else {
                    try SMAppService.mainApp.unregister()
                }
            } catch {
                print("Error configurando auto-inicio: \(error.localizedDescription)")
            }
        }
    }
    
    private func startMonitoring() {
        // Verificar inmediatamente
        checkGateway()
        
        // Usar DispatchSourceTimer (más eficiente que Timer)
        let timer = DispatchSource.makeTimerSource(queue: queue)
        let interval = DispatchTimeInterval.seconds(checkInterval)
        timer.schedule(deadline: .now() + interval, repeating: interval)
        timer.setEventHandler { [weak self] in
            DispatchQueue.main.async {
                self?.checkGateway()
            }
        }
        timer.resume()
        self.timer = timer
    }

    private func startNetworkMonitoring() {
        pathMonitor.pathUpdateHandler = { [weak self] _ in
            self?.checkGateway()
        }
        pathMonitor.start(queue: queue)
    }
    
    private func restartMonitoring() {
        // Cancelar el timer existente
        timer?.cancel()
        // Reiniciar con el nuevo intervalo
        startMonitoring()
    }
    
    func refreshData() {
        // Función pública para actualizar datos cuando el usuario abre el popover
        loadMonthData()
        fetchHolidays()
        checkGateway()
    }
    
    func checkGateway() {
        queue.async { [weak self] in
            guard let self = self else { return }

            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/sbin/netstat")
            task.arguments = ["-rn"]

            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = FileHandle.nullDevice
            var detectedGateway: String?

            do {
                try task.run()
                task.waitUntilExit()

                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                if let output = String(data: data, encoding: .utf8) {
                    for line in output.components(separatedBy: "\n") where line.hasPrefix("default") {
                        let components = line.split(separator: " ").map(String.init)
                        if components.count >= 2 {
                            detectedGateway = components[1]
                            break
                        }
                    }
                }
            } catch {
                detectedGateway = nil
            }

            DispatchQueue.main.async {
                self.currentGateway = detectedGateway
                self.isConnectedToOffice = detectedGateway.map(self.officeGateways.contains) ?? false
                self.loadMonthData()

                if self.isConnectedToOffice && !self.todayRegistered {
                    self.registerToday()
                }

                self.fetchHolidays()
            }
        }
    }
    
    private func registerToday() {
        setAttendance(on: Date(), attended: true)
    }

    func isRegistered(on date: Date) -> Bool {
        loadAllRecords().contains { Calendar.current.isDate($0.date, inSameDayAs: date) }
    }

    func setAttendance(on date: Date, attended: Bool) {
        let day = Calendar.current.startOfDay(for: date)
        var records = loadAllRecords()

        if attended {
            if !records.contains(where: { Calendar.current.isDate($0.date, inSameDayAs: day) }) {
                records.append(DayRecord(date: day))
            }
        } else {
            records.removeAll { Calendar.current.isDate($0.date, inSameDayAs: day) }
        }

        saveRecords(records)
        loadMonthData()
    }

    func setOfficeGateways(_ gateways: [String]) {
        officeGateways = Array(Set(gateways)).sorted()
        userDefaults.set(officeGateways, forKey: officeGatewaysKey)
        checkGateway()
    }
    
    private func loadAllRecords() -> [DayRecord] {
        // Cache: solo recargar si han pasado más de 5 minutos o no hay cache
        if let cached = cachedRecords,
           let lastLoad = lastRecordsLoad,
           Date().timeIntervalSince(lastLoad) < 300 {
            return cached
        }
        
        guard let data = userDefaults.data(forKey: recordsKey),
              let records = try? JSONDecoder().decode([DayRecord].self, from: data) else {
            cachedRecords = []
            lastRecordsLoad = Date()
            return []
        }
        
        cachedRecords = records
        lastRecordsLoad = Date()
        return records
    }
    
    private func saveRecords(_ records: [DayRecord]) {
        // Mantener solo los últimos 12 meses
        let cutoffDate = Calendar.current.date(byAdding: .month, value: -12, to: Date())!
        let filteredRecords = records.filter { $0.date > cutoffDate }
        
        if let data = try? JSONEncoder().encode(filteredRecords) {
            userDefaults.set(data, forKey: recordsKey)
            // Invalidar cache
            cachedRecords = filteredRecords
            lastRecordsLoad = Date()
        }
    }
    
    func loadMonthData() {
        let records = loadAllRecords()
        let calendar = Calendar.current
        let now = Date()
        
        // Contar días del mes actual
        let currentMonth = calendar.component(.month, from: now)
        let currentYear = calendar.component(.year, from: now)
        
        daysThisMonth = records.filter { record in
            let recordMonth = calendar.component(.month, from: record.date)
            let recordYear = calendar.component(.year, from: record.date)
            return recordMonth == currentMonth && recordYear == currentYear
        }.count
        
        // Verificar si hoy ya está registrado
        let today = calendar.startOfDay(for: now)
        todayRegistered = records.contains { calendar.isDate($0.date, inSameDayAs: today) }
        
        // Calcular días hábiles restantes
        calculateWorkdaysRemaining()
    }
    
    func getRecordsForCurrentMonth() -> [DayRecord] {
        let records = loadAllRecords()
        let calendar = Calendar.current
        let now = Date()
        
        let currentMonth = calendar.component(.month, from: now)
        let currentYear = calendar.component(.year, from: now)
        
        return records.filter { record in
            let recordMonth = calendar.component(.month, from: record.date)
            let recordYear = calendar.component(.year, from: record.date)
            return recordMonth == currentMonth && recordYear == currentYear
        }.sorted { $0.date < $1.date }
    }
    
    var progressPercentage: Double {
        return min(Double(daysThisMonth) / Double(monthlyGoal), 1.0)
    }
    
    var goalReached: Bool {
        return daysThisMonth >= monthlyGoal
    }
    
    var daysRemaining: Int {
        return max(monthlyGoal - daysThisMonth, 0)
    }
    
    private func fetchHolidays() {
        let calendar = Calendar.current
        let now = Date()
        let year = calendar.component(.year, from: now)
        let month = calendar.component(.month, from: now)
        
        // Solo recargar si es un mes diferente
        if let lastFetch = lastHolidaysFetch,
           lastFetch.month == month && lastFetch.year == year {
            return
        }
        
        // Intentar cargar desde cache
        if let cachedData = userDefaults.data(forKey: holidaysCacheKey),
           let cached = try? JSONDecoder().decode([String: [String]].self, from: cachedData),
           let monthHolidays = cached["\(year)-\(month)"] {
            self.holidays = monthHolidays
            self.lastHolidaysFetch = (month, year)
            self.calculateWorkdaysRemaining()
            return
        }
        
        let urlString = "https://api.argentinadatos.com/api/v2/feriados/\(year)/\(month)"
        guard let url = URL(string: urlString) else { return }
        
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            guard let data = data, error == nil else { return }
            
            if let feriados = try? JSONDecoder().decode([Feriado].self, from: data) {
                let holidayDates = feriados.map { $0.fecha }
                
                DispatchQueue.main.async {
                    self?.holidays = holidayDates
                    self?.lastHolidaysFetch = (month, year)
                    self?.calculateWorkdaysRemaining()
                    
                    // Guardar en cache
                    var cache = [String: [String]]()
                    if let cachedData = self?.userDefaults.data(forKey: self?.holidaysCacheKey ?? ""),
                       let existing = try? JSONDecoder().decode([String: [String]].self, from: cachedData) {
                        cache = existing
                    }
                    cache["\(year)-\(month)"] = holidayDates
                    
                    if let encoded = try? JSONEncoder().encode(cache) {
                        self?.userDefaults.set(encoded, forKey: self?.holidaysCacheKey ?? "")
                    }
                }
            }
        }.resume()
    }
    
    private func calculateWorkdaysRemaining() {
        let calendar = Calendar.current
        let now = Date()
        let currentDay = calendar.component(.day, from: now)
        let year = calendar.component(.year, from: now)
        let month = calendar.component(.month, from: now)
        
        // Obtener el último día del mes
        let range = calendar.range(of: .day, in: .month, for: now)!
        let lastDay = range.upperBound - 1
        
        var workdays = 0
        
        guard currentDay < lastDay else {
            workdaysRemaining = 0
            return
        }

        for day in (currentDay + 1)...lastDay {
            let components = DateComponents(year: year, month: month, day: day)
            guard let date = calendar.date(from: components) else { continue }
            
            let weekday = calendar.component(.weekday, from: date)
            let dateString = ISO8601DateFormatter().string(from: date).prefix(10)
            
            // Lunes (2) a Viernes (6)
            let isWeekday = weekday >= 2 && weekday <= 6
            let isHoliday = holidays.contains(String(dateString))
            
            if isWeekday && !isHoliday {
                workdays += 1
            }
        }
        
        workdaysRemaining = workdays
    }
    
    func validateGateway(_ gateway: String) -> Bool {
        let parts = gateway.split(separator: ".")
        guard parts.count == 4 else { return false }
        
        for part in parts {
            guard let num = Int(part), num >= 0, num <= 255 else {
                return false
            }
        }
        return true
    }
    
    deinit {
        timer?.cancel()
        pathMonitor.cancel()
    }
}
