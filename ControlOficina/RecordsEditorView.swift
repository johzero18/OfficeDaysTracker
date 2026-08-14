import SwiftUI

struct RecordsEditorView: View {
    @ObservedObject var attendanceManager: AttendanceManager
    @Environment(\.dismiss) private var dismiss
    @State private var selectedDate = Date()

    private var currentMonthRange: ClosedRange<Date> {
        let calendar = Calendar.current
        let monthStart = calendar.dateInterval(of: .month, for: Date())?.start ?? Date()
        return monthStart...Date()
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Label("Editar días", systemImage: "calendar.badge.checkmark")
                    .font(.headline)
                Spacer()
                Button("Cerrar") {
                    dismiss()
                }
                .keyboardShortcut(.cancelAction)
            }
            .padding()

            Divider()

            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    DatePicker(
                        "Fecha",
                        selection: $selectedDate,
                        in: currentMonthRange,
                        displayedComponents: .date
                    )

                    Spacer()

                    let isRegistered = attendanceManager.isRegistered(on: selectedDate)
                    Button {
                        attendanceManager.setAttendance(on: selectedDate, attended: !isRegistered)
                    } label: {
                        Label(
                            isRegistered ? "Quitar" : "Añadir",
                            systemImage: isRegistered ? "minus.circle" : "plus.circle"
                        )
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(isRegistered ? .red : .blue)
                }

                Text("Días registrados este mes")
                    .font(.subheadline)
                    .fontWeight(.medium)

                let records = attendanceManager.getRecordsForCurrentMonth()
                if records.isEmpty {
                    VStack(spacing: 8) {
                        Image(systemName: "calendar")
                            .font(.largeTitle)
                            .foregroundColor(.secondary)
                        Text("Sin registros")
                            .font(.headline)
                        Text("Selecciona una fecha para añadirla.")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(records) { record in
                        HStack {
                            Text(record.date, format: .dateTime.weekday(.wide).day().month(.wide))
                            Spacer()
                            Button {
                                attendanceManager.setAttendance(on: record.date, attended: false)
                            } label: {
                                Image(systemName: "trash")
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(.red)
                            .help("Quitar día")
                        }
                    }
                    .listStyle(.inset)
                }
            }
            .padding()
        }
        .frame(width: 430, height: 400)
    }
}

#Preview {
    RecordsEditorView(attendanceManager: AttendanceManager())
}