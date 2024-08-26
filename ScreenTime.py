from __future__ import print_function
import time
import json
import datetime
import win32gui
from dateutil import parser
import firebase_admin
from firebase_admin import credentials, db
import os
import re

class ActivityList:
    def __init__(self, activities):
        self.activities = activities
    
    def initialize_me(self, data):
        self.activities = self.get_activities_from_json(data)
    
    def get_activities_from_json(self, data):
        return_list = []
        activities = data.get('activities', [])
        for activity in activities:
            return_list.append(
                Activity(
                    name=activity['name'],
                    time_entries=self.get_time_entries_from_json(activity),
                )
            )
        return return_list
    
    def get_time_entries_from_json(self, data):
        return_list = []
        for entry in data.get('time_entries', []):
            return_list.append(
                TimeEntry(
                    start_time=parser.parse(entry['start_time']),
                    end_time=parser.parse(entry['end_time']),
                    days=entry['days'],
                    hours=entry['hours'],
                    minutes=entry['minutes'],
                    seconds=entry['seconds'],
                )
            )
        return return_list
    
    def serialize(self):
        return {
            'activities': self.activities_to_json()
        }
    
    def activities_to_json(self):
        activities_ = []
        for activity in self.activities:
            activities_.append(activity.serialize())
        return activities_

class Activity:
    def __init__(self, name, time_entries):
        self.name = name
        self.time_entries = time_entries

    def serialize(self):
        return {
            'name': self.name,
            'time_entries': self.make_time_entries_to_json()
        }
    
    def make_time_entries_to_json(self):
        time_list = []
        for time in self.time_entries:
            time_list.append(time.serialize())
        return time_list

class TimeEntry:
    def __init__(self, start_time, end_time, days, hours, minutes, seconds):
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = end_time - start_time
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    
    def _get_specific_times(self):
        self.days, self.seconds = self.total_time.days, self.total_time.seconds
        self.hours = self.days * 24 + self.seconds // 3600
        self.minutes = (self.seconds % 3600) // 60
        self.seconds = self.seconds % 60

    def serialize(self):
        return {
            'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end_time': self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'days': self.days,
            'hours': self.hours,
            'minutes': self.minutes,
            'seconds': self.seconds
        }

def get_active_window():
    _active_window_name = None
    window = win32gui.GetForegroundWindow()
    _active_window_name = win32gui.GetWindowText(window)
    return _active_window_name

def get_last_two_segments(title):
    # Remove leading numbers, spaces, and parentheses
    title = re.sub(r'^\(\d+\)\s*', '', title).strip()
    segments = title.split(' - ')
    if len(segments) >= 2:
        return ' - '.join(segments[-2:])
    return title

def get_data_ref(device_name):
    return db.reference(f'device/{device_name}')

def data_exists(device_name):
    ref = get_data_ref(device_name)
    return ref.get() is not None

def write_data(device_name, data):
    ref = get_data_ref(device_name)
    ref.set(data)

def save_to_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)

def load_from_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

cred = credentials.Certificate('screen-time-52e52-firebase-adminsdk-1aqkf-e11d87c05a.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://screen-time-52e52-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

device_name_file = 'DeviceName.json'

if not os.path.exists(device_name_file):
    print("DeviceName.json not found. Exiting.")
    exit()

data = load_from_json(device_name_file)
device_name = data['device_name']
password = data.get('password')

active_window_name = ""
activity_name = ""
start_time = datetime.datetime.now()
activeList = ActivityList([])
first_time = True

ref = get_data_ref(device_name)
data = ref.get()

if data and 'activities' in data:
    activeList.initialize_me(data)
else:
    activeList.activities = []

try:
    while True:
        previous_site = ""
        new_window_name = get_active_window()
        if 'Google Chrome' in new_window_name:
            new_window_name = get_last_two_segments(new_window_name)

        if active_window_name != new_window_name:
            print(active_window_name)
            activity_name = active_window_name

            if not first_time:
                end_time = datetime.datetime.now()
                time_entry = TimeEntry(start_time, end_time, 0, 0, 0, 0)
                time_entry._get_specific_times()

                exists = False
                for activity in activeList.activities:
                    if activity.name == activity_name:
                        exists = True
                        activity.time_entries.append(time_entry)

                if not exists:
                    activity = Activity(activity_name, [time_entry])
                    activeList.activities.append(activity)

                firebase_data = {
                    'password': password,
                    'activities': activeList.serialize()['activities']
                }
                write_data(device_name, firebase_data)
                    
                start_time = datetime.datetime.now()
            first_time = False
            active_window_name = new_window_name

        time.sleep(1)

except KeyboardInterrupt:
    firebase_data = {
        'password': password,
        'activities': activeList.serialize()['activities']
    }
    write_data(device_name, firebase_data)
