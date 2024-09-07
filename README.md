<h1 align="center">
  <a href="https://github.com/dec0dOS/amazing-github-template">
    <img src="img\TimeSpy Logo.png" alt="Logo">
  </a>
</h1>

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Set Up](#set-up)
  - [Running Program](#running-program)
- [Privacy Policy](#privacy-policy)
- [Authors](#authors)

</details>

---

# About

<table>
<tr>
<td>

Hello and welcome to TimeSpy, your go-to screentime tracking and visualization tool designed to bring clarity to employee activities in the digital workspace. Whether you're a company looking to boost productivity or an employer seeking to optimize workflow, TimeSpy is here to provide you with detailed insights into how screen time is being spent. By offering an intuitive platform that records, monitors, and visualizes screen activity, TimeSpy empowers organizations to track and analyze employee behavior, making it easier to identify patterns, enhance efficiency, and maintain accountability. Dive into the world of data-driven decision-making with TimeSpy, where every click tells a story!

</td>
</tr>
</table>

### Built With

<div >
	<img width="50" src="img\Python Logo.png" alt="Python" title="Python"/>
	<img width="50" src="img\Firebase logo.png" alt="FireBase" title="FireBase"/>
</div>

# Getting Started

### Prerequisites

To set up and run the TimeSpy, you need to install several Python libraries:

PyQt5 for the GUI.

```sh
git pip install PyQt5
```

firebase_admin for interacting with Firebase.

```sh
pip install firebase-admin
```

matplotlib for plotting graphs.

```sh
pip install matplotlib
```

numpy for numerical operations.

```sh
pip install numpy
```

python-dateutil for parsing dates.

```sh
pip install python-dateutil
```

pywin32 for Windows-specific functionality (e.g., working with window titles)

```sh
pip install pywin32
```

### Set Up

###### As Admin or Employer

1.Create new Real-Time Database in Firebase

<table>
<tr>
<td>
To set up Firebase Realtime Database, first, create a Firebase project at Firebase Console and enable the Realtime Database. Download the service account key (JSON) from the Firebase Console under Project Settings > Service Accounts, and place the key in your program folder
</td>
</tr>
</table>
2.Import JSON from Database.json to Firebase
<table>
<tr>
<td>
To import a JSON file, such as Database.json, into Firebase Realtime Database, go to the Firebase Console, navigate to the Realtime Database section, and click on the three dots in the top-right corner of the database window. Select Import JSON, then upload your Database.json file. Before importing, make sure to open the JSON file in a text editor and update the password field to whatever you prefer. Once the changes are made, save the file and proceed with the import to securely upload your data.
</td>
</tr>
</table>
3.Register the Firebase into the Program
<table>
<tr>
<td>
In this setup, the main program will prompt you with two input fields using line edits. The first line edit will ask for the relative path of your Firebase service account key (e.g., `firebase-key.json`), and the second will ask for the Firebase Realtime Database URL (e.g., `https://your-database-url.firebaseio.com/`). After filling in both fields, you click the **submit** button, and the program will capture these inputs to initialize the Firebase connection. The key and URL are essential for securely linking your program to the Firebase database and enabling real-time data interaction.
</td>
</tr>
</table>
4.Send the whole program folder to your employee
<table>
<tr>
<td>
To send the whole program folder to your employee, first navigate to the location where your program is stored on your computer. Copy the entire folder containing the program files, dependencies, and any required assets (like the Firebase key). Once copied, compress the folder into a .zip file to make it easier to share. After zipping, upload the compressed file to a cloud storage service, such as Google Drive, Dropbox, or any other file-sharing platform. Share the download link with your employee, allowing them to access and download the program from the cloud. This ensures the employee can easily access and run the program on their end.
</td>
</tr>
</table>

###### As Employee

1.Create new username

<table>
<tr>
<td>
After receiving and extracting the zip file, you need to run the program by executing main.py. The program will then prompt you to create a new username and password. If you already have a username from a previous device, you can bypass the creation process by clicking the text below "Create New Device" and entering your existing username and password. After entering your credentials, click "Login in New Device" to access the program with your previous account details.
</td>
</tr>
</table>
2.Make the program starts automatically after the device boots up.

<table>
<tr>
<td>
To schedule `ScreenTime.pyw` to run every time Windows boots up using Task Scheduler, start by opening Task Scheduler (search for it in the Start menu). Click on "Create Task" in the Actions pane. In the "General" tab, name your task (e.g., "ScreenTime Launch") and select "Run with highest privileges" if needed. Go to the "Triggers" tab, click "New...", and choose "At startup" to set the task to trigger when Windows starts. Next, in the "Actions" tab, click "New..." and select "Start a program" as the action. In the "Program/script" field, enter the path to your Python interpreter (e.g., `C:\Python39\pythonw.exe`), which runs Python scripts without opening a console window. In the "Add arguments" field, input the full path to your `ScreenTime.pyw` script (e.g., `C:\Scripts\ScreenTime.pyw`). Click "OK" to save each dialog. This setup ensures that `ScreenTime.pyw` runs automatically every time Windows boots up.
</td>
</tr>
</table>
3.Restart your device

<table>
<tr>
<td>
Once you’ve configured your program to start automatically after the device boots up, you need to restart your device to ensure that the program initializes correctly. This restart will allow the operating system to execute the startup settings you’ve applied, ensuring that the program launches as intended each time the device is powered on.
</td>
</tr>
</table>

### Running Program

<table>
<tr>
<td>

To run the TimeSpy program, you need to start by executing the main.py script. Upon launching the program, you will be prompted to enter your username and password. If you are a regular user, simply log in with your credentials to access the user view.

For those requiring admin access, enter "admin" as the username and the admin password that already been set in the first place. This will grant you access to the admin view, where you can configure various settings. In the admin view, you can select the username for which you wish to generate a graph. You will also need to set the start and end dates for the graph. Once these parameters are set, click on "Generate Graph" to display the requested graph.

In the user view, you can also set the start and end dates and then click "Generate Graph" to produce the graph for your activities. Additionally, after setting the dates, you can choose which specific graph to display by selecting from the buttons above the "Generate Graph" button. To view a detailed list of activities, simply click on "View Activity Details."

</td>
</tr>
</table>

# Features

### Admin View (for employer)

By log in as Admin, you can access to other employee by enter their username and then **visualize the data with graph.**

<details>

  <summary>User Interface</summary>
  
<img src="img\Admin.jpg" alt="Admin UI">

</details>

### User View (for employee)

By log in with your username, you can access to your own data then **visualize the data with graph.**

<details>
<summary>User Interface</summary>
  
<img src="img\User.jpg" alt="User UI">

</details>

### Data Visualization with Graphs

After log in, you can set the time range to select data to be visualize by enter start date and end date **The graph will appear after you click the Generate Graph button.**

<details>
<summary>User Interface</summary>
  
<img src="img\Graph 1.jpg" alt="Graph 1">
<img src="img\Graph 2.jpg" alt="Graph 2">

</details>

### Activities List

After generate the graph, you can access to detailed activities list **in time range that already set** by clicking "View Activity Details" under Generate Graph button.

<details>
<summary>User Interface</summary>
  
<img src="img\Activity List.jpg" alt="Activity List">

</details>

## Privacy Policy

At TimeSpy, your privacy is important to us. We want to ensure that your data remains secure and under your control. TimeSpy does not collect, store, or transmit any personal data from its users. The database used by the program is created and managed solely by the admin or employer, giving them full control over the information stored within it. TimeSpy operates purely as a tool to assist in time tracking without accessing or processing any of your data externally.

## Authors

<details>
<summary>Attafahqi Amirtha Dariswan</summary>

- **Backend Development:** Implement functionality to gather screen time data.
- **Login Feature:** Design and develop the UI, frontend, and backend for the login functionality.
- **Admin and User Views:** Develop the frontend for both admin and user views.
- **Activity and Time Graphs:** Create a program to generate graphs for activities and total time.

</details>

<details>
<summary>Puti Nabilah</summary>
  
- **Backend Development:** Implement functionality to gather screen time data.
- **Activity List:** Develop both the frontend and backend for managing the activity list.
- **Total Time Calculation:** Create a program to calculate the total time spent on activities.
- **Donut Chart:** Implement a program to generate a donut chart displaying the percentage of time used.

</details>
<details>
<summary>Ferdinand Sumichael Sunan</summary>

</details>
