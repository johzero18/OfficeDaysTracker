from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGridLayout, QFrame, QCheckBox, QSizePolicy,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor, QPen

from datetime import datetime, date

import i18n


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
    def __init__(self, manager, on_settings_saved=None):
        super().__init__()
        self._manager = manager
        self._on_settings_saved = on_settings_saved
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedWidth(350)
        QApplication.instance().installEventFilter(self)

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
            #btnManual {
                font-size: 11px;
                padding: 4px 10px;
                border: 1px solid #2e7d32;
                border-radius: 4px;
                background: #e8f5e9;
                color: #2e7d32;
            }
            #btnManual:hover {
                background: #c8e6c9;
            }
            #btnManual:disabled {
                background: #f0f0f0;
                border-color: #ccc;
                color: #999;
            }
            #headerBtn {
                border: none;
                background: transparent;
                font-size: 12px;
                color: #555;
                padding: 2px 6px;
                border-radius: 3px;
            }
            #headerBtn:hover {
                background: #ddd;
                color: #000;
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

        hdr.addSpacing(6)

        self._help_btn = QPushButton("?")
        self._help_btn.setObjectName("headerBtn")
        self._help_btn.clicked.connect(self._on_help)
        hdr.addWidget(self._help_btn)

        self._min_btn = QPushButton("\u2013")
        self._min_btn.setObjectName("headerBtn")
        self._min_btn.clicked.connect(self.hide)
        hdr.addWidget(self._min_btn)

        self._close_btn = QPushButton("\u2715")
        self._close_btn.setObjectName("headerBtn")
        self._close_btn.clicked.connect(self.close)
        hdr.addWidget(self._close_btn)

        root.addWidget(header)

        # ── Estado actual ──
        sec, lay = _make_section()
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(2)
        self._status_title = QLabel("")
        self._status_title.setObjectName("smallText")
        left.addWidget(self._status_title)
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
        self._today_title = QLabel("")
        self._today_title.setObjectName("smallText")
        left.addWidget(self._today_title)
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
        self._workdays_title = QLabel("")
        self._workdays_title.setObjectName("smallText")
        left.addWidget(self._workdays_title)
        self._workdays_label = QLabel("—")
        self._workdays_label.setObjectName("subText")
        left.addWidget(self._workdays_label)
        row.addLayout(left)
        row.addStretch()
        lay.addLayout(row)
        root.addWidget(sec)

        # ── Días registrados ──
        sec, lay = _make_section()
        self._days_title = QLabel("")
        self._days_title.setObjectName("sectionTitle")
        lay.addWidget(self._days_title)
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

        self._autostart_cb = QCheckBox("")
        ftr.addWidget(self._autostart_cb)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._settings_btn = QPushButton("")
        self._settings_btn.setObjectName("btn")
        self._settings_btn.clicked.connect(self._on_settings)
        btn_row.addWidget(self._settings_btn)

        self._records_btn = QPushButton("")
        self._records_btn.setObjectName("btn")
        self._records_btn.clicked.connect(self._on_records)
        btn_row.addWidget(self._records_btn)

        btn_row.addStretch()

        self._refresh_btn = QPushButton("")
        self._refresh_btn.setObjectName("btn")
        self._refresh_btn.clicked.connect(self._on_refresh)
        btn_row.addWidget(self._refresh_btn)

        ftr.addLayout(btn_row)

        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(6)

        self._manual_btn = QPushButton("")
        self._manual_btn.setObjectName("btnManual")
        self._manual_btn.clicked.connect(self._on_manual_today)
        btn_row2.addWidget(self._manual_btn)

        btn_row2.addStretch()

        self._quit_btn = QPushButton("")
        self._quit_btn.setObjectName("btnQuit")
        self._quit_btn.clicked.connect(self._on_quit)
        btn_row2.addWidget(self._quit_btn)

        ftr.addLayout(btn_row2)
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
        self._apply_language()

        self._status_dot.setStyleSheet(
            f"color: {'#2e7d32' if m.is_connected else '#c62828'}; font-size: 16px;"
        )
        self._status_text.setText(
            f"{i18n.t('status_office')} \U0001F3E2" if m.is_connected else f"{i18n.t('status_away')} \U0001F3E0"
        )
        self._status_text.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {'#2e7d32' if m.is_connected else '#555'};"
        )
        self._status_icon.setText("\u2705" if m.is_connected else "\u274C")

        if m.today_registered:
            self._today_icon.setText("\U0001F511")
            self._today_text.setText(f"{i18n.t('registered')} \u2713")
            self._today_text.setStyleSheet("font-size: 13px; font-weight: 500; color: #2e7d32;")
        else:
            self._today_icon.setText("\U0001F512")
            self._today_text.setText(i18n.t("not_registered"))
            self._today_text.setStyleSheet("font-size: 13px; font-weight: 500; color: #888;")

        now = datetime.now()
        self._month_label.setText(f"{i18n.month_name(now.month)} {now.year}".capitalize())

        count = m.days_this_month
        total = m.monthly_goal
        color = "#2e7d32" if m.goal_reached else "#000"
        self._count_label.setText(f"{count} / {total} {i18n.t('days')}")
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
            self._goal_label.setText(f"\u2B50 {i18n.t('goal_reached')}")
            self._goal_label.setStyleSheet("font-size: 11px; color: #2e7d32;")
        else:
            self._goal_label.setText(i18n.t("days_to_goal", n=m.days_remaining))
            self._goal_label.setStyleSheet("font-size: 11px; color: #888;")

        self._workdays_label.setText(f"{m.workdays_remaining} {i18n.t('days')}")

        self._refresh_days_grid()
        self._autostart_cb.setChecked(m.launch_at_login)
        self._manual_btn.setEnabled(not m.today_registered)

    def _apply_language(self):
        self._status_title.setText(i18n.t("status_current"))
        self._today_title.setText(i18n.t("today"))
        self._workdays_title.setText(i18n.t("workdays_remaining"))
        self._days_title.setText(i18n.t("registered_days"))
        self._autostart_cb.setText(i18n.t("autostart"))
        self._settings_btn.setText(f"\u2699 {i18n.t('settings')}")
        self._records_btn.setText(f"\u270E {i18n.t('records')}")
        self._records_btn.setToolTip(i18n.t("records_tooltip"))
        self._refresh_btn.setText(f"\u21BB {i18n.t('refresh')}")
        self._manual_btn.setText(f"\u2705 {i18n.t('register_today')}")
        self._manual_btn.setToolTip(i18n.t("register_today_tooltip"))
        self._quit_btn.setText(f"\u23FB {i18n.t('quit')}")
        self._help_btn.setToolTip(i18n.t("help"))
        self._min_btn.setToolTip(i18n.t("minimize"))
        self._close_btn.setToolTip(i18n.t("close"))

    def _refresh_days_grid(self):
        while self._days_grid.count():
            item = self._days_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        records = self._manager.get_records_for_current_month()
        if not records:
            lbl = QLabel(i18n.t("no_records_month"))
            lbl.setObjectName("smallText")
            lbl.setStyleSheet("font-style: italic;")
            self._days_grid.addWidget(lbl, 0, 0)
            return

        for i, rec in enumerate(records):
            dt = datetime.fromisoformat(rec["date"])
            lbl = QLabel(f"{dt.day} {i18n.month_name(dt.month)[:3]}")
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
            if self._on_settings_saved:
                self._on_settings_saved()

    def _on_records(self):
        from .records_dialog import RecordsDialog
        dlg = RecordsDialog(self._manager, self)
        dlg.exec()

    def _on_manual_today(self):
        self._manager.add_record(date.today())

    def _on_help(self):
        from .info_dialog import InfoDialog
        InfoDialog(self).exec()

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

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if self.isVisible() and event.type() == QEvent.Type.MouseButtonPress:
            pos = event.globalPosition().toPoint()
            if not self.geometry().contains(pos):
                self.close()
        return super().eventFilter(obj, event)

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
