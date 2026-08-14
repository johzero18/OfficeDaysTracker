import SwiftUI

struct SettingsView: View {
    @ObservedObject var attendanceManager: AttendanceManager
    @Environment(\.dismiss) var dismiss
    
    @State private var gatewayInput: String = ""
    @State private var officeGateways: [String] = []
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
                    // Gateways de la oficina
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Redes de oficina", systemImage: "network")
                            .font(.headline)
                        
                        Text("Solo estas redes pueden registrar asistencia automáticamente")
                            .font(.caption)
                            .foregroundColor(.secondary)

                        ForEach(officeGateways, id: \.self) { gateway in
                            HStack {
                                Image(systemName: "building.2")
                                    .foregroundColor(.blue)
                                Text(gateway)
                                    .font(.system(.body, design: .monospaced))
                                Spacer()
                                Button {
                                    officeGateways.removeAll { $0 == gateway }
                                } label: {
                                    Image(systemName: "trash")
                                }
                                .buttonStyle(.plain)
                                .foregroundColor(.red)
                                .help("Eliminar red de oficina")
                            }
                            .padding(.vertical, 3)
                        }
                        
                        HStack {
                            TextField("Ej: 10.15.16.1", text: $gatewayInput)
                                .textFieldStyle(.roundedBorder)
                                .font(.system(.body, design: .monospaced))

                            Button(action: attendanceManager.checkGateway) {
                                Label("Detectar", systemImage: "magnifyingglass")
                                    .font(.caption)
                            }
                            .buttonStyle(.bordered)

                            Button(action: addGateway) {
                                Label("Añadir", systemImage: "plus")
                                    .font(.caption)
                            }
                            .buttonStyle(.bordered)
                        }
                        
                        if let current = attendanceManager.currentGateway {
                            HStack {
                                Text("Gateway actual: \(current)")
                                    .font(.caption2)
                                    .foregroundColor(.secondary)
                                Spacer()
                                if !officeGateways.contains(current) {
                                    Button("Usar actual") {
                                        gatewayInput = current
                                        addGateway()
                                    }
                                    .font(.caption2)
                                    .buttonStyle(.link)
                                }
                            }
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
        .frame(width: 500, height: 520)
        .onAppear {
            officeGateways = attendanceManager.officeGateways
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
    
    private func addGateway() {
        let trimmedGateway = gatewayInput.trimmingCharacters(in: .whitespaces)

        if !attendanceManager.validateGateway(trimmedGateway) {
            errorMessage = "La dirección IP del gateway no es válida.\nFormato: xxx.xxx.xxx.xxx"
            showError = true
            return
        }

        if !officeGateways.contains(trimmedGateway) {
            officeGateways.append(trimmedGateway)
            officeGateways.sort()
        }
        gatewayInput = ""
    }
    
    private func saveSettings() {
        let trimmedGateway = gatewayInput.trimmingCharacters(in: .whitespaces)

        if !trimmedGateway.isEmpty {
            if !attendanceManager.validateGateway(trimmedGateway) {
                errorMessage = "La dirección IP del gateway no es válida.\nFormato: xxx.xxx.xxx.xxx"
                showError = true
                return
            }
            if !officeGateways.contains(trimmedGateway) {
                officeGateways.append(trimmedGateway)
            }
        }
        
        // Guardar configuraciones
        attendanceManager.setOfficeGateways(officeGateways)
        attendanceManager.checkInterval = max(60, intervalMinutes * 60) // Mínimo 1 minuto
        
        dismiss()
    }
}

#Preview {
    SettingsView(attendanceManager: AttendanceManager())
}
