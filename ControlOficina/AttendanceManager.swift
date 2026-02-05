import Foundation
import AppKit
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
    @Published var officeGateway: String = "10.15.16.1" {
        didSet {
            userDefaults.set(officeGateway, forKey: "officeGateway")
        }
    }
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
    private let userDefaults = UserDefaults.standard
    private let recordsKey = "attendanceRecords"
    private let holidaysCacheKey = "cachedHolidays"
    private let queue = DispatchQueue(label: "com.controloficina.background", qos: .utility)
    
    init() {
        // Cargar configuraciones
        if let savedGateway = userDefaults.string(forKey: "officeGateway") {
            officeGateway = savedGateway
        }
        checkInterval = userDefaults.integer(forKey: "checkInterval")
        if checkInterval == 0 {
            checkInterval = 3600 // Default 1 hora
        }
        
        loadMonthData()
        fetchHolidays()
        startMonitoring()
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
    
    private func restartMonitoring() {
        // Cancelar el timer existente
        timer?.cancel()
        // Reiniciar con el nuevo intervalo
        startMonitoring()
    }
    
    func refreshData() {
        // Función pública para actualizar datos cuando el usuario abre el popover
        checkGateway()
    }
    
    func checkGateway() {
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Obtener el gateway actual usando netstat
            let task = Process()
            task.launchPath = "/usr/sbin/netstat"
            task.arguments = ["-rn"]
            
            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = FileHandle.nullDevice
            
            do {
                try task.run()
                task.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let output = String(data: data, encoding: .utf8) {
                // Buscar la línea con "default" para obtener el gateway
                let lines = output.components(separatedBy: "\n")
                for line in lines {
                    if line.contains("default") {
                        let components = line.split(separator: " ").map(String.init)
                        if components.count >= 2 {
                            currentGateway = components[1]
                            break
                        }
                    }
                }
            }
        } catch {
            self.currentGateway = nil
        }
        
        // Verificar si estamos en la oficina
        let wasConnected = self.isConnectedToOffice
        let newConnectionStatus = self.currentGateway == self.officeGateway
        
        DispatchQueue.main.async {
            self.isConnectedToOffice = newConnectionStatus
            
            // Si acabamos de conectarnos a la oficina, registrar el d\u00eda
            if self.isConnectedToOffice && !self.todayRegistered {
                self.registerToday()
            }
            
            // Recargar datos del mes si cambi\u00f3 el estado
            if self.isConnectedToOffice != wasConnected {
                self.loadMonthData()
            }
        }
        }
    }
    
    private func registerToday() {
        let today = Calendar.current.startOfDay(for: Date())
        
        var records = loadAllRecords()
        
        // Verificar si ya existe un registro para hoy
        let alreadyExists = records.contains { Calendar.current.isDate($0.date, inSameDayAs: today) }
        
        if !alreadyExists {
            let newRecord = DayRecord(date: today)
            records.append(newRecord)
            saveRecords(records)
        }
        
        todayRegistered = true
        loadMonthData()
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
    }
}
