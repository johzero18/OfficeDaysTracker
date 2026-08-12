import sys
import os

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFont, QAction
from PySide6.QtCore import Qt, QTimer

from attendance_manager import AttendanceManager, MONTHLY_GOAL
from ui.main_popup import MainPopup
from ui.settings_dialog import SettingsDialog


def _build_tray_icon() -> QIcon:
    """Dibuja un ícono de edificio simple."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    p.setBrush(QColor("#3b82f6"))
    p.setPen(QPen(QColor("#2563eb"), 1.5))
    p.drawRoundedRect(4, 6, 24, 22, 3, 3)

    p.setBrush(QColor("#fff"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(8, 16, 6, 10)
    p.drawRect(18, 10, 6, 6)

    p.setPen(QPen(QColor("#fff"), 1.5))
    p.drawLine(4, 6, 16, 2)
    p.drawLine(28, 6, 16, 2)

    p.end()
    return QIcon(pixmap)


class App:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setApplicationName("ControlOficina")
        self._app.setQuitOnLastWindowClosed(False)

        self._manager = AttendanceManager()

        self._popup = MainPopup(self._manager)

        self._setup_tray()
        self._setup_timer()

        self._manager.state_changed.connect(self._on_state_changed)
        self._on_state_changed()

    def _setup_tray(self):
        self._tray = QSystemTrayIcon()
        self._tray.setIcon(_build_tray_icon())
        self._tray.setToolTip("Office Days Tracker")

        menu = QMenu()

        show_action = QAction("Mostrar", None)
        show_action.triggered.connect(self._show_popup)
        menu.addAction(show_action)

        settings_action = QAction("\u2699 Configuración", None)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction("\u23FB Salir", None)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._manager.check_gateway)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_popup()

    def _show_popup(self):
        if self._popup.isVisible():
            self._popup.hide()
        else:
            # Restart timer with current interval when showing
            interval_ms = self._manager.check_interval * 1000
            self._timer.start(interval_ms)
            self._popup.show_near_tray()

    def _show_settings(self):
        dlg = SettingsDialog(self._manager, None)
        if dlg.exec():
            self._manager.state_changed.emit()
            interval_ms = self._manager.check_interval * 1000
            self._timer.start(interval_ms)

    def _on_state_changed(self):
        if self._manager.goal_reached and self._manager.today_registered:
            self._tray.showMessage(
                "Office Days Tracker",
                f"\u2B50 ¡Meta cumplida! ({MONTHLY_GOAL} días este mes)",
                QSystemTrayIcon.MessageIcon.Information,
                5000,
            )

    def _quit(self):
        self._popup.close()
        QApplication.instance().quit()

    def run(self):
        sys.exit(self._app.exec())


if __name__ == "__main__":
    app = App()
    app.run()
