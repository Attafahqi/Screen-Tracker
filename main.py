import sys
import os
import json
import subprocess
import firebase_admin
from firebase_admin import credentials, db
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import UI.res_rc

def initialize_firebase():
    firebasecread_file = 'FirebaseCred.json'
    data = load_from_json(firebasecread_file)
    firebase_key = data['firebase_key']
    data_url = data.get('data_url')
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred, {
        'databaseURL': data_url
    })

def load_from_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def check_firebase_file():
    try:
        with open('FirebaseCred.json', 'r') as file:
            return True
    except FileNotFoundError:
        return False
    
def check_device_file():
    try:
        with open('DeviceName.json', 'r') as file:
            return True
    except FileNotFoundError:
        return False

class InitialPage(QMainWindow):
    def __init__(self):
        super(InitialPage, self).__init__()
        uic.loadUi("UI/initialpage.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
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
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
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
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
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
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
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
            admin_check = "True"
            self.close()
            os.environ['ADMIN_CHECK'] = admin_check
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

class FirebaseEntry (QMainWindow):
    def __init__(self):
        super(FirebaseEntry, self).__init__()
        uic.loadUi("UI/firebaseentry.ui", self)
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.Submit.clicked.connect(self.firebaseentry)
        self.Exit.clicked.connect(self.quit)
    
    def quit(self):
        QApplication.quit()

    def firebaseentry(self):
        firebase_key = self.FirebaseKey.text()
        data_url = self.DataURL.text()

        firebase_info = {"firebase_key": firebase_key, "data_url": data_url}
        with open('FirebaseCred.json', 'w') as file:
            json.dump(firebase_info, file)
        
        self.quit()
        


def main():
    app = QApplication(sys.argv)

    if not check_firebase_file():
        window = FirebaseEntry()
        app.exec_()

    initialize_firebase()

    if not check_device_file():
        window = InitialPage()
    else:
        window = Login()

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
