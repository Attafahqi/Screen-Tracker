import sys
import os
import json
import subprocess
import firebase_admin
from firebase_admin import credentials, db
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
import UI.res_rc

cred = credentials.Certificate('screen-time-52e52-firebase-adminsdk-1aqkf-e11d87c05a.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://screen-time-52e52-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def check_device_file():
    try:
        with open('DeviceName.json', 'r') as file:
            return True
    except FileNotFoundError:
        return False


def login_to_device():
    device_name = input("Enter Device Name: ")
    password = input("Enter Password: ")

    ref = db.reference(f'device/{device_name}')
    device_data = ref.get()

    if device_data is None or device_data.get('password') != password:
        print("Incorrect Device Name or Password.")
        return

    device_info = {"device_name": device_name, "password": password}
    with open('DeviceName.json', 'w') as file:
        json.dump(device_info, file)

class InitialPage(QMainWindow):
    def __init__(self):
        super(InitialPage, self).__init__()
        uic.loadUi("UI/initialpage.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("APK Screen Tracker")
        self.show()
        
        self.CreateNewDevice.clicked.connect(self.openCreateNewDevice)
        self.LoginInNewDevice.clicked.connect(self.openLoginInNewDevice)
        self.Exit.clicked.connect(self.quit)

    def quit(self):
        QApplication.quit()

    def openCreateNewDevice(self):
        self.createDeviceWindow = CreateNewDevice()
        self.createDeviceWindow.show()
        self.close()

    def openLoginInNewDevice(self):
        self.loginDeviceWindow = LoginInNewDevice()
        self.loginDeviceWindow.show()
        self.close()
    
class CreateNewDevice(QMainWindow):
    def __init__(self):
        super(CreateNewDevice, self).__init__()
        uic.loadUi("UI/createdevice.ui", self)
        self.setWindowTitle("APK Screen Tracker")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.CreateNewDevice.clicked.connect(self.create_new_device)
        self.Back.clicked.connect(self.back_to_initialpage)
        self.Exit.clicked.connect(self.quit)

    def quit(self):
        QApplication.quit()

    def create_new_device(self):
        device_name = self.DeviceName.text()
        password = self.Password.text()

        if not self.create_new_device_logic(device_name, password):
            self.DeviceName.clear()
            self.Password.clear()
            self.show_warning("This device already exists. Please choose another name.")
        
        else:
            QApplication.quit()

    def create_new_device_logic(self, device_name, password):
        device_name = device_name.lower()
        
        ref = db.reference(f'device/{device_name}')
        
        if ref.get() is not None:
            return False  

        ref.set({
            "password": password
        })

        device_info = {"device_name": device_name, "password": password}
        with open('DeviceName.json', 'w') as file:
            json.dump(device_info, file)
        
        self.close()
        return True

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def back_to_initialpage(self):
        self.initialPageWindow = InitialPage()
        self.initialPageWindow.show()
        self.close()  

class LoginInNewDevice(QMainWindow):
    def __init__(self):
        super(LoginInNewDevice, self).__init__()
        uic.loadUi("UI/logininnewdevice.ui", self)
        self.setWindowTitle("APK Screen Tracker")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.LoginInNewDevice.clicked.connect(self.login_in_new_device)
        self.Back.clicked.connect(self.back_to_initialpage)
        self.Exit.clicked.connect(self.quit)

    def quit(self):
        QApplication.quit()

    def login_in_new_device(self):
        device_name = self.DeviceName.text()
        password = self.Password.text()

        if not self.login_in_new_device_logic(device_name, password):
            self.DeviceName.clear()
            self.Password.clear()
            self.show_warning("Your device name or password is wrong. Please try again.")
        
        else:
            QApplication.quit()

    def login_in_new_device_logic(self, device_name, password):
        device_name = device_name.lower()

        ref = db.reference(f'device/{device_name}')
        device_data = ref.get()

        if device_data is None or device_data.get('password') != password:
            return False 

        device_info = {"device_name": device_name, "password": password}
        with open('DeviceName.json', 'w') as file:
            json.dump(device_info, file)

        return True
    
    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def back_to_initialpage(self):
        self.initialPageWindow = InitialPage()
        self.initialPageWindow.show()
        self.close() 

class Login (QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("UI/login.ui", self)
        self.setWindowTitle("APK Screen Tracker")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.Login.clicked.connect(self.login)
        self.Exit.clicked.connect(self.quit)

    def quit(self):
        QApplication.quit()
    
    def login(self):
        device_name = self.DeviceName.text()
        password = self.Password.text()

        if not self.login_logic(device_name, password):
            self.DeviceName.clear()
            self.Password.clear()
            self.show_warning("Your device name or password is wrong. Please try again.")
        
    
    def login_logic(self, device_name, password):
        device_name = device_name.lower()
        ref = db.reference(f'device/{device_name}')
        device_data = ref.get()

        if device_data is None or device_data.get('password') != password:
            return False

        if device_name == "admin":
            print("Opening Admin Panel...")
            self.close()
            subprocess.run([sys.executable, 'admin.py'])
            QApplication.quit()

        else:
            print("Opening User Panel...")
            self.close()
            os.environ['DEVICE_NAME'] = device_name
            subprocess.run([sys.executable, 'user.py'])
            QApplication.quit()

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()


def main():
    if not check_device_file():
        app = QApplication([])
        window = InitialPage()
        app.exec_()

    else:
        app = QApplication([])
        window = Login()
        app.exec_()

if __name__ == "__main__":
    main()
