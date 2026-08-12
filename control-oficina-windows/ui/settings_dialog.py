from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFrame, QMessageBox, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.network import get_default_gateway, validate_ip


class SettingsDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle("Configuración")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(480, 420)
        self.setModal(True)

        self._gateway_input = QLineEdit()
        self._interval_spin = QSpinBox()
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
                padding: 12px;
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
        title = QLabel("Configuración")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        h.addWidget(title)
        h.addStretch()
        root.addWidget(hdr)

        # ── Body ──
        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(16)

        # Gateway section
        gw_frame = QFrame()
        gw_frame.setObjectName("section")
        gw_lay = QVBoxLayout(gw_frame)
        gw_lay.setSpacing(6)

        gw_title = QLabel("\U0001F310 Gateway de la oficina")
        gw_title.setObjectName("sectionTitle")
        gw_lay.addWidget(gw_title)

        gw_desc = QLabel("Dirección IP del gateway de tu red de oficina")
        gw_desc.setObjectName("desc")
        gw_lay.addWidget(gw_desc)

        gw_row = QHBoxLayout()
        self._gateway_input.setPlaceholderText("Ej: 10.15.16.1")
        self._gateway_input.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; padding: 4px 8px;"
            " border: 1px solid #ccc; border-radius: 4px; font-size: 13px;"
        )
        gw_row.addWidget(self._gateway_input)

        detect_btn = QPushButton("\U0001F50D Detectar")
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
        iv_lay.setSpacing(6)

        iv_title = QLabel("\u23F0 Intervalo de chequeo")
        iv_title.setObjectName("sectionTitle")
        iv_lay.addWidget(iv_title)

        iv_desc = QLabel("Cada cuánto tiempo verificar la conexión a la oficina")
        iv_desc.setObjectName("desc")
        iv_lay.addWidget(iv_desc)

        iv_row = QHBoxLayout()
        self._interval_spin.setMinimum(1)
        self._interval_spin.setMaximum(1440)
        self._interval_spin.setStyleSheet(
            "padding: 4px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;"
        )
        iv_row.addWidget(self._interval_spin)
        iv_row.addWidget(QLabel("minutos"))
        iv_row.addStretch()
        iv_lay.addLayout(iv_row)

        presets = QHBoxLayout()
        presets.setSpacing(6)
        presets.addWidget(QLabel("Rápido:"))
        presets.addWidget(self._preset_btn(5))
        presets.addWidget(self._preset_btn(15))
        presets.addWidget(self._preset_btn(30))
        presets.addWidget(self._preset_btn(60))
        presets.addStretch()
        iv_lay.addLayout(presets)

        note = QLabel("\u2139 Intervalos muy cortos (< 5 min) pueden consumir más batería")
        note.setObjectName("smallNote")
        note.setStyleSheet("font-size: 11px; color: #3b82f6;")
        iv_lay.addWidget(note)

        body.addWidget(iv_frame)
        body.addStretch()
        root.addLayout(body)

        # ── Footer ──
        ftr = QFrame()
        ftr.setObjectName("footer")
        f = QHBoxLayout(ftr)
        f.setContentsMargins(16, 8, 16, 8)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(
            "padding: 6px 20px; border: 1px solid #ccc; border-radius: 4px; background: #fff;"
        )
        cancel_btn.clicked.connect(self.reject)
        f.addWidget(cancel_btn)

        f.addStretch()

        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet(
            "padding: 6px 20px; border: none; border-radius: 4px;"
            " background: #3b82f6; color: #fff; font-weight: 600;"
        )
        save_btn.clicked.connect(self._on_save)
        f.addWidget(save_btn)

        root.addWidget(ftr)

    def _preset_btn(self, minutes: int) -> QPushButton:
        label = f"{minutes} min" if minutes < 60 else f"{minutes // 60} h"
        btn = QPushButton(label)
        btn.setObjectName("btnPreset")
        btn.clicked.connect(lambda: self._interval_spin.setValue(minutes))
        return btn

    def _load_current(self):
        self._gateway_input.setText(self._manager.office_gateway)
        self._interval_spin.setValue(self._manager.check_interval // 60)
        self._update_current_gateway()

    def _update_current_gateway(self):
        gw = self._manager.current_gateway
        if gw:
            self._current_gw_label.setText(f"Gateway actual: {gw}")
        else:
            self._current_gw_label.setText("Gateway actual: —")

    def _detect_current(self):
        gw = get_default_gateway()
        if gw:
            self._gateway_input.setText(gw)
            self._current_gw_label.setText(f"Gateway actual: {gw}")
        else:
            QMessageBox.warning(self, "Error", "No se pudo detectar el gateway actual")

    def _on_save(self):
        gw = self._gateway_input.text().strip()
        if not validate_ip(gw):
            QMessageBox.warning(
                self,
                "Error",
                "La dirección IP del gateway no es válida.\nFormato: xxx.xxx.xxx.xxx",
            )
            return

        self._manager.office_gateway = gw
        self._manager.check_interval = self._interval_spin.value() * 60
        self.accept()
