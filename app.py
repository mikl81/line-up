from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea)
import sys


class AttractionRow(QFrame):
    def __init__(self, name, time):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #D3D3D3;
                border-radius: 10px;
                margin: 2px;
            }
        """)
        layout = QHBoxLayout(self)


        icon = QLabel("🖼️")
        icon.setFixedSize(30, 30)
        icon.setStyleSheet("background-color: white; border-radius: 5px; border: 1px solid #999;")
        icon.setAlignment(Qt.AlignCenter)

        name_label = QLabel(name)
        name_label.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px; font-weight: bold;")

        time_label = QLabel(f"{time}\nmin")
        time_label.setStyleSheet("color: red; background-color: white; border-radius: 5px; font-size: 10px; padding: 5px 10px;")
        time_label.setAlignment(Qt.AlignCenter)

        check_btn = QPushButton("✓")
        check_btn.setFixedSize(35, 35)
        check_btn.setStyleSheet("background-color: #7CFF6B; color: white; border-radius: 5px; font-weight: bold;")

        layout.addWidget(icon)
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(time_label)
        layout.addWidget(check_btn)

class TimeDisplay(QFrame):
    def __init__(self, time, place):
        super().__init__()
        
        self.setStyleSheet("""
            QFrame {
                background-color: #969696; 
                border-radius: 20px; 
                color: white;
            }
            QLabel { background: transparent; }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)

        eta_column = QVBoxLayout()
        eta_header = QLabel("ETA")
        eta_header.setStyleSheet("text-decoration: underline; font-size: 14px;")
        eta_header.setAlignment(Qt.AlignCenter)
        
        self.eta_val = QLabel(time)
        self.eta_val.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.eta_val.setAlignment(Qt.AlignCenter)
        
        eta_column.addWidget(eta_header)
        eta_column.addWidget(self.eta_val)

        place_column = QVBoxLayout()
        place_header = QLabel("Place")
        place_header.setStyleSheet("text-decoration: underline; font-size: 14px;")
        place_header.setAlignment(Qt.AlignCenter)
        
        self.place_val = QLabel(place)
        self.place_val.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.place_val.setAlignment(Qt.AlignCenter)
        
        place_column.addWidget(place_header)
        place_column.addWidget(self.place_val)

        main_layout.addLayout(eta_column)
        main_layout.addLayout(place_column)

    def update_status(self, new_eta, new_place):
        """Method to update labels dynamically"""
        self.eta_val.setText(new_eta)
        self.place_val.setText(str(new_place))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Line-Up")
        self.setFixedSize(320, 500)
        self.setStyleSheet("background-color: #F0F0F0;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        status_card = QFrame()
        status_card.setStyleSheet("background-color: #D3D3D3; border-radius: 20px;")
        status_layout = QHBoxLayout(status_card)

        self.status_info = TimeDisplay("N/A", "N/A")

        leave_btn = QPushButton("Leave\nLine")
        leave_btn.setFixedSize(80, 80)
        leave_btn.setStyleSheet("background-color: #F07167; color: white; border-radius: 40px; font-weight: bold;")

        status_layout.addWidget(self.status_info, stretch=2)
        status_layout.addWidget(leave_btn)
        
        main_layout.addWidget(status_card)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        list_layout.addWidget(AttractionRow("The Wheelie Wheel", "12"))
        list_layout.addWidget(AttractionRow("Thunderdome", "54"))
        list_layout.addWidget(AttractionRow("Tesla's Fury", "10"))
        list_layout.addWidget(AttractionRow("Simply the Best", "30"))
        
        list_layout.addStretch()
        scroll.setWidget(list_widget)
        main_layout.addWidget(scroll)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())