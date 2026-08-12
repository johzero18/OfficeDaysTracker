from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDateEdit, QFrame, QMessageBox, QWidget,
)

import i18n


class RecordsDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle(i18n.t("records_title"))
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumSize(440, 480)
        self.resize(460, 540)
        self.setModal(True)

        self._build_ui()
        self._reload()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 13px;
                background: #fff;
            }
            #sectionTitle {
                font-size: 14px;
                font-weight: 600;
            }
            #btn {
                font-size: 11px;
                padding: 3px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
            }
            #btn:hover {
                background: #e8e8e8;
            }
            #btnDel {
                font-size: 11px;
                padding: 3px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #fff;
                color: #c00;
            }
            #btnDel:hover {
                background: #ffe0e0;
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
        icon = QLabel("\U0001F4C5")
        icon.setStyleSheet("font-size: 18px;")
        h.addWidget(icon)
        self._month_title = QLabel("")
        self._month_title.setStyleSheet("font-size: 15px; font-weight: 600;")
        h.addWidget(self._month_title)
        h.addStretch()
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("font-size: 12px; color: #555;")
        h.addWidget(self._count_label)
        root.addWidget(hdr)

        # Body
        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(12)

        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px;"
            " background: #fff; }"
            " QListWidget::item { padding: 2px 0px; }"
        )
        body.addWidget(self._list)

        add_row = QHBoxLayout()
        add_row.addWidget(QLabel(i18n.t("add_day")))
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("dd/MM/yyyy")
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setStyleSheet(
            "padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;"
        )
        add_row.addWidget(self._date_edit)
        add_btn = QPushButton(i18n.t("add"))
        add_btn.setObjectName("btn")
        add_btn.clicked.connect(self._on_add)
        add_row.addWidget(add_btn)
        add_row.addStretch()
        body.addLayout(add_row)

        root.addLayout(body)

        # Footer
        ftr = QFrame()
        ftr.setObjectName("footer")
        f = QHBoxLayout(ftr)
        f.setContentsMargins(16, 8, 16, 8)
        close_btn = QPushButton(i18n.t("close"))
        close_btn.setStyleSheet(
            "padding: 6px 20px; border: 1px solid #ccc; border-radius: 4px; background: #fff;"
        )
        close_btn.clicked.connect(self.accept)
        f.addStretch()
        f.addWidget(close_btn)
        root.addWidget(ftr)

    def _reload(self):
        records = self._manager.get_records_for_current_month()
        now = date.today()
        self._month_title.setText(
            i18n.t("records_of_month", month=i18n.month_name(now.month), year=now.year)
        )
        self._count_label.setText(i18n.t("days_count", n=len(records)))
        self._list.clear()
        if not records:
            item = QListWidgetItem(i18n.t("no_records_month"))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)
            return
        for rec in records:
            self._add_row(rec)

    def _add_row(self, rec):
        dt = date.fromisoformat(rec["date"])
        label = QLabel(f"{dt.day} de {i18n.month_name(dt.month)} de {dt.year}")
        label.setStyleSheet("font-size: 13px;")
        edit_btn = QPushButton("\u270E")
        edit_btn.setObjectName("btn")
        edit_btn.setToolTip(i18n.t("change_date"))
        edit_btn.clicked.connect(lambda _=False, rid=rec["id"]: self._on_edit(rid))
        del_btn = QPushButton("\u2715")
        del_btn.setObjectName("btnDel")
        del_btn.setToolTip(i18n.t("delete"))
        del_btn.clicked.connect(lambda _=False, rid=rec["id"]: self._on_delete(rid))

        row = QHBoxLayout()
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)
        row.addWidget(label)
        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(del_btn)

        holder = QWidget()
        holder.setLayout(row)
        item = QListWidgetItem()
        item.setSizeHint(holder.sizeHint())
        self._list.addItem(item)
        self._list.setItemWidget(item, holder)

    def _current_rec(self, record_id):
        for rec in self._manager.get_records_for_current_month():
            if rec["id"] == record_id:
                return rec
        return None

    def _on_add(self):
        qdate = self._date_edit.date()
        day = date(qdate.year(), qdate.month(), qdate.day())
        if not self._manager.add_record(day):
            QMessageBox.information(self, i18n.t("exists_title"), i18n.t("already_exists"))
            return
        self._reload()

    def _on_edit(self, record_id):
        rec = self._current_rec(record_id)
        if not rec:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.t("change_date"))
        lay = QVBoxLayout(dlg)
        de = QDateEdit()
        de.setCalendarPopup(True)
        de.setDisplayFormat("dd/MM/yyyy")
        dt = date.fromisoformat(rec["date"])
        de.setDate(QDate(dt.year, dt.month, dt.day))
        de.setStyleSheet("padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;")
        lay.addWidget(de)
        btns = QHBoxLayout()
        ok = QPushButton(i18n.t("save"))
        ok.setStyleSheet(
            "padding: 6px 16px; border: none; border-radius: 4px;"
            " background: #3b82f6; color: #fff; font-weight: 600;"
        )
        ok.clicked.connect(dlg.accept)
        cancel = QPushButton(i18n.t("cancel"))
        cancel.setStyleSheet(
            "padding: 6px 16px; border: 1px solid #ccc; border-radius: 4px; background: #fff;"
        )
        cancel.clicked.connect(dlg.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        lay.addLayout(btns)
        if dlg.exec():
            qdate = de.date()
            new_day = date(qdate.year(), qdate.month(), qdate.day())
            if not self._manager.edit_record(record_id, new_day):
                QMessageBox.information(self, i18n.t("exists_title"), i18n.t("already_exists"))
                return
            self._reload()

    def _on_delete(self, record_id):
        rec = self._current_rec(record_id)
        if not rec:
            return
        ans = QMessageBox.question(
            self,
            i18n.t("confirm"),
            i18n.t("confirm_delete", date=rec["date"]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            self._manager.remove_record(record_id)
            self._reload()
