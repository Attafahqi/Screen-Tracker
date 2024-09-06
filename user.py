import os
import json
import matplotlib.pyplot as plt
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDesktopWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate
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
    num_days = (end_date - start_date).days
    if num_days > 30 :
        show =  7
    if num_days > 7 :
        show = 3
    else :
        show = 1

    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    activities = set()
    for day_data in data.values():
        activities.update(day_data.keys())

    app_usage = []
    for activity in activities:
        total_time = sum(data.get(date, {}).get(activity, timedelta()).total_seconds() for date in dates)
        app_usage.append({
            "activity": activity,
            "total_time_seconds": total_time
        })

    top_activities = sorted(activities, key=lambda a: sum(
        data.get(date, {}).get(a, timedelta()).total_seconds() for date in dates
    ), reverse=True)[:10]

    fig1, ax1 = plt.subplots()

    for activity in top_activities:
        hours = [data.get(date, {}).get(activity, timedelta()).total_seconds() / 3600 for date in dates]
        ax1.plot(dates, hours, label=activity)

    ax1.set_xlabel('Date', color='white')
    ax1.set_ylabel('Hours per Activity', color='white')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=show))  # Customize 'show' for date intervals
    fig1.autofmt_xdate()

    ax1.set_facecolor('white')
    ax1.tick_params(axis='both', colors='white')
    ax1.spines['top'].set_edgecolor('white')
    ax1.spines['right'].set_edgecolor('white')
    ax1.spines['bottom'].set_edgecolor('white')
    ax1.spines['left'].set_edgecolor('white')

    plt.savefig('UI/user_graph.png', bbox_inches='tight', dpi=300, transparent=True)

    handles, labels = ax1.get_legend_handles_labels()
    fig_legend = plt.figure(figsize=(4, 2))
    fig_legend.legend(handles, labels, loc='center', fontsize=6)
    fig_legend.gca().axis('off')
    fig_legend.savefig('Ui/user_legend.png', bbox_inches='tight', dpi=300, transparent=True)

    total_usage = []
    for date in dates:
        total_time = sum(data.get(date, {}).get(activity, timedelta()).total_seconds() for activity in data.get(date, {}))
        total_usage.append(total_time / 3600)  # Convert seconds to hours

    fig2, ax2 = plt.subplots()

    ax2.plot(dates, total_usage, label='Total Activity Time', color='cyan')

    ax2.set_xlabel('Date', color='white')
    ax2.set_ylabel('Total Hours', color='white')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=show))
    fig2.autofmt_xdate()

    ax2.set_facecolor('white')
    ax2.tick_params(axis='both', colors='white')
    ax2.spines['top'].set_edgecolor('white')
    ax2.spines['right'].set_edgecolor('white')
    ax2.spines['bottom'].set_edgecolor('white')
    ax2.spines['left'].set_edgecolor('white')

    plt.savefig('UI/user_graph2.png', bbox_inches='tight', dpi=300, transparent=True)


    total_time_per_activity = {}
    for activity in activities:
        total_time = sum(data.get(date, {}).get(activity, timedelta()).total_seconds() for date in dates)
        total_time_per_activity[activity] = total_time

    total_time_seconds = int(sum(total_time_per_activity.values()))
    total_inactive_time_seconds = ((num_days + 1) * 86400) - total_time_seconds
    percentage = f"{total_time_seconds * 100 / ((int(num_days) + 1) * 86400):.2f}%" 
    
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

    return formatted_time, num_days, app_usage

class User (QMainWindow):
    def __init__(self):
        super(User, self).__init__()
        uic.loadUi("UI/user.ui", self)
        self.center()
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        today = QDate.currentDate()
        self.EndDate.setDate(today)
        seven_days_ago = today.addDays(-7)
        self.StartDate.setDate(seven_days_ago)
        self.show()

        self.DeviceName.setText(device_name)
        self.Generate.clicked.connect(self.admin)
        self.Exit.clicked.connect(self.quit)
        self.TotalTimeButton.clicked.connect(self.total_time)
        self.Top10Button.clicked.connect(self.top_ten)
        self.Details.setHidden(True)
        self.TotalTimeButton.setHidden(True)
        self.Top10Button.setHidden(True)
        self.Graph_3.setHidden(True)

    def top_ten(self):
        self.TotalTimeButton.setHidden(False)
        self.Top10Button.setHidden(True)
        self.Graph_3.setHidden(True)
        self.Graph.setHidden(False)
        self.Legend.setHidden(False)

    def total_time(self):
        self.TotalTimeButton.setHidden(True)
        self.Top10Button.setHidden(False)
        self.Graph_3.setHidden(False)
        self.Graph.setHidden(True)
        self.Legend.setHidden(True)

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
        formatted_time, num_days, app_usage = generate_graphs(data, start_date, end_date)
        self.Graph.setStyleSheet(f"border-image: url(UI/user_graph.png);")
        self.Graph.repaint()
        self.Legend.setStyleSheet(f"border-image: url(UI/user_legend.png);")
        self.Legend.repaint()
        self.Graph_2.setStyleSheet(f"border-image: url(UI/user_donutchart.png);")
        self.Graph_2.repaint()
        self.Graph_3.setStyleSheet(f"border-image: url(UI/user_graph2.png);")
        self.Graph.repaint()
        self.TotalText.setText("Total Screen Time in " + str(num_days+1) + " days")
        self.TotalTime.setText(formatted_time)
        data = 0

        self.TotalTimeButton.setHidden(False)
        self.Details.setHidden(False)
        self.Details.clicked.connect(self.details)
    
    def details(self):
        start_date_qt = self.StartDate.date()  
        end_date_qt = self.EndDate.date()     
        start_date = start_date_qt.toPyDate() 
        end_date = end_date_qt.toPyDate()

        if start_date >= end_date:
            self.show_popup_message("Start date must be before to end date.")
            return

        activities = get_data_from_firebase(device_name, start_date, end_date)

        data = aggregate_data(activities, start_date, end_date)

        self.details_window = DetailsWindow(data, start_date, end_date)
        self.details_window.show()

    def show_popup_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

class DetailsWindow(QMainWindow):
    def __init__(self, data, start_date, end_date):
        super(DetailsWindow, self).__init__()
        uic.loadUi("UI/details.ui", self)
        self.center()
        self.setWindowTitle("FAP TimeSpy")
        self.setWindowIcon(QIcon("UI/FAP Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Store the data to use in the details window
        self.data = data
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_label_2.setText(start_date.strftime("%Y-%m-%d"))
        self.end_date_label_2.setText(end_date.strftime("%Y-%m-%d"))

        # Generate table
        self.tableWidget.setColumnWidth(0,600)
        self.tableWidget.setColumnWidth(1,270)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        formatted_time, num_days, app_usage = generate_graphs(self.data, self.start_date, self.end_date)
        self.loaddata(app_usage)

        self.Exit.clicked.connect(self.quit)
        self.BacktoGenerate.clicked.connect(self.backtogenerate)

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def quit(self):
        QApplication.quit()

    def backtogenerate(self):
        self.hide()

    def loaddata(self, app_usage):
        app_usage_sorted_indices = np.argsort([-item['total_time_seconds'] for item in app_usage])
        app_usage_sorted = [app_usage[i] for i in app_usage_sorted_indices]

        def format_duration(seconds):
            seconds = int(seconds)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            
            parts = []
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            if seconds > 0 or not parts:  # Always show seconds if there are no hours and minutes
                parts.append(f"{seconds}s")
            
            return ' '.join(parts) 

        row=0
        self.tableWidget.setRowCount(len(app_usage_sorted))
        for item in app_usage_sorted:
            activity_item = QTableWidgetItem(item['activity'])
            activity_item.setFlags(activity_item.flags() & ~Qt.ItemIsEditable)
            time_seconds = item['total_time_seconds']
            formatted_time = format_duration(time_seconds)
            self.tableWidget.setItem(row, 0, activity_item)
            time_item = QTableWidgetItem(formatted_time)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row, 1, time_item)
            row = row + 1
            
if __name__ == "__main__":
    if not os.environ['DEVICE_NAME'] :
         QApplication.quit()

    initialize_firebase()
    app = QApplication([])
    window = User()
    app.exec_()

