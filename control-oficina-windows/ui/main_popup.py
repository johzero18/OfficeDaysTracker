from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGridLayout, QFrame, QCheckBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor, QPen

from datetime import datetime

from attendance_manager import MONTHLY_GOAL

MONTH_NAMES_ES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _make_section(title="") -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("section")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(6)
    if title:
        lbl = QLabel(title)
        lbl.setObjectName("sectionTitle")
        layout.addWidget(lbl)
    return frame, layout


class MainPopup(QWidget):
    def __init__(self, manager):
        super().__init__()
        self._manager = manager
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedWidth(350)

        self._build_ui()
        self._connect_signals()
        self._refresh()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 13px;
            }
            #header {
                background: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            #header QLabel {
                font-size: 13px;
            }
            #section {
                background: #f7f7f7;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 0px 12px;
            }
            #sectionTitle {
                font-size: 11px;
                color: #888;
                font-weight: 600;
                text-transform: uppercase;
            }
            #bigText {
                font-size: 18px;
                font-weight: 600;
            }
            #subText {
                font-size: 13px;
                font-weight: 500;
            }
            #smallText {
                font-size: 11px;
                color: #888;
            }
            #footer {
                border-top: 1px solid #d0d0d0;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
                background: #f0f0f0;
                padding: 6px;
            }
            #dayTag {
                background: #d0e0ff;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
            }
            #progressBar {
                border: none;
                background: #ddd;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            #progressBar::chunk {
                border-radius: 4px;
            }
            #btn {
                font-size: 11px;
                padding: 4px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
            }
            #btn:hover {
                background: #e8e8e8;
            }
            #btnQuit {
                font-size: 11px;
                padding: 4px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
                color: #c00;
            }
            #btnQuit:hover {
                background: #ffe0e0;
            }
            QCheckBox {
                font-size: 11px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # ── Header ──
        header = QFrame()
        header.setObjectName("header")
        hdr = QHBoxLayout(header)
        hdr.setContentsMargins(14, 8, 14, 8)

        self._icon_label = QLabel("\U0001F3E2")
        self._icon_label.setFont(QFont("Segoe UI Emoji", 14))
        hdr.addWidget(self._icon_label)

        self._title_label = QLabel("Office Days Tracker")
        self._title_label.setStyleSheet("font-weight: 600;")
        hdr.addWidget(self._title_label)

        hdr.addStretch()

        self._status_dot = QLabel("\u25CF")
        self._status_dot.setStyleSheet("color: #ccc; font-size: 16px;")
        hdr.addWidget(self._status_dot)

        root.addWidget(header)

        # ── Estado actual ──
        sec, lay = _make_section()
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(2)
        lbl = QLabel("Estado actual")
        lbl.setObjectName("smallText")
        left.addWidget(lbl)
        self._status_text = QLabel("—")
        self._status_text.setObjectName("bigText")
        left.addWidget(self._status_text)
        row.addLayout(left)
        row.addStretch()
        self._status_icon = QLabel("")
        self._status_icon.setFont(QFont("Segoe UI Emoji", 26))
        row.addWidget(self._status_icon)
        lay.addLayout(row)
        root.addWidget(sec)

        # ── Hoy ──
        sec, lay = _make_section()
        row = QHBoxLayout()
        self._today_icon = QLabel("")
        self._today_icon.setFont(QFont("Segoe UI Emoji", 18))
        row.addWidget(self._today_icon)
        left = QVBoxLayout()
        left.setSpacing(0)
        lbl = QLabel("Hoy")
        lbl.setObjectName("smallText")
        left.addWidget(lbl)
        self._today_text = QLabel("—")
        self._today_text.setObjectName("subText")
        left.addWidget(self._today_text)
        row.addLayout(left)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(sec)

        # ── Meta mensual ──
        sec, lay = _make_section()
        row = QHBoxLayout()
        cal_icon = QLabel("\U0001F4C5")
        cal_icon.setFont(QFont("Segoe UI Emoji", 14))
        row.addWidget(cal_icon)
        self._month_label = QLabel("")
        self._month_label.setObjectName("subText")
        row.addWidget(self._month_label)
        row.addStretch()
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("font-weight: 700; font-size: 13px;")
        row.addWidget(self._count_label)
        lay.addLayout(row)

        self._progress = QProgressBar()
        self._progress.setObjectName("progressBar")
        self._progress.setRange(0, 100)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(8)
        lay.addWidget(self._progress)

        self._goal_label = QLabel("")
        self._goal_label.setObjectName("smallText")
        lay.addWidget(self._goal_label)
        root.addWidget(sec)

        # ── Días hábiles restantes ──
        sec, lay = _make_section()
        row = QHBoxLayout()
        clock_icon = QLabel("\u23F0")
        clock_icon.setFont(QFont("Segoe UI Emoji", 16))
        row.addWidget(clock_icon)
        left = QVBoxLayout()
        left.setSpacing(0)
        lbl = QLabel("Días hábiles restantes")
        lbl.setObjectName("smallText")
        left.addWidget(lbl)
        self._workdays_label = QLabel("—")
        self._workdays_label.setObjectName("subText")
        left.addWidget(self._workdays_label)
        row.addLayout(left)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(sec)

        # ── Días registrados ──
        sec, lay = _make_section()
        lbl = QLabel("Días registrados")
        lbl.setObjectName("sectionTitle")
        lay.addWidget(lbl)
        self._days_grid = QGridLayout()
        self._days_grid.setSpacing(6)
        lay.addLayout(self._days_grid)
        root.addWidget(sec)

        # ── Spacer ──
        root.addStretch()

        # ── Footer ──
        footer = QFrame()
        footer.setObjectName("footer")
        ftr = QVBoxLayout(footer)
        ftr.setContentsMargins(12, 6, 12, 6)
        ftr.setSpacing(6)

        self._autostart_cb = QCheckBox("Iniciar al encender la PC")
        ftr.addWidget(self._autostart_cb)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        settings_btn = QPushButton("\u2699 Configuración")
        settings_btn.setObjectName("btn")
        settings_btn.clicked.connect(self._on_settings)
        btn_row.addWidget(settings_btn)

        refresh_btn = QPushButton("\u21BB Actualizar")
        refresh_btn.setObjectName("btn")
        refresh_btn.clicked.connect(self._on_refresh)
        btn_row.addWidget(refresh_btn)

        btn_row.addStretch()

        quit_btn = QPushButton("\u23FB Salir")
        quit_btn.setObjectName("btnQuit")
        quit_btn.clicked.connect(self._on_quit)
        btn_row.addWidget(quit_btn)

        ftr.addLayout(btn_row)
        root.addWidget(footer)

        # ── Bordes redondeados ──
        self.setStyleSheet(self.styleSheet() + """
            MainPopup {
                border: 1px solid #bbb;
                border-radius: 8px;
                background: #fff;
            }
        """)

    def _connect_signals(self):
        self._manager.state_changed.connect(self._refresh)
        self._autostart_cb.stateChanged.connect(self._on_autostart_toggle)

    def _refresh(self):
        m = self._manager

        self._status_dot.setStyleSheet(
            f"color: {'#2e7d32' if m.is_connected else '#c62828'}; font-size: 16px;"
        )
        self._status_text.setText(
            "En la oficina \U0001F3E2" if m.is_connected else "Fuera de la oficina \U0001F3E0"
        )
        self._status_text.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {'#2e7d32' if m.is_connected else '#555'};"
        )
        self._status_icon.setText("\u2705" if m.is_connected else "\u274C")

        if m.today_registered:
            self._today_icon.setText("\U0001F511")
            self._today_text.setText("Registrado \u2713")
            self._today_text.setStyleSheet("font-size: 13px; font-weight: 500; color: #2e7d32;")
        else:
            self._today_icon.setText("\U0001F512")
            self._today_text.setText("Sin registrar")
            self._today_text.setStyleSheet("font-size: 13px; font-weight: 500; color: #888;")

        now = datetime.now()
        month_name = MONTH_NAMES_ES[now.month]
        self._month_label.setText(f"{month_name} {now.year}".capitalize())

        count = m.days_this_month
        total = MONTHLY_GOAL
        color = "#2e7d32" if m.goal_reached else "#000"
        self._count_label.setText(f"{count} / {total} días")
        self._count_label.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {color};")

        self._progress.setValue(int(m.progress_percentage * 100))
        chunk_color = "#2e7d32" if m.goal_reached else "#3b82f6"
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                border: none; background: #ddd; border-radius: 4px; height: 8px;
            }}
            QProgressBar::chunk {{
                background: {chunk_color}; border-radius: 4px;
            }}
        """)

        if m.goal_reached:
            self._goal_label.setText("\u2B50 \u00A1Meta cumplida!")
            self._goal_label.setStyleSheet("font-size: 11px; color: #2e7d32;")
        else:
            self._goal_label.setText(f"Faltan {m.days_remaining} días para la meta")
            self._goal_label.setStyleSheet("font-size: 11px; color: #888;")

        self._workdays_label.setText(f"{m.workdays_remaining} días")

        self._refresh_days_grid()
        self._autostart_cb.setChecked(m.launch_at_login)

    def _refresh_days_grid(self):
        while self._days_grid.count():
            item = self._days_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = self._manager.get_records_for_current_month()
        if not records:
            lbl = QLabel("No hay registros este mes")
            lbl.setObjectName("smallText")
            lbl.setStyleSheet("font-style: italic;")
            self._days_grid.addWidget(lbl, 0, 0)
            return

        for i, rec in enumerate(records):
            dt = datetime.fromisoformat(rec["date"])
            day_text = dt.strftime("%d %b")
            lbl = QLabel(day_text)
            lbl.setObjectName("dayTag")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                "background: #d0e0ff; border-radius: 4px; padding: 3px 8px; font-size: 11px;"
            )
            self._days_grid.addWidget(lbl, i // 4, i % 4)

    def _on_settings(self):
        from .settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._manager, self)
        if dlg.exec():
            self._manager.state_changed.emit()

    def _on_refresh(self):
        self._manager.refresh()

    def _on_quit(self):
        self.close()
        from PySide6.QtWidgets import QApplication
        QApplication.instance().quit()

    def _on_autostart_toggle(self, state):
        self._manager.launch_at_login = bool(state)

    def show_near_tray(self):
        self._refresh()
        screen = self.screen().availableGeometry()
        x = screen.right() - self.width() - 20
        y = screen.bottom() - self.height() - 10
        self.move(x, y)
        self.show()
        self.activateWindow()
        self.raise_()

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint()
        self._dragging = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)
