import os
import json
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDesktopWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import UI.res_rc

device_name = os.getenv('DEVICE_NAME')

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

    total_time_per_activity = {}
    for activity in activities:
        total_time = sum(data.get(date, {}).get(activity, timedelta()).total_seconds() for date in dates)
        total_time_per_activity[activity] = total_time

    total_time_seconds = int(sum(total_time_per_activity.values()))
    num_days = (end_date - start_date).days
    total_inactive_time_seconds = ((num_days + 1) * 86400) - total_time_seconds
    percentage = f"{total_time_seconds * 100 / ((num_days + 1) * 86400):.1f}%" 
    
    hours, remainder = divmod(total_time_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours:02}H {minutes:02}M {seconds:02}S"

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        [total_time_seconds, total_inactive_time_seconds],
        wedgeprops={'width': 0.3},
        startangle=90,
        colors=['#5DADE2', '#515A5A']
    )
    plt.text(0, 0, percentage, ha='center', va='center', fontsize=42, color='white')
    plt.savefig('UI/user_donutchart.png', bbox_inches='tight', dpi=300, transparent=True)

    return formatted_time, num_days

class User (QMainWindow):
    def __init__(self):
        super(User, self).__init__()
        uic.loadUi("UI/user.ui", self)
        self.center()
        self.setWindowTitle("FAP Screen Tracker")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.Generate.clicked.connect(self.admin)
        self.Exit.clicked.connect(self.quit)

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
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
        formatted_time, num_days = generate_graphs(data, start_date, end_date)
        self.Graph.setStyleSheet(f"border-image: url(UI/user_graph.png);")
        self.Graph.repaint()
        self.Legend.setStyleSheet(f"border-image: url(UI/user_legend.png);")
        self.Legend.repaint()
        self.Graph_2.setStyleSheet(f"border-image: url(UI/admin_donutchart.png);")
        self.Graph_2.repaint()
        self.TotalText.setText("Total Screen Time in " + str(num_days) + " days")
        self.TotalTime.setText(formatted_time)
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

