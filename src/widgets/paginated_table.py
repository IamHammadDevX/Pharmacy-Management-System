from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class PaginatedTable(QWidget):
    edit_requested = pyqtSignal(dict)     # emits medicine dict
    delete_requested = pyqtSignal(int)    # emits medicine id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget { background: white; border-radius: 12px; }
            QHeaderView::section { background: #f4f6ff; font-weight: bold; }
            QPushButton { border-radius: 6px; padding: 4px 12px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 7 columns: Name, Strength, Batch, Expiry, Quantity, Price, Actions
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Strength", "Batch No", "Expiry Date", "Quantity", "Unit Price", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # Dummy pagination controls (optional, can be ignored for now)
        pagination = QHBoxLayout()
        pagination.addStretch()
        pagination.addWidget(QPushButton("Prev"))
        pagination.addWidget(QPushButton("Next"))
        layout.addLayout(pagination)

    def set_data(self, medicines):
        self.table.setRowCount(len(medicines))
        for row, med in enumerate(medicines):
            # --- Set Items ---
            self.table.setItem(row, 0, QTableWidgetItem(med.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(med.get("strength", "")))
            self.table.setItem(row, 2, QTableWidgetItem(med.get("batch_no", "")))
            self.table.setItem(row, 3, QTableWidgetItem(med.get("expiry_date", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(med.get("quantity", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(med.get("unit_price", ""))))

            # --- Highlighting Logic ---
            low_stock = False
            expiry_soon = False
            try:
                low_stock = int(med.get("quantity", 0)) < 10
            except Exception:
                pass
            expiry_str = med.get("expiry_date", "")
            if expiry_str:
                from datetime import datetime, timedelta
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                    today = datetime.today()
                    if expiry_date > today and (expiry_date - today).days <= 30:
                        expiry_soon = True
                except Exception:
                    pass
            for col in range(6):  # Only color data columns, not actions
                item = self.table.item(row, col)
                if not item:
                    continue
                if low_stock and expiry_soon:
                    item.setBackground(QColor("#ffcccc"))  # Light red for both
                elif low_stock:
                    item.setBackground(QColor("#fff7e6"))  # Light orange for low stock
                elif expiry_soon:
                    item.setBackground(QColor("#e6f7ff"))  # Light blue for expiry soon
                else:
                    item.setBackground(QColor("white"))

            # --- Actions: Edit and Delete buttons ---
            action_widget = QWidget()
            actions = QHBoxLayout(action_widget)
            actions.setContentsMargins(0, 0, 0, 0)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("background:#36b37e; color:white;")
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background:#ff5630; color:white;")

            # Use default arguments in lambda to avoid late binding bug!
            edit_btn.clicked.connect(lambda _, m=med: self.edit_requested.emit(m))
            delete_btn.clicked.connect(lambda _, id=med["id"]: self.delete_requested.emit(id))

            actions.addWidget(edit_btn)
            actions.addWidget(delete_btn)
            actions.addStretch()
            action_widget.setLayout(actions)
            self.table.setCellWidget(row, 6, action_widget)