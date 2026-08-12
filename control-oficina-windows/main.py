import sys
import os
from datetime import date

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QFont, QAction
from PySide6.QtCore import Qt, QTimer

from attendance_manager import AttendanceManager
import i18n
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

        self._popup = MainPopup(self._manager, on_settings_saved=self._restart_timer)

        self._setup_tray()
        self._setup_timer()

        self._goal_notified_date = None

        self._manager.state_changed.connect(self._on_state_changed)
        self._on_state_changed()

    def _setup_tray(self):
        self._tray = QSystemTrayIcon()
        self._tray.setIcon(_build_tray_icon())
        self._tray.setToolTip("Office Days Tracker")

        menu = QMenu()

        self._show_action = QAction("", None)
        self._show_action.triggered.connect(self._show_popup)
        menu.addAction(self._show_action)

        self._settings_action = QAction("", None)
        self._settings_action.triggered.connect(self._show_settings)
        menu.addAction(self._settings_action)

        self._help_action = QAction("", None)
        self._help_action.triggered.connect(self._show_help)
        menu.addAction(self._help_action)

        menu.addSeparator()

        self._quit_action = QAction("", None)
        self._quit_action.triggered.connect(self._quit)
        menu.addAction(self._quit_action)

        self._apply_language()

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _apply_language(self):
        self._show_action.setText(i18n.t("menu_show"))
        self._settings_action.setText(f"\u2699 {i18n.t('menu_settings')}")
        self._help_action.setText(f"\u2139 {i18n.t('help')}")
        self._quit_action.setText(f"\u23FB {i18n.t('menu_quit')}")

    def _show_help(self):
        from ui.info_dialog import InfoDialog
        InfoDialog(None).exec()

    def _setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._manager.check_gateway)
        self._restart_timer()

    def _restart_timer(self):
        interval_ms = self._manager.check_interval * 1000
        self._timer.start(interval_ms)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_popup()

    def _show_popup(self):
        if self._popup.isVisible():
            self._popup.hide()
        else:
            self._popup.show_near_tray()

    def _show_settings(self):
        dlg = SettingsDialog(self._manager, None)
        if dlg.exec():
            self._manager.state_changed.emit()
            self._restart_timer()

    def _on_state_changed(self):
        if (
            self._manager.goal_reached
            and self._manager.today_registered
            and self._goal_notified_date != date.today()
        ):
            self._goal_notified_date = date.today()
            self._apply_language()
            self._tray.showMessage(
                "Office Days Tracker",
                i18n.t("goal_message", n=self._manager.monthly_goal),
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
