from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PySide6.QtCore import Qt

import i18n


class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("help"))
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumSize(480, 400)
        self.resize(520, 440)
        self.setModal(True)

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 13px;
                background: #fff;
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

        # Header
        hdr = QFrame()
        hdr.setStyleSheet("background: #f0f0f0; border-bottom: 1px solid #d0d0d0;")
        h = QHBoxLayout(hdr)
        h.setContentsMargins(16, 12, 16, 12)
        icon = QLabel("\U0001F4D6")
        icon.setStyleSheet("font-size: 18px;")
        h.addWidget(icon)
        title = QLabel(i18n.t("help_title"))
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        h.addWidget(title)
        h.addStretch()
        root.addWidget(hdr)

        # Body
        body = QVBoxLayout()
        body.setContentsMargins(20, 16, 20, 16)
        text = QLabel(i18n.t("help_body"))
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text.setStyleSheet("font-size: 13px; color: #333;")
        body.addWidget(text)
        body.addStretch()
        root.addLayout(body)

        # Footer
        ftr = QFrame()
        ftr.setObjectName("footer")
        f = QHBoxLayout(ftr)
        f.setContentsMargins(16, 8, 16, 8)
        ok = QPushButton(i18n.t("ok"))
        ok.setStyleSheet(
            "padding: 6px 24px; border: none; border-radius: 4px;"
            " background: #3b82f6; color: #fff; font-weight: 600;"
        )
        ok.clicked.connect(self.accept)
        f.addStretch()
        f.addWidget(ok)
        root.addWidget(ftr)
