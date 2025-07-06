from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QSizePolicy, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class HelpSupportDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Help & Support")
        self.setMinimumSize(800, 600)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel#header_label {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QLabel {
                font-size: 16px;
                color: #34495e;
                line-height: 1.5;
            }
            QLabel#section_title {
                font-size: 20px;
                font-weight: bold;
                color: #4834d4;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: white;
            }
            QScrollArea > QWidget { /* Content widget inside scroll area */
                background-color: white;
                padding: 15px;
            }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 90px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 14px;
                background: #0984e3;
            }
            QPushButton:hover {
                background: #0062a3;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Help & Support")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        # Search bar (optional, but good for UX)
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search help topics...")
        self.search_input.returnPressed.connect(self.perform_search) # Connect Enter key
        search_layout.addWidget(self.search_input)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)

        # Scrollable content area for help topics
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft) # Align content to top-left
        self.scroll_layout.setContentsMargins(10, 10, 10, 10) # Padding inside scroll area

        self._add_help_content() # Populate initial help content

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

        main_layout.addStretch() # Push content to top
        self.setLayout(main_layout)

    def _add_help_content(self):
        """Populates the scroll area with predefined help content."""
        # Clear existing content before adding new (useful for search/filter)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # FAQ Section
        self.scroll_layout.addWidget(self._create_section_title("Frequently Asked Questions (FAQ)"))
        self.scroll_layout.addWidget(QLabel("<b>Q: How do I add a new medicine?</b><br>A: Go to 'Medicine Management' from the sidebar, then click the 'Add Medicine' button."))
        self.scroll_layout.addWidget(QLabel("<b>Q: How do I record a sale?</b><br>A: Click 'New Sale' button on the top bar, select the medicine, quantity, and customer (optional)."))
        self.scroll_layout.addWidget(QLabel("<b>Q: Can I change my password?</b><br>A: Yes, go to 'Settings' from the sidebar."))
        self.scroll_layout.addWidget(QLabel("<b>Q: How do I view sales reports?</b><br>A: Click 'Sales Report' from the sidebar. You can filter by date."))
        self.scroll_layout.addWidget(QLabel("<b>Q: What if a medicine goes out of stock?</b><br>A: The system automatically archives medicines with zero stock. You can view them in 'Medicine Management'."))

        # Contact Us Section
        self.scroll_layout.addWidget(self._create_section_title("Contact Us"))
        self.scroll_layout.addWidget(QLabel("If you need further assistance, please contact our support team:"))
        self.scroll_layout.addWidget(QLabel("<b>Email:</b> iamhammaddev03@gmail.com"))
        self.scroll_layout.addWidget(QLabel("<b>Phone:</b> +92 03279747932"))
        self.scroll_layout.addWidget(QLabel("<b>WhatsApp:</b> +92 03091860907"))
        self.scroll_layout.addWidget(QLabel("<b>Operating Hours:</b> Mon-Fri, 9 AM - 5 PM (Local Time)"))

        # About Section
        self.scroll_layout.addWidget(self._create_section_title("About This Application"))
        self.scroll_layout.addWidget(QLabel("This Pharmacy Management Application helps you efficiently manage your medicine inventory, sales, purchases, orders, and user accounts."))
        self.scroll_layout.addWidget(QLabel("<b>Version:</b> 1.0.0"))
        self.scroll_layout.addWidget(QLabel("<b>Developed by:</b> Hammad - @copyright all rights are reserved"))


    def _create_section_title(self, text):
        """Helper to create styled section titles."""
        title_label = QLabel(text)
        title_label.setObjectName("section_title")
        return title_label

    def perform_search(self):
        """
        Performs a simple search on help content.
        For a real app, this would involve more sophisticated searching.
        For now, it's just a placeholder.
        """
        search_query = self.search_input.text().strip().lower()
        if not search_query:
            self._add_help_content() # Reload all content if search is empty
            self.status_bar.showMessage("Displaying all help topics.", 3000)
            return

        # Simple simulation of search:
        # In a real app, you'd filter the actual data source.
        # For this example, we'll just show a message.
        QMessageBox.information(self, "Search Result", 
                                f"Searching for '{search_query}'... (Feature under development)\n"
                                "Please refer to the listed FAQs for now.")
        # You could implement actual filtering here by re-populating self.scroll_layout
        # with only relevant QLabel widgets.
        
        # Example of how you might filter (conceptual, requires storing content in a searchable way)
        # filtered_content = [label for label in self._all_help_labels if search_query in label.text().lower()]
        # self._add_help_content(filtered_content) # A new method to add specific content

