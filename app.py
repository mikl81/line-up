from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QDialog)
import sys
import time
import random

class ConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.setFixedSize(250, 150)
        
        # Remove the standard help button from the title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Style the dialog
        self.setStyleSheet("""
            QDialog { 
                background-color: #F0F0F0; 
                border: 2px solid #D3D3D3;
                border-radius: 10px;
            }
            QLabel { 
                color: #333; 
                font-size: 14px; 
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)

        message = QLabel("Leave the line?\nYou will lose your place.")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        # Button Container
        btn_layout = QHBoxLayout()
        
        self.yes_btn = QPushButton("Yes, Leave")
        self.yes_btn.setStyleSheet("background-color: #F07167; color: white; padding: 8px; border-radius: 5px; font-weight: bold;")
        
        self.no_btn = QPushButton("Cancel")
        self.no_btn.setStyleSheet("background-color: #969696; color: white; padding: 8px; border-radius: 5px;")

        btn_layout.addWidget(self.no_btn)
        btn_layout.addWidget(self.yes_btn)

        layout.addWidget(message)
        layout.addLayout(btn_layout)

        # Connect internal signals
        self.yes_btn.clicked.connect(self.accept) # Built-in QDialog accept (returns 1)
        self.no_btn.clicked.connect(self.reject) # Built-in QDialog reject (returns 0)

class AttractionRow(QFrame):
    #Custom signal to pass up the time and place vars from the attraction
    signal = pyqtSignal(str, str)

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

        check_btn = QPushButton("\u2714")
        check_btn.setFixedSize(35, 35)
        check_btn.setStyleSheet("background-color: #7CFF6B; color: white; border-radius: 5px; font-weight: bold;")
        check_btn.clicked.connect(lambda: self.check_out_ride(name, time, str(random.randint(1, int(time)))))

        layout.addWidget(icon)
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(time_label)
        layout.addWidget(check_btn)

    def check_out_ride(self, name, time, place):
        self.signal.emit(time, place)

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

        self.seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def update_status(self, new_eta, new_place):
        try:
            self.seconds = int(new_eta) * 60
            self.place_val.setText(str(new_place))
            self.update_label()
        except ValueError:
            self.eta_val.setText("N/A")
            self.remaining_seconds = 0

    def tick(self):
        if self.seconds > 0:
            self.seconds -=1
            self.update_label()
        else:
            self.reset_display()

    def update_label(self):
        min, sec = divmod(self.seconds, 60)
        self.eta_val.setText(f"{min}:{sec:02d}")

    def reset_display(self):
        self.seconds = 0
        self.eta_val.setText("N/A")
        self.place_val.setText("N/A")
     

class MainWindow(QMainWindow):
    #Test data
    rides = [
        ("The Wheelie Wheel", "12"),
        ("Thunderdome", "54"),
        ("Tesla's Fury", "10"),
        ("Simply the Best", "30")
    ]

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
        leave_btn.clicked.connect(self.confirm_leave)

        status_layout.addWidget(self.status_info, stretch=2)
        status_layout.addWidget(leave_btn)
        
        main_layout.addWidget(status_card)

        #Added for future in case we add more rides
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        #Test Attractions
        for name, time in self.rides:
            row = AttractionRow(name, time)
            row.signal.connect(self.status_info.update_status)
            list_layout.addWidget(row)
        
        list_layout.addStretch()
        scroll.setWidget(list_widget)
        main_layout.addWidget(scroll)

    def confirm_leave(self):
        dialog = ConfirmDialog(self)

        if dialog.exec_():
            self.status_info.reset_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())