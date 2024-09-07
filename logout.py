import os
import subprocess

def stop_process(process_name):
    try:
        
        result = subprocess.check_output(f'tasklist | findstr {process_name}', shell=True).decode()
       
        if process_name in result:
            pid = int(result.split()[1])  
            subprocess.call(['taskkill', '/PID', str(pid), '/F'])  
            print(f"Terminated {process_name} with PID {pid}")
            return True
    except subprocess.CalledProcessError:
        return False

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted.")
    else:
        print(f"{file_path} not found.")

def main():
    process_name = 'ScreenTime.pyc'  # 
    json_file_path = 'DeviceName.json' 

    if stop_process(process_name):
        print(f"{process_name} stopped successfully.")
    else:
        print(f"Could not find {process_name} running.")

    delete_file(json_file_path)

if __name__ == "__main__":
    main()

