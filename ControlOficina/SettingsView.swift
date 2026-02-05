import SwiftUI

struct SettingsView: View {
    @ObservedObject var attendanceManager: AttendanceManager
    @Environment(\.dismiss) var dismiss
    
    @State private var gatewayInput: String = ""
    @State private var intervalMinutes: Int = 60
    @State private var showError: Bool = false
    @State private var errorMessage: String = ""
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Image(systemName: "gearshape.fill")
                    .font(.title2)
                    .foregroundColor(.blue)
                Text("Configuración")
                    .font(.title3)
                    .fontWeight(.semibold)
                Spacer()
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            
            Divider()
            
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Gateway de la oficina
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Gateway de la oficina", systemImage: "network")
                            .font(.headline)
                        
                        Text("Dirección IP del gateway de tu red de oficina")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack {
                            TextField("Ej: 10.15.16.1", text: $gatewayInput)
                                .textFieldStyle(.roundedBorder)
                                .font(.system(.body, design: .monospaced))
                            
                            Button(action: detectCurrentGateway) {
                                Label("Detectar", systemImage: "magnifyingglass")
                                    .font(.caption)
                            }
                            .buttonStyle(.bordered)
                        }
                        
                        if let current = attendanceManager.currentGateway {
                            Text("Gateway actual: \(current)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                    
                    // Intervalo de chequeo
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Intervalo de chequeo", systemImage: "clock")
                            .font(.headline)
                        
                        Text("Cada cuánto tiempo verificar la conexión a la oficina")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack {
                            Stepper(value: $intervalMinutes, in: 1...1440, step: 1) {
                                HStack {
                                    TextField("", value: $intervalMinutes, format: .number)
                                        .textFieldStyle(.roundedBorder)
                                        .frame(width: 60)
                                        .multilineTextAlignment(.trailing)
                                    
                                    Text("minutos")
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        
                        // Presets rápidos
                        HStack(spacing: 8) {
                            Text("Rápido:")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            ForEach([5, 15, 30, 60], id: \.self) { minutes in
                                Button(action: { intervalMinutes = minutes }) {
                                    Text(formatInterval(minutes))
                                        .font(.caption2)
                                }
                                .buttonStyle(.bordered)
                                .controlSize(.small)
                            }
                        }
                        
                        HStack {
                            Image(systemName: "info.circle")
                                .foregroundColor(.blue)
                                .font(.caption)
                            Text("Intervalos muy cortos (< 5 min) pueden consumir más batería")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(Color(NSColor.controlBackgroundColor).opacity(0.5))
                    .cornerRadius(8)
                }
                .padding()
            }
            
            Divider()
            
            // Footer con botones
            HStack {
                Button("Cancelar") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
                
                Spacer()
                
                Button("Guardar") {
                    saveSettings()
                }
                .keyboardShortcut(.defaultAction)
                .buttonStyle(.borderedProminent)
            }
            .padding()
        }
        .frame(width: 500, height: 450)
        .onAppear {
            gatewayInput = attendanceManager.officeGateway
            intervalMinutes = attendanceManager.checkInterval / 60
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }
    
    private func formatInterval(_ minutes: Int) -> String {
        if minutes < 60 {
            return "\(minutes) min"
        } else {
            let hours = minutes / 60
            return "\(hours) h"
        }
    }
    
    private func detectCurrentGateway() {
        if let current = attendanceManager.currentGateway {
            gatewayInput = current
        } else {
            errorMessage = "No se pudo detectar el gateway actual"
            showError = true
        }
    }
    
    private func saveSettings() {
        // Validar gateway
        let trimmedGateway = gatewayInput.trimmingCharacters(in: .whitespaces)
        
        if !attendanceManager.validateGateway(trimmedGateway) {
            errorMessage = "La dirección IP del gateway no es válida.\nFormato: xxx.xxx.xxx.xxx"
            showError = true
            return
        }
        
        // Guardar configuraciones
        attendanceManager.officeGateway = trimmedGateway
        attendanceManager.checkInterval = max(60, intervalMinutes * 60) // Mínimo 1 minuto
        
        dismiss()
    }
}

#Preview {
    SettingsView(attendanceManager: AttendanceManager())
}
