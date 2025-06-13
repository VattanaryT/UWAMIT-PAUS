'''
Vattanary Tevy - created 07/23/2024
User interface for BMS60 motor controller

Running this program initiates a user interface for the Aerotech BMS60 motor. It includes entries for the user's 
desired speed and fiber angles, a "Start Motor", "Stop Motor", and "Reset" button for the motor itself, buttons to download the Machine Controller Definition (MCD) files, 
and a section to log messages or errors for the user.

Notes: 
- External files include Aerosciprt files to start and stop position synchronized outputs (PSO) to send triggers, as
well as the MCD file.
- The "Start Motor" and "Stop Motor" buttons will automatically start triggering (from the first fiber)
'''

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure
import automation1 as a1
import numpy as np
import os
import socket
import threading

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(DESKTOP_PATH, 'Motor_PSOtrigger')

#paths for each file using the base directory
FOLDER_PATH = os.path.join(BASE_DIR, 'Motor_PSOtrigger')
PSO_FILE = 'psoscript2.ascript'
STOP_PSO_FILE = 'StopPso.ascript'
MCD = os.path.join(FOLDER_PATH, 'StepperMotorPSO.MCD')

controller = None   #global variable

server_thread = None
server_socket = None

# Create the event object that will be used as a flag
stop_event = threading.Event()

def start_server():
    global server_thread
    global stop_event
    server_thread = threading.Thread(target=run_server, args=(stop_event,))
    server_thread.start()
    log_message(f"Server started...\n")

def stop_server():
    global server_socket
    global server_thread
    global stop_event
    stop_event.set()  # Set the flag to stop the loop
    if server_socket:
        server_socket.close()
        #log_message(f"Server stopped...\n")
    #server_thread.join()

def run_server(stop_event):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 65432))
    server_socket.listen(1)
    log_message("Waiting for a connection...\n")

    while not stop_event.is_set():
        try:
            conn, addr = server_socket.accept()
            log_message(f"Connected by {addr}\n")
            while not stop_event.is_set():
                data = conn.recv(1024)
                if not data:
                    break
                client_message = data.decode()
                log_message(f"Received from client: {client_message}\n")
                conn.sendall(b"ACK")
                if client_message == "starttrigger":
                    starttrigger()
                elif client_message == "stoptrigger":
                    stoptrigger()
            conn.close()
        except socket.error:
            break

def log_message(message):
    error_display.insert(tk.END, message + "\n")
    error_display.see(tk.END)  #auto-scroll to the bottom

#function to clear the error display
def clear_error_display():
    error_display.delete(1.0, tk.END)

def upload_mcd():
    global controller
    try:
        controller = a1.Controller.connect_usb()
        
        controller.upload_mcd_to_controller(MCD, True, True, False)

        log_message(f"Configuration loaded from {MCD} successfully.")
    except Exception as e:
        log_message(f"Failed to load configuration: {e}")

def download_mcd():
    global controller
    try:
        controller = a1.Controller.connect_usb()
        
        controller.download_mcd_to_file(MCD, True, True)

        log_message(f"Downloaded MCD File successfully: {MCD}.")
    except Exception as e:
        log_message(f"Failed to download configuration: {e}")

#ensure user enters an angle
def validate_entry(new_value):
    if new_value == "":
        return True  
    if new_value == "-":
        return True 
    if new_value == ".":
        return True  
    if new_value == "-.":
        return True
    
    try:
        value = float(new_value)
        # Check if the value is between -360 and 360 and has up to 2 decimal places
        if -360 <= value <= 360:
            # Split the value to check the decimal places
            parts = new_value.split(".")
            if len(parts) == 1 or (len(parts) == 2 and len(parts[1]) <= 2):
                return True
        return False
    except ValueError:
        return False
    
def validate_speed(new_value):
    if new_value == "":
        return True 
    try:
        value = int(new_value)
        return 0 <= value <= 50  #set limit to 0 to 50 Hz
    except ValueError:
        return False

#enable user to modify inputs
def edit_button():
    for entry in entries:
        entry.config(state='normal')
    speed_entry.config(state='normal')
    starttrigger_button.config(state='disabled')
    set_button.config(state="normal")
    edit_button.config(state="disabled")
    log_message(f"Edit mode enabled")

#save user's input into file
# def record():
#     global user_angles, controller
#     user_angles = [float(entry.get()) * 20000 / 360 if entry.get() else 0 for entry in entries]
#     # speed_value = int(speed_entry.get()) if speed_entry.get().isdigit() else 0
#     for entry in entries:
#         entry.config(state='readonly')
#     speed_entry.config(state='readonly')
#     starttrigger_button.config(state='normal')
#     set_button.config(state="disabled")
#     edit_button.config(state="normal")

#     controller.runtime.commands.motion.enable(['Theta'])

def record():
    global user_angles, controller
    try:
        # Validate and collect user angles and speed
        user_angles = [float(entry.get()) if entry.get().strip() else 0.0 for entry in entries]
        user_speed = speed_entry.get().strip()

        # Validate speed entry
        if not user_speed.isdigit() or int(user_speed) < 0 or int(user_speed) > 50:
            log_message("Invalid speed. Please enter a value between 0 and 50 Hz.")
            return

        # Convert angles to counts for saving
        user_counts = [angle * 20000 / 360 for angle in user_angles]
        
        # Write speed and counts to files
        controller.files.write_text("UserSpeed.txt", user_speed)
        controller.files.write_text("UserPosition.txt", ",".join(map(str, user_counts)))
        
        # Set entries to readonly
        for entry in entries:
            entry.config(state='readonly')
        speed_entry.config(state='readonly')
        
        # Update button states
        starttrigger_button.config(state='normal')
        set_button.config(state="disabled")
        edit_button.config(state="normal")
        
        log_message(f"Speed saved to UserSpeed.txt: {user_speed}")
        log_message(f"Positions saved to UserPosition.txt: {user_counts}")
    except Exception as e:
        log_message(f"Error saving settings: {str(e)}")

#load user inputs onto user interface
# def load_settings():
#     global controller
#     if controller is None:
#         try:
#             controller = a1.Controller.connect_usb()
#             controller.start()
#         except Exception as e:
#             log_message(f"Failed to connect to controller: {str(e)}")
#             return [], ''  # Return empty defaults on failure

#     try:
#         # Read speed and distance from text files
#         speed = controller.files.read_text("UserSpeed.txt").strip()  # Read speed as a string and strip any whitespace
#         distances_str = controller.files.read_text("UserPosition.txt").strip()

#         # Convert distances (angles) from comma-separated string to a list of integers
#         positions = list(map(float, distances_str.split(',')))

#         # Use numpy for element-wise operations
#         positions_array = np.array(positions)
#         angles = positions_array / 20000 * 360

#         angles = np.round(angles, 2)

#         return angles, speed  # Convert back to a list for further use

#     except Exception as e:
#         log_message(f"Error reading files: {str(e)}")
#         return [], ''  # Return empty values on failure

def load_settings():
    global controller
    try:
        # Connect to the controller if not already connected
        if controller is None:
            controller = a1.Controller.connect_usb()
            controller.start()

        # Read speed and positions from files
        speed = controller.files.read_text("UserSpeed.txt").strip()
        positions_str = controller.files.read_text("UserPosition.txt").strip()

        # Convert comma-separated positions to angles
        positions = list(map(float, positions_str.split(',')))
        angles = [pos * 360 / 20000 for pos in positions]

        log_message(f"Loaded speed: {speed}")
        log_message(f"Loaded positions: {angles}")
        
        return angles, speed
    except FileNotFoundError:
        log_message("Settings files not found. Loading default values.")
        return [], ''  # Default values
    except Exception as e:
        log_message(f"Error loading settings: {str(e)}")
        return [], ''  # Default values

# def initialize_ui():
#     global controller
#     controller = a1.Controller.connect_usb()
#     controller.start()
#     angles, speed = load_settings()
#     for i, angle in enumerate(angles):
#         if i < len(entries):
#             entries[i].delete(0, tk.END)
#             entries[i].insert(0, str(angle))
#     if speed:  
#         speed_entry.delete(0, tk.END)
#         speed_entry.insert(0, str(speed))  #insert speed as is (as a string)
#     else:
#         log_message("No speed loaded or speed is zero.")
        
#     #disable button initially
#     starttrigger_button.config(state='normal')
#     stoptrigger_button.config(state='disabled')

def initialize_ui():
    global controller
    try:
        controller = a1.Controller.connect_usb()
        controller.start()
        angles, speed = load_settings()
        
        # Populate entries with loaded values
        for i, angle in enumerate(angles):
            if i < len(entries):
                entries[i].delete(0, tk.END)
                entries[i].insert(0, str(angle))
        if speed:
            speed_entry.delete(0, tk.END)
            speed_entry.insert(0, str(speed))
        else:
            log_message("No speed loaded. Defaulting to 0.")
        
        # Set initial button states
        starttrigger_button.config(state='normal')
        stoptrigger_button.config(state='disabled')
        set_button.config(state="disabled")
    except Exception as e:
        log_message(f"Error initializing UI: {str(e)}")
    
def run_script():
    global controller
    try:
        controller = a1.Controller.connect_usb()  
        if not controller.is_running:
            raise Exception("Controller connection failed.")
        
        # load and run the AeroScript program
        controller.runtime.tasks[1].program.run(PSO_FILE)
    
    except Exception as e:
        log_message(f"Failed to start the script: {str(e)}")

def starttrigger():
    global controller
    if controller and controller.is_running:
        controller.runtime.commands.motion.enable(['Theta'])
        # controller.runtime.commands.motion.home(['Theta'])
        run_script()  #run the AeroScript program when the trigger is started
        log_message("Trigger started.")
        starttrigger_button.config(state='disabled')
        stoptrigger_button.config(state='disabled')
        edit_button.config(state='disabled')
        stoptrigger_button.after(17000, lambda: stoptrigger_button.config(state='normal'))
    else:
        log_message("Cannot start trigger: Motor is not running.")

def stoptrigger():  #trigger command is in separate (AeroScript) stop-trigger file
    try:
        controller.runtime.tasks[1].program.run(STOP_PSO_FILE)
        # controller.disconnect()
        log_message("Trigger stopped.")

        starttrigger_button.config(state='normal')
        edit_button.config(state='normal')
        
    except Exception as e:
        log_message(f"Failed to stop the AeroScript: {e}")

def emergency_stop():
    log_message("Emergency stop initiated.")
    try:
        if controller and controller.is_running:
            controller.runtime.commands.motion.movefreerunstop('Theta')
            controller.runtime.commands.motion.disable(['Theta'])
            controller.disconnect()
            log_message("Motor stopped.")
    except Exception as e:
        log_message(f"Failed to stop the motor: {e}")

def on_closing():
    #call emergency stop before closing
    emergency_stop()
    #close the window
    window.destroy()
    stop_server()

def reset_controller():
    try:
        if controller and controller.is_running:
            controller.reset()
            log_message("Controller has been reset.")
    except Exception as e:
        log_message(f"Failed to reset")

'''
window setup
'''

window = tk.Tk()
window.geometry('1000x450')
window.title('Motor Controller')
window.resizable(False, False)

vcmd = (window.register(validate_entry), '%P')
vcmd2 = (window.register(validate_speed), '%P')

total_columns = 21
column_width = 1000 // total_columns
columns = ['Triggers'] + [str(i) for i in range(1, 21)]
table = ttk.Treeview(window, columns=columns, show='headings')
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=column_width)
table.insert('', 'end', values=['Degrees'] + ['' for _ in range(20)])
table.pack(expand=True, fill='both')

entries = [tk.Entry(window, width=7, validate='key', validatecommand=vcmd) for _ in range(20)]
for i, entry in enumerate(entries):
    entry.place(x=(column_width * (i + 1)) + 15, y=27)

MCD_value = 'motor1'

#MCD file
download_button = tk.Button(window, text="Download MCD File", command=download_mcd, font=("Arial", 11))  
download_button.place(x=30, y=390)
upload_button = tk.Button(window, text="Upload MCD File", command=upload_mcd, font=("Arial", 11))
upload_button.place(x=200, y=390)

#speed_entry
speed_entry = tk.Entry(window, width=5, validate='key', validatecommand=vcmd2)
speed_entry.place(x=50, y=200)

#set and edit buttons
set_button = tk.Button(window, text="SET", command=record)
set_button.place(x=100, y=70)
edit_button = tk.Button(window, text="EDIT", command=edit_button)
edit_button.place(x=200, y=70)

#reset motor button
reset_button = tk.Button(window, text="Reset", command=reset_controller, bg='dark orange', fg='white')
reset_button.place(x=900, y=70)

#labels
speed_label = tk.Label(window, text="Speed (Hz) - Max: 50 Hz", font=("Arial", 11))
speed_label.place(x=20, y=170)
mcd_label = tk.Label(window, text="Machine Controller Definition (MCD) File", font=("Arial", 11))
mcd_label.place(x=20, y=350)
event_label = tk.Label(window, text="Event Logs", font=("Arial", 11))
event_label.place(x=400, y=120)

#start and stop trigger buttons
starttrigger_button = tk.Button(window, text="START MOTOR", command=starttrigger, bg='green', fg='white')
starttrigger_button.place(x=690, y=70)
stoptrigger_button = tk.Button(window, text="STOP MOTOR", command=stoptrigger, bg='red', fg='white')
stoptrigger_button.place(x=790, y=70)

save_data = False
user_angles = []

#clear messages
clear_button = tk.Button(window, text="Clear", command=clear_error_display)
clear_button.place(x=400, y=405)

#error display section
error_display_frame = tk.Frame(window)
error_display_frame.place(x=400, y=150, width=570, height=250)

error_display = ScrolledText(error_display_frame, wrap=tk.WORD, height=10, width=100)
error_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#bind the close event to call the emergency stop
window.protocol("WM_DELETE_WINDOW", on_closing)

#automatically initialize UI after running program
initialize_ui()

#start server
start_server()

window.mainloop()
