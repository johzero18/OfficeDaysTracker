from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QComboBox, QFrame, QMessageBox, QWidget,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.network import get_default_gateway, validate_ip
import i18n


def _spin_stylesheet() -> str:
    return """
        QSpinBox {
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 13px;
        }
        QSpinBox::up-button {
            width: 18px;
            subcontrol-origin: border;
            subcontrol-position: top right;
        }
        QSpinBox::down-button {
            width: 18px;
            subcontrol-origin: border;
            subcontrol-position: bottom right;
        }
        QSpinBox::up-arrow {
            width: 8px;
            height: 8px;
        }
        QSpinBox::down-arrow {
            width: 8px;
            height: 8px;
        }
    """


class SettingsDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle(i18n.t("settings"))
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumSize(520, 420)
        self.resize(540, 620)
        self.setModal(True)

        self._gateway_input = QLineEdit()
        self._interval_spin = QSpinBox()
        self._goal_spin = QSpinBox()
        self._lang_combo = QComboBox()
        self._current_gw_label = QLabel("")

        self._build_ui()
        self._load_current()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 13px;
                background: #fff;
            }
            #section {
                background: #f7f7f7;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            #sectionTitle {
                font-size: 14px;
                font-weight: 600;
            }
            #desc {
                font-size: 11px;
                color: #888;
            }
            #smallNote {
                font-size: 11px;
                color: #666;
            }
            #btnPreset {
                font-size: 11px;
                padding: 3px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
            }
            #btnPreset:hover {
                background: #e0e0ff;
            }
            #btnDetect {
                font-size: 11px;
                padding: 4px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
            }
            #btnDetect:hover {
                background: #e8e8e8;
            }
            #footer {
                border-top: 1px solid #d0d0d0;
                padding: 12px;
                background: #f0f0f0;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        hdr = QFrame()
        hdr.setStyleSheet("background: #f0f0f0; border-bottom: 1px solid #d0d0d0;")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(16, 12, 16, 12)
        icon_lbl = QLabel("\u2699")
        icon_lbl.setFont(QFont("", 20))
        h.addWidget(icon_lbl)
        title = QLabel(i18n.t("settings"))
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        h.addWidget(title)
        h.addStretch()

        help_btn = QPushButton("?")
        help_btn.setStyleSheet(
            "border: none; background: transparent; font-size: 16px; color: #555; padding: 0 6px;"
        )
        help_btn.setToolTip(i18n.t("help"))
        help_btn.clicked.connect(self._on_help)
        h.addWidget(help_btn)

        root.addWidget(hdr)

        # ── Body (scrollable) ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #fff; border: none; }")

        container = QWidget()
        body = QVBoxLayout(container)
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(16)

        # Gateway section
        gw_frame = QFrame()
        gw_frame.setObjectName("section")
        gw_lay = QVBoxLayout(gw_frame)
        gw_lay.setContentsMargins(12, 12, 12, 12)
        gw_lay.setSpacing(6)

        gw_title = QLabel(f"\U0001F310 {i18n.t('gateway_section')}")
        gw_title.setObjectName("sectionTitle")
        gw_lay.addWidget(gw_title)

        gw_desc = QLabel(i18n.t("gateway_desc"))
        gw_desc.setObjectName("desc")
        gw_lay.addWidget(gw_desc)

        gw_row = QHBoxLayout()
        self._gateway_input.setPlaceholderText(i18n.t("gateway_placeholder"))
        self._gateway_input.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; padding: 4px 8px;"
            " border: 1px solid #ccc; border-radius: 4px; font-size: 13px;"
        )
        gw_row.addWidget(self._gateway_input)

        detect_btn = QPushButton(f"\U0001F50D {i18n.t('detect')}")
        detect_btn.setObjectName("btnDetect")
        detect_btn.clicked.connect(self._detect_current)
        gw_row.addWidget(detect_btn)
        gw_lay.addLayout(gw_row)

        self._current_gw_label.setObjectName("smallNote")
        gw_lay.addWidget(self._current_gw_label)

        body.addWidget(gw_frame)

        # Interval section
        iv_frame = QFrame()
        iv_frame.setObjectName("section")
        iv_lay = QVBoxLayout(iv_frame)
        iv_lay.setContentsMargins(12, 12, 12, 12)
        iv_lay.setSpacing(6)

        iv_title = QLabel(f"\u23F0 {i18n.t('interval_section')}")
        iv_title.setObjectName("sectionTitle")
        iv_lay.addWidget(iv_title)

        iv_desc = QLabel(i18n.t("interval_desc"))
        iv_desc.setObjectName("desc")
        iv_lay.addWidget(iv_desc)

        iv_row = QHBoxLayout()
        self._interval_spin.setMinimum(1)
        self._interval_spin.setMaximum(1440)
        self._interval_spin.setMinimumWidth(130)
        self._interval_spin.setStyleSheet(_spin_stylesheet())
        iv_row.addWidget(self._interval_spin)
        iv_row.addWidget(QLabel(i18n.t("minutes")))
        iv_row.addStretch()
        iv_lay.addLayout(iv_row)

        presets = QHBoxLayout()
        presets.setSpacing(6)
        presets.addWidget(QLabel(f"{i18n.t('quick')}"))
        presets.addWidget(self._preset_btn(5))
        presets.addWidget(self._preset_btn(15))
        presets.addWidget(self._preset_btn(30))
        presets.addWidget(self._preset_btn(60))
        presets.addStretch()
        iv_lay.addLayout(presets)

        note = QLabel(f"\u2139 {i18n.t('interval_note')}")
        note.setObjectName("smallNote")
        note.setStyleSheet("font-size: 11px; color: #3b82f6;")
        iv_lay.addWidget(note)

        body.addWidget(iv_frame)

        # Meta mensual section
        gl_frame = QFrame()
        gl_frame.setObjectName("section")
        gl_lay = QVBoxLayout(gl_frame)
        gl_lay.setContentsMargins(12, 12, 12, 12)
        gl_lay.setSpacing(6)

        gl_title = QLabel(f"\U0001F3C6 {i18n.t('goal_section')}")
        gl_title.setObjectName("sectionTitle")
        gl_lay.addWidget(gl_title)

        gl_desc = QLabel(i18n.t("goal_desc"))
        gl_desc.setObjectName("desc")
        gl_lay.addWidget(gl_desc)

        gl_row = QHBoxLayout()
        self._goal_spin.setMinimum(1)
        self._goal_spin.setMaximum(31)
        self._goal_spin.setMinimumWidth(130)
        self._goal_spin.setStyleSheet(_spin_stylesheet())
        gl_row.addWidget(self._goal_spin)
        gl_row.addWidget(QLabel(i18n.t("days")))
        gl_row.addStretch()
        gl_lay.addLayout(gl_row)

        body.addWidget(gl_frame)

        # Idioma / Language section
        lg_frame = QFrame()
        lg_frame.setObjectName("section")
        lg_lay = QVBoxLayout(lg_frame)
        lg_lay.setContentsMargins(12, 12, 12, 12)
        lg_lay.setSpacing(6)

        lg_title = QLabel(f"\U0001F1FA\U0001F1F8/\U0001F1EA\U0001F1F8 {i18n.t('language_section')}")
        lg_title.setObjectName("sectionTitle")
        lg_lay.addWidget(lg_title)

        lg_desc = QLabel(i18n.t("language_desc"))
        lg_desc.setObjectName("desc")
        lg_lay.addWidget(lg_desc)

        lg_row = QHBoxLayout()
        self._lang_combo.addItem("Español", "es")
        self._lang_combo.addItem("English", "en")
        self._lang_combo.setMinimumWidth(160)
        self._lang_combo.setStyleSheet(
            "padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;"
        )
        lg_row.addWidget(self._lang_combo)
        lg_row.addStretch()
        lg_lay.addLayout(lg_row)

        body.addWidget(lg_frame)
        body.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # ── Footer ──
        ftr = QFrame()
        ftr.setObjectName("footer")
        f = QHBoxLayout(ftr)
        f.setContentsMargins(16, 8, 16, 8)

        cancel_btn = QPushButton(i18n.t("cancel"))
        cancel_btn.setStyleSheet(
            "padding: 6px 20px; border: 1px solid #ccc; border-radius: 4px; background: #fff;"
        )
        cancel_btn.clicked.connect(self.reject)
        f.addWidget(cancel_btn)

        f.addStretch()

        save_btn = QPushButton(i18n.t("save"))
        save_btn.setStyleSheet(
            "padding: 6px 20px; border: none; border-radius: 4px;"
            " background: #3b82f6; color: #fff; font-weight: 600;"
        )
        save_btn.clicked.connect(self._on_save)
        f.addWidget(save_btn)

        root.addWidget(ftr)

    def _on_help(self):
        from .info_dialog import InfoDialog
        InfoDialog(self).exec()

    def _preset_btn(self, minutes: int) -> QPushButton:
        label = f"{minutes} min" if minutes < 60 else f"{minutes // 60} h"
        btn = QPushButton(label)
        btn.setObjectName("btnPreset")
        btn.clicked.connect(lambda: self._interval_spin.setValue(minutes))
        return btn

    def _load_current(self):
        self._gateway_input.setText(self._manager.office_gateway)
        self._interval_spin.setValue(self._manager.check_interval // 60)
        self._goal_spin.setValue(self._manager.monthly_goal)
        idx = self._lang_combo.findData(self._manager.language)
        self._lang_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._update_current_gateway()

    def _update_current_gateway(self):
        gw = self._manager.current_gateway
        if gw:
            self._current_gw_label.setText(i18n.t("current_gateway", gw=gw))
        else:
            self._current_gw_label.setText(i18n.t("current_gateway_none"))

    def _detect_current(self):
        gw = get_default_gateway()
        if gw:
            self._gateway_input.setText(gw)
            self._current_gw_label.setText(i18n.t("current_gateway", gw=gw))
        else:
            QMessageBox.warning(self, i18n.t("error"), i18n.t("detect_failed"))

    def _on_save(self):
        gw = self._gateway_input.text().strip()
        if not validate_ip(gw):
            QMessageBox.warning(self, i18n.t("error"), i18n.t("invalid_ip"))
            return

        self._manager.office_gateway = gw
        self._manager.check_interval = self._interval_spin.value() * 60
        self._manager.monthly_goal = self._goal_spin.value()
        self._manager.language = self._lang_combo.currentData()
        self.accept()
