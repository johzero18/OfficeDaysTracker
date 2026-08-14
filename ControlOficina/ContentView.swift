import SwiftUI

struct ContentView: View {
    @StateObject private var attendanceManager = AttendanceManager()
    @State private var showingSettings = false
    @State private var showingRecordsEditor = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Image(systemName: "building.2.fill")
                    .font(.body)
                    .foregroundColor(.blue)
                Text("Office Days Tracker")
                    .font(.subheadline)
                    .fontWeight(.medium)
                Spacer()
                
                // Indicador de conexión
                Circle()
                    .fill(attendanceManager.isConnectedToOffice ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color(NSColor.controlBackgroundColor))
            
            Divider()
            
            VStack(spacing: 0) {
                VStack(spacing: 10) {
                    // Estado actual
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Estado actual")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(attendanceManager.isConnectedToOffice ? "En la oficina" : "Fuera de la oficina")
                                .font(.title3)
                                .fontWeight(.medium)
                        }
                        Spacer()
                        Image(systemName: attendanceManager.isConnectedToOffice ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .font(.largeTitle)
                            .foregroundColor(attendanceManager.isConnectedToOffice ? .green : .red)
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                    
                    // Registro de hoy
                    HStack {
                        Image(systemName: attendanceManager.todayRegistered ? "checkmark.seal.fill" : "seal")
                            .foregroundColor(attendanceManager.todayRegistered ? .green : .gray)
                            .font(.title2)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Hoy")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(attendanceManager.todayRegistered ? "Registrado ✓" : "Sin registrar")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        Spacer()
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                    
                    // Meta mensual
                    VStack(spacing: 8) {
                        HStack {
                            Image(systemName: "calendar")
                                .foregroundColor(.blue)
                            Text(currentMonthName())
                                .font(.subheadline)
                                .fontWeight(.medium)
                            Spacer()
                            Text("\(attendanceManager.daysThisMonth) / \(attendanceManager.monthlyGoal) días")
                                .font(.subheadline)
                                .fontWeight(.bold)
                                .foregroundColor(attendanceManager.goalReached ? .green : .primary)
                        }
                        
                        // Barra de progreso
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Color.gray.opacity(0.3))
                                    .frame(height: 8)
                                
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(attendanceManager.goalReached ? Color.green : Color.blue)
                                    .frame(width: geometry.size.width * attendanceManager.progressPercentage, height: 8)
                            }
                        }
                        .frame(height: 8)
                        
                        // Estado de la meta
                        HStack {
                            if attendanceManager.goalReached {
                                Label("¡Meta cumplida!", systemImage: "star.fill")
                                    .font(.caption)
                                    .foregroundColor(.green)
                            } else {
                                Text("Faltan \(attendanceManager.daysRemaining) días para la meta")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                        }
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                    
                    // Días hábiles restantes
                    HStack {
                        Image(systemName: "calendar.badge.clock")
                            .foregroundColor(.orange)
                            .font(.title2)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Días hábiles restantes")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("\(attendanceManager.workdaysRemaining) días")
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        Spacer()
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                    
                    // Lista de días registrados este mes
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Días registrados")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Spacer()
                            Button {
                                showingRecordsEditor = true
                            } label: {
                                Label("Editar", systemImage: "pencil")
                                    .font(.caption)
                            }
                            .buttonStyle(.plain)
                        }
                        
                        let records = attendanceManager.getRecordsForCurrentMonth()
                        if records.isEmpty {
                            Text("No hay registros este mes")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .italic()
                        } else {
                            LazyVGrid(columns: [
                                GridItem(.flexible()),
                                GridItem(.flexible()),
                                GridItem(.flexible()),
                                GridItem(.flexible())
                            ], spacing: 8) {
                                ForEach(records) { record in
                                    Text(formatDay(record.date))
                                        .font(.caption)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Color.blue.opacity(0.2))
                                        .cornerRadius(4)
                                }
                            }
                        }
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
            }
            
            Divider()
            
            // Footer
            VStack(spacing: 4) {
                // Auto-inicio
                HStack {
                    Toggle(isOn: $attendanceManager.launchAtLogin) {
                        Text("Iniciar sesión en el Mac")
                            .font(.caption)
                    }
                    .toggleStyle(.checkbox)
                    Spacer()
                }
                
                HStack {
                    // Botón de configuración
                    Button(action: {
                        showingSettings = true
                    }) {
                        Label("Configuración", systemImage: "gearshape")
                            .font(.caption2)
                    }
                    .buttonStyle(.plain)
                    
                    // Botón para forzar verificación
                    Button(action: {
                        attendanceManager.checkGateway()
                        attendanceManager.loadMonthData()
                    }) {
                        Label("Actualizar", systemImage: "arrow.clockwise")
                            .font(.caption2)
                    }
                    .buttonStyle(.plain)
                    
                    Spacer()
                    
                    Button(action: {
                        NSApplication.shared.terminate(nil)
                    }) {
                        Label("Salir", systemImage: "power")
                            .font(.caption2)
                            .foregroundColor(.red)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
        }
        .frame(width: 340)
        .onAppear {
            // Actualizar datos cuando se abre la vista
            attendanceManager.refreshData()
        }
        .sheet(isPresented: $showingSettings) {
            SettingsView(attendanceManager: attendanceManager)
        }
        .sheet(isPresented: $showingRecordsEditor) {
            RecordsEditorView(attendanceManager: attendanceManager)
        }
    }
    
    private func currentMonthName() -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "es_ES")
        formatter.dateFormat = "MMMM yyyy"
        return formatter.string(from: Date()).capitalized
    }
    
    private func formatDay(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "es_ES")
        formatter.dateFormat = "d MMM"
        return formatter.string(from: date)
    }
}

#Preview {
    ContentView()
}
