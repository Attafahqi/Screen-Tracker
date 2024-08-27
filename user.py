import os
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import UI.res_rc

device_name = os.getenv('DEVICE_NAME')

def initialize_firebase():
    cred = credentials.Certificate('screen-time-52e52-firebase-adminsdk-1aqkf-e11d87c05a.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://screen-time-52e52-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

def get_data_from_firebase(device_name, start_date, end_date):
    ref = db.reference(f'device/{device_name}/activities')
    activities = ref.get()
    return activities

def aggregate_data(activities, start_date, end_date):
    data = {}

    if isinstance(activities, list):
        for activity in activities:
            if not activity.get('name') or 'time_entries' not in activity:
                continue

            for entry in activity['time_entries']:
                start_time = datetime.fromisoformat(entry['start_time'])
                end_time = datetime.fromisoformat(entry['end_time'])
                duration = timedelta(days=entry['days'], hours=entry['hours'], minutes=entry['minutes'], seconds=entry['seconds'])
                date = start_time.date()

                if start_date <= date <= end_date:
                    if date not in data:
                        data[date] = {}
                    if activity['name'] not in data[date]:
                        data[date][activity['name']] = timedelta()
                    data[date][activity['name']] += duration

    return data

def generate_graphs(data, start_date, end_date):
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    activities = set()
    for day_data in data.values():
        activities.update(day_data.keys())

    top_activities = sorted(activities, key=lambda a: sum(
        data.get(date, {}).get(a, timedelta()).total_seconds() for date in dates
    ), reverse=True)[:10]

    fig, ax = plt.subplots()
    for activity in top_activities:
        hours = [data.get(date, {}).get(activity, timedelta()).total_seconds() / 3600 for date in dates]
        ax.plot(dates, hours, label=activity)

    ax.set_xlabel('Date', color= 'white')
    ax.set_ylabel('Hours', color= 'white')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    fig.autofmt_xdate()
    ax.set_facecolor('white')
    ax.tick_params(axis='both', colors='white')
    ax.spines['top'].set_edgecolor('white')    
    ax.spines['right'].set_edgecolor('white')  
    ax.spines['bottom'].set_edgecolor('white') 
    ax.spines['left'].set_edgecolor('white')

    plt.savefig('UI/user_graph.png', bbox_inches='tight', dpi=300, transparent=True)

    handles, labels = ax.get_legend_handles_labels()
    fig_legend = plt.figure(figsize=(4, 2))
    fig_legend.legend(handles, labels, loc='center', fontsize=6)
    fig_legend.gca().axis('off')
    fig_legend.savefig('Ui/user_legend.png', bbox_inches='tight', dpi=300, transparent=True)

    return True

class User (QMainWindow):
    def __init__(self):
        super(User, self).__init__()
        uic.loadUi("UI/user.ui", self)
        self.setWindowTitle("APK Screen Tracker")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.Generate.clicked.connect(self.admin)
        self.Exit.clicked.connect(self.quit)

    def quit(self):
        QApplication.quit()
    
    def admin(self):
        start_date_qt = self.StartDate.date()  
        end_date_qt = self.EndDate.date()     
        start_date = start_date_qt.toPyDate() 
        end_date = end_date_qt.toPyDate()

        if start_date >= end_date:
            self.show_popup_message("Start date must be before to end date.")
            return
        
        activities = get_data_from_firebase(device_name, start_date, end_date)
        
        data = aggregate_data(activities, start_date, end_date)
        generate_graphs(data, start_date, end_date)
        self.Graph.setStyleSheet(f"border-image: url(UI/user_graph.png);")
        self.Graph.repaint()
        self.Legend.setStyleSheet(f"border-image: url(UI/user_legend.png);")
        self.Legend.repaint()
        data = 0
    
    def show_popup_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()
        
if __name__ == "__main__":
    if not os.environ['DEVICE_NAME'] :
         QApplication.quit()

    initialize_firebase()
    app = QApplication([])
    window = User()
    app.exec_()

