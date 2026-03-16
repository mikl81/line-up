from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                             QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea, QDialog, QLineEdit)
import sys
import time
from  datetime import datetime
import random
import zmq
import json
from auth_service_types import RequestType, ResultType, prep_request

"""
    Confirmation window for removing your place in line
"""
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
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setStyleSheet("background-color: #F07167; color: white; padding: 8px; border-radius: 5px; font-weight: bold;")
        
        self.no_btn = QPushButton("Cancel")
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.setStyleSheet("background-color: #969696; color: white; padding: 8px; border-radius: 5px;")

        btn_layout.addWidget(self.no_btn)
        btn_layout.addWidget(self.yes_btn)

        layout.addWidget(message)
        layout.addLayout(btn_layout)

        # Connect internal signals
        self.yes_btn.clicked.connect(self.accept) # Built-in QDialog accept (returns 1)
        self.no_btn.clicked.connect(self.reject) # Built-in QDialog reject (returns 0)

class AttractionDialog(QDialog):
    reserved = pyqtSignal(str, str)

    def __init__(self, name, time, detail, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(280, 350)
        self.name = name
        self.time = time
        
        self.setStyleSheet("""
            QDialog { 
                background-color: white; 
                border: 2px solid #D3D3D3; 
                border-radius: 20px; 
            }
            #Title { font-size: 20px; font-weight: bold; color: #333; }
            #Detail { color: #666; font-size: 13px; }
            #TimeLabel { color: #F07167; font-weight: bold; font-size: 18px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel(name)
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        # Placeholder for a larger "Image" or Icon
        img_placeholder = QLabel("🎢")
        img_placeholder.setStyleSheet("font-size: 60px; background: #F0F0F0; border-radius: 15px; padding: 20px;")
        img_placeholder.setAlignment(Qt.AlignCenter)

        # Description text
        description = QLabel(detail)
        description.setObjectName("Detail")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)

        # Time Info
        wait_time = QLabel(f"Current Wait: {time} min")
        wait_time.setObjectName("TimeLabel")
        wait_time.setAlignment(Qt.AlignCenter)

        # Buttons
        btn_layout = QHBoxLayout()
        
        close_btn = QPushButton("Back")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("background-color: #969696; color: white; padding: 10px; border-radius: 8px;")
        close_btn.clicked.connect(self.reject)

        reserve_btn = QPushButton("Join Line")
        reserve_btn.setCursor(Qt.PointingHandCursor)
        reserve_btn.setStyleSheet("background-color: #7CFF6B; color: #333; padding: 10px; border-radius: 8px; font-weight: bold;")
        reserve_btn.clicked.connect(self.handle_reserve)

        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(reserve_btn)

        layout.addWidget(title)
        layout.addWidget(img_placeholder)
        layout.addWidget(description)
        layout.addWidget(wait_time)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def handle_reserve(self):
        # Generate random place and emit signal back to main
        place = str(random.randint(1, 100))
        self.reserved.emit(self.time, place)
        self.accept()

class AttractionRow(QFrame):
    #Custom signal to pass up the time and place vars from the attraction
    signal = pyqtSignal(str, str)

    def __init__(self, name, time, detail):
        super().__init__()

        self.name = name
        self.time = time
        self.detail = detail

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

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("background-color: white; padding: 5px; border-radius: 5px; font-weight: bold;")

        self.time_label = QLabel(f"{time}\nmin")
        self.time_label.setStyleSheet("color: red; background-color: white; border-radius: 5px; font-size: 10px; padding: 5px 10px;")
        self.time_label.setAlignment(Qt.AlignCenter)

        check_btn = QPushButton("\u2714")
        check_btn.setFixedSize(35, 35)
        check_btn.setStyleSheet("background-color: #7CFF6B; color: white; border-radius: 5px; font-weight: bold;")
        check_btn.clicked.connect(lambda: self.check_out_ride(name, time, str(random.randint(1, int(time)))))

        layout.addWidget(icon)
        layout.addWidget(self.name_label, stretch=1)
        layout.addWidget(self.time_label)
        layout.addWidget(check_btn)

        self.mousePressEvent = self.open_details

    def check_out_ride(self, name, time, place):
        self.signal.emit(str(time), place)
    
    def open_details(self, event):
        detail = AttractionDialog(self.name, self.time, self.detail, self.window())
        detail.reserved.connect(self.window().status_info.update_status)
        detail.exec_()

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

class LoginFrame(QFrame):
    login_successful = pyqtSignal(str)  # Emits username on success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loginFrame")
        self.setFixedSize(320, 220)
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        # Title
        self.title = QLabel("Sign In")
        self.title.setObjectName("loginTitle")
        self.title.setAlignment(Qt.AlignCenter)

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()

        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)

        layout.addWidget(self.title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.error_label)
        layout.addWidget(self.login_button)

    def setup_styles(self):
        self.setStyleSheet("""
            QFrame#loginFrame {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }

            QLabel#loginTitle {
                font-size: 18px;
                font-weight: bold;
                color: palette(windowText);
                border: none;
            }

            QLabel#errorLabel {
                color: #e74c3c;
                font-size: 12px;
                border: none;
            }

            QLineEdit {
                padding: 8px;
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
                color: palette(windowText);
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #3498db;
            }

            QPushButton {
                padding: 8px;
                background-color: #7CFF6B;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please fill in all fields.")
            return

        # Replace this with your real auth logic
        # if username == "admin" and password == "password":
        #     self.error_label.hide()
        #     self.login_successful.emit(username)
        # else:
        #     self.show_error("Invalid username or password.")
        
        context = zmq.Context()
        print("Connecting to auth server")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        req_type = RequestType.VERIFY_CREDENTIAL

        req = prep_request(req_type, username, password)
        print(req)
        socket.send_json(req)
        result = socket.recv_json()
        print(result["result_type"])
        if result["result_type"] == ResultType.VERIFY_SUCCESS:
            self.error_label.hide()
            self.login_successful.emit(username)
        else:
            self.show_error("Invalid username or password.")


    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

class HeaderDisplay(QFrame):
    #convention name and date on the right
    #user log in on right side
    def __init__(self) -> None:
        super().__init__()
        date = datetime.now()
        layout = QHBoxLayout(self)
        left_col = QVBoxLayout()

        self.date_label = QLabel("Date: " + date.strftime("%m/%d/%y"))
        self.con_name = QLabel("Convention: Starseekers")
        self.login = QPushButton("User: None")

        self.login.setCursor(Qt.PointingHandCursor)

        self.login.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                margin: 0;
                color: black;
                font: inherit;
                text-align: right;
            }
            QPushButton:hover {
                color: purple;
                text-decoration:underline;
            }
            QPushButton:pressed {
                background-color: transparent;
            }
            QPushButton:focus {
                outline: none;
                border: none;
            }
        """)

        self.login.clicked.connect(lambda: self.open_login())

        left_col.addWidget(self.date_label)
        left_col.addWidget(self.con_name)
        layout.addLayout(left_col)
        layout.addWidget(self.login)

    def open_login(self):
        dialog = QDialog(self.window())
        dialog.setWindowTitle("Login")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setFixedSize(320, 220)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        login_frame = LoginFrame()
        login_frame.login_successful.connect(lambda username: self.on_login(username, dialog))
        layout.addWidget(login_frame)

        dialog.exec_()

    def on_login(self, username, dialog):
        self.login.setText(f"User: {username}")
        dialog.accept()

class MainWindow(QMainWindow):
    #Test data
    # rides = [
    #     ("The Wheelie Wheel", "12", "The best circular object this side of Thunderdome!"),
    #     ("Thunderdome", "54", "The best ride in the wasteland. Now featuring Tina Turner!"),
    #     ("Tesla's Fury", "10", "Rated the most scary ride by Thomas Edison"),
    #     ("Simply the Best", "30", "A ride that will surely take you down memory lane with classic song after classic song!")
    # ]

    def __init__(self):
        super().__init__()
        rides = self.request_ride_data()
        print(rides)

        self.setWindowTitle("Line-Up")
        self.setFixedSize(320, 500)
        self.setStyleSheet("background-color: #F0F0F0;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.header = HeaderDisplay()

        self.header.setStyleSheet("""
            QFrame {
                border: none;
                border-bottom: 1px solid palette(mid);
            }
            QFrame * {
                border: none;
            }
        """)

        main_layout.addWidget(self.header)

        status_card = QFrame()
        status_card.setStyleSheet("background-color: #D3D3D3; border-radius: 20px;")
        status_layout = QHBoxLayout(status_card)



        self.status_info = TimeDisplay("N/A", "N/A")

        leave_btn = QPushButton("Leave\nLine")
        leave_btn.setCursor(Qt.PointingHandCursor)
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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        action_call = QLabel("Select a ride below to save your spot!")
        action_call.setStyleSheet("""
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-decoration: underline;
            """)
        action_call.setAlignment(Qt.AlignHCenter)
        
        main_layout.addWidget(action_call)

        #Attractions
        # for name, time, detail in self.rides:
        #     row = AttractionRow(name, time, detail)
        #     row.setCursor(Qt.PointingHandCursor)
        #     row.signal.connect(self.status_info.update_status)
        #     list_layout.addWidget(row)

        for row in rides["data"]["rows"]:
            place = self.request_place_in_line(row["RideID"])
            est_wait = place["data"]["total"]*5
            gui = AttractionRow(row["RideName"], est_wait, row["RideDesc"])
            gui.setCursor(Qt.PointingHandCursor)
            gui.signal.connect(self.status_info.update_status)
            list_layout.addWidget(gui)

        list_layout.addStretch()
        scroll.setWidget(list_widget)
        main_layout.addWidget(scroll)

    def confirm_leave(self):
        dialog = ConfirmDialog(self)

        if dialog.exec_():
            self.status_info.reset_display()

    def request_ride_data(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5556")

        request = {
            "action": "select",
            "table": "rides"
        }

        socket.send(json.dumps(request).encode("utf-8"))

        response_bytes = socket.recv()

        response = json.loads(response_bytes.decode("utf-8"))

        return response
    
    def request_place_in_line(self, rideId):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5557")

        request = {
            "action": "filtered_statistics",
            "table": "users_to_rides",
            "filters": {
                "RideID": f"{rideId}"
            }
        }

        socket.send(json.dumps(request).encode("utf-8"))

        response_bytes = socket.recv()

        response = json.loads(response_bytes.decode("utf-8"))

        return response

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())