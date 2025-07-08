from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QHeaderView, QLabel, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from datetime import datetime

class PaginatedTable(QWidget):
    edit_requested = pyqtSignal(dict)     # emits medicine dict
    delete_requested = pyqtSignal(int)    # emits medicine id

    PAGE_SIZE = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget { background: white; border-radius: 12px; font-size:14px;}
            QHeaderView::section { background: #3a7bd5; color:white; font-weight: bold; font-size:15px;}
            QPushButton, QToolButton {
                border-radius: 8px; padding: 6px 16px; font-weight:bold; font-size:14px;
            }
            QPushButton#nav { background: #6c7ae0; color: white; border: none;}
            QPushButton#nav:disabled { background: #d3dae0; color: #888;}
            QPushButton#edit_btn { background:#28a745; color:white; min-width:64px; padding:5px 0; }
            QPushButton#delete_btn { background:#e74c3c; color:white; min-width:72px; padding:5px 0; }
            QLabel#page_info { font-size:15px; font-weight:500; color: #444;}
        """)

        self._all_medicines = []
        self._filtered_meds = []
        self._current_page = 1
        self._total_pages = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Strength", "Batch No", "Expiry Date", "Quantity", "Unit Price", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table, 1)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-style: italic;")
        layout.addWidget(self.error_label)

        # Pagination controls
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 5, 0, 0)
        nav_layout.setSpacing(12)

        self.prev_btn = QPushButton("⟵ Previous")
        self.prev_btn.setObjectName("nav")
        self.prev_btn.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.page_info = QLabel("")
        self.page_info.setObjectName("page_info")
        self.page_info.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.page_info)

        nav_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.next_btn = QPushButton("Next ⟶")
        self.next_btn.setObjectName("nav")
        self.next_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def set_data(self, medicines):
        """Call this with the FULL medicine list. Actual display is paginated."""
        self.error_label.clear()
        self._all_medicines = medicines if medicines else []
        self._filtered_meds = self._all_medicines  # By default, no search filter
        self._current_page = 1
        self._total_pages = max(1, (len(self._filtered_meds) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self._update_page()

    def filter(self, search_text):
        """Filter by search_text (case-insensitive, any field) and reset pagination."""
        s = search_text.strip().lower()
        if not s:
            self._filtered_meds = self._all_medicines
        else:
            keys = ["name", "strength", "batch_no", "expiry_date", "quantity", "unit_price"]
            self._filtered_meds = [
                m for m in self._all_medicines
                if any(s in str(m.get(k, "")).lower() for k in keys)
            ]
        self._current_page = 1
        self._total_pages = max(1, (len(self._filtered_meds) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self._update_page()

    def _update_page(self):
        meds = self._filtered_meds
        start = (self._current_page - 1) * self.PAGE_SIZE
        end = min(start + self.PAGE_SIZE, len(meds))
        paged = meds[start:end]

        self.table.setRowCount(0)
        self.table.setRowCount(len(paged))

        errors = []
        today = datetime.today()

        for row, med in enumerate(paged):
            try:
                self.table.setItem(row, 0, QTableWidgetItem(str(med.get("name", ""))))
                self.table.setItem(row, 1, QTableWidgetItem(str(med.get("strength", ""))))
                self.table.setItem(row, 2, QTableWidgetItem(str(med.get("batch_no", ""))))
                self.table.setItem(row, 3, QTableWidgetItem(str(med.get("expiry_date", ""))))
                self.table.setItem(row, 4, QTableWidgetItem(str(med.get("quantity", ""))))
                self.table.setItem(row, 5, QTableWidgetItem("₨{}".format(med.get("unit_price", ""))))

                low_stock = False
                expiry_soon = False

                # Quantity check
                try:
                    quantity = int(med.get("quantity", 0))
                    low_stock = quantity < 10
                except (ValueError, TypeError):
                    errors.append(f"Invalid quantity for '{med.get('name', 'Unknown')}'.")

                # Expiry check
                expiry_str = med.get("expiry_date", "")
                if expiry_str:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                        if expiry_date > today and (expiry_date - today).days <= 30:
                            expiry_soon = True
                        if expiry_date <= today:
                            expiry_soon = True
                    except (ValueError, TypeError):
                        errors.append(f"Invalid expiry date for '{med.get('name', 'Unknown')}': {expiry_str}")

                # Highlight cells
                for col in range(6):
                    item = self.table.item(row, col)
                    if not item:
                        continue
                    if low_stock and expiry_soon:
                        item.setBackground(QColor("#ffcccc"))  # Light red
                    elif low_stock:
                        item.setBackground(QColor("#fff7e6"))  # Light orange
                    elif expiry_soon:
                        item.setBackground(QColor("#e6f7ff"))  # Light blue
                    else:
                        item.setBackground(QColor("white"))

                # Action buttons
                action_widget = QWidget()
                actions = QHBoxLayout(action_widget)
                actions.setContentsMargins(0, 0, 0, 0)
                actions.setSpacing(6)

                edit_btn = QPushButton("Edit")
                edit_btn.setObjectName("edit_btn")
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.setFixedWidth(64)
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("delete_btn")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setFixedWidth(72)

                edit_btn.clicked.connect(lambda _, m=med: self.edit_requested.emit(m))
                delete_btn.clicked.connect(lambda _, id=med.get("id", -1): self.delete_requested.emit(id))

                actions.addWidget(edit_btn)
                actions.addWidget(delete_btn)
                actions.addStretch()
                action_widget.setLayout(actions)
                self.table.setCellWidget(row, 6, action_widget)

            except Exception as e:
                errors.append(f"Error processing row {row + 1}: {str(e)}")

        # Page info
        total = len(self._filtered_meds)
        start_show = (self._current_page - 1) * self.PAGE_SIZE + 1 if total > 0 else 0
        end_show = min(self._current_page * self.PAGE_SIZE, total)
        self.page_info.setText(f"Showing {start_show}-{end_show} of {total}   |   Page {self._current_page}/{self._total_pages}")

        # Navigation buttons
        self.prev_btn.setDisabled(self._current_page <= 1)
        self.next_btn.setDisabled(self._current_page >= self._total_pages)

        if errors:
            self.error_label.setText(" | ".join(errors))
        else:
            self.error_label.clear()

    def next_page(self):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._update_page()

    def prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._update_page()

    def sizeHint(self):
        return self.table.sizeHint()