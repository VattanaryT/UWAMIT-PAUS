'''
Vattanary Tevy - created 11/14/2024
User interface for Angle Alignment of BMS60 motor controller

The user interface includes a table with 21 columns and 3 rows:
1. "Triggers" row (fixed labels from 1-20),
2. "Degrees" row (automatically calculated from Counts),
3. "Counts" row (editable by the user).

What the UI does:
- Allows the user to input counts for triggers in a dedicated input box.
- Automatically updates the Degrees row based on a formula.

Notes for user:
- Enter counts within the range -20000 to 20000.
- Input supports up to 2 decimal places.
'''

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import automation1 as a1
import numpy as np

AnglesAligned = 'UserAngleAlignment.txt'
coordinated_speed = 400

controller = None

def log_message(message):
    error_display.insert(tk.END, message + "\n")
    error_display.see(tk.END)  # Auto-scroll to the bottom

# Function to clear the error display
def clear_error_display():
    error_display.delete(1.0, tk.END)

def update_degree_entry(index):
    try:
        count_value = usercount_entries[index].get()  # Get the current value in the Count entry
        if count_value.strip():  # Only process non-empty values
            count_value = float(count_value)
            degrees_value = round((count_value * 360) / 20000, 2)  # Perform the conversion
            degree_entries[index].config(state="normal")
            degree_entries[index].delete(0, tk.END)
            degree_entries[index].insert(0, str(degrees_value))
            degree_entries[index].config(state="readonly")
        else:
            degree_entries[index].config(state="normal")
            degree_entries[index].delete(0, tk.END)
            degree_entries[index].config(state="readonly")
    except ValueError:
        degree_entries[index].config(state="normal")
        degree_entries[index].delete(0, tk.END)
        degree_entries[index].config(state="readonly")

# Function to handle cell selection
# def set_selected_cell(index):
#     count_entries.delete(0, tk.END)
#     count_entries.insert(0, count_entries[index].get())
#     global selected_column
#     selected_column = index

# # Function to save the value from the entry field to the Counts row
# def save_value():
#     value = count_entries.get()
#     count_entries[selected_column].delete(0, tk.END)
#     count_entries[selected_column].insert(0, value)
#     update_degrees()

# Ensure valid input in the entry field
def validate_entry(new_value):
    if new_value == "" or new_value == "-" or new_value == "." or new_value == "-.":
        return True
    
    try:
        value = int(new_value)
        if -20000 <= value <= 20000:  # Valid range
            # Check for up to 2 decimal places
            parts = new_value.split(".")
            if len(parts) == 1 or (len(parts) == 2 and len(parts[1]) <= 2):
                return True
    except ValueError:
        pass
    return False

#enable user to modify inputs
def edit_button():
    for entry in usercount_entries:
        entry.config(state='normal')
    # speed_entry.config(state='normal')
    # starttrigger_button.config(state='disabled')
    set_button.config(state="normal")
    edit_button.config(state="disabled")
    log_message(f"Edit mode enabled")

#save user's input into file
# def record():
#     global user_counts, controller
#     user_counts = [int(entry.get()) if entry.get().strip() else 0.0 for entry in usercount_entries]
#     # speed_value = int(speed_entry.get()) if speed_entry.get().isdigit() else 0
#     for entry in usercount_entries:
#         entry.config(state='readonly')
#     # speed_entry.config(state='readonly')
#     # starttrigger_button.config(state='normal')
#     set_button.config(state="disabled")
#     edit_button.config(state="normal")

def record():
    global user_counts, controller
    try:
        # Collect user counts from the entry widgets
        user_counts = [entry.get().strip() if entry.get().strip() else "0" for entry in usercount_entries]
        # Convert the list to a comma-separated string
        file_content = ",".join(user_counts)
        
        # Write to the controller file
        controller.files.write_text(AnglesAligned, file_content)
        
        # Set entries to readonly
        for entry in usercount_entries:
            entry.config(state='readonly')
        
        # Update button states
        set_button.config(state="disabled")
        edit_button.config(state="normal")
        
        log_message(f"Counts saved to {AnglesAligned}: {user_counts}")
    except Exception as e:
        log_message(f"Error saving counts: {str(e)}")


#load user inputs onto user interface
def load():
    global controller
    if controller is None:
        try:
            controller = a1.Controller.connect_usb()
            controller.start()
        except Exception as e:
            log_message(f"Failed to connect to controller: {str(e)}")
            return [0] * 20  # Return default list of zeros on failure
    
    try:
        # Read the file from the controller
        counts_str = controller.files.read_text(AnglesAligned).strip()  # Read and strip extra spaces/newlines
        # Convert the comma-separated string to a list of integers
        counts_list = list(map(int, counts_str.split(',')))
        counts_array = np.array(counts_list)

        counts = np.round(counts_array, 2)
        log_message(f"Loaded counts: {counts_list}")
        return counts
    except FileNotFoundError:
        log_message(f"File '{AnglesAligned}' not found. Loading default values.")
        # return [0] * 20  # Return default list of zeros
    except Exception as e:
        log_message(f"Error reading file '{AnglesAligned}': {str(e)}")
        # return [0] * 20  # Return default list of zeros on failure

def update_degrees():
    for i in range(0, 20):  # Update columns 1-20
        count_value = usercount_entries[i].get()
        if count_value.strip():  # Only process non-empty values
            try:
                count_value = float(count_value)
                degrees_value = round((count_value * 360) / 20000, 2)  # Conversion
                degree_entries[i].config(state="normal")
                degree_entries[i].delete(0, tk.END)
                degree_entries[i].insert(0, str(degrees_value))
                degree_entries[i].config(state="readonly")
            except ValueError:
                degree_entries[i].config(state="normal")
                degree_entries[i].delete(0, tk.END)
                degree_entries[i].config(state="readonly")
        else:
            degree_entries[i].config(state="normal")
            degree_entries[i].delete(0, tk.END)
            degree_entries[i].config(state="readonly")

def initialize_ui():
    try:
        controller = a1.Controller.connect_usb()
        controller.runtime.commands.motion.enable(['Theta'])
        controller.start()
        loaded_counts = load()  # Load counts from the file
        for i, value in enumerate(loaded_counts):
            if i < len(usercount_entries):  # Ensure we don't exceed the number of widgets
                usercount_entries[i].delete(0, tk.END)
                usercount_entries[i].insert(0, str(value))
        update_degrees()  # Recalculate the Degrees row based on loaded counts
        log_message("UI initialized with loaded counts.")
    except Exception as e:
        log_message(f"Error initializing UI: {str(e)}")
        
    #disable button initially
    # starttrigger_button.config(state='normal')
    # stoptrigger_button.config(state='disabled')

def home():
    controller.runtime.commands.motion.home(['Theta'])
    log_message("Motor homed")

def move_position():
    try:
        # Extract value from move_entry and convert it to integer
        move_value = int(move_entry.get())
        # Send the move command
        controller.runtime.commands.motion.home(['Theta'])
        controller.runtime.commands.motion.movelinear(['Theta'], [move_value], coordinated_speed)
        log_message(f"Motor moved to: {move_value}")
    except ValueError:
        log_message("Invalid input for motor position. Please enter a valid number.")
    except Exception as e:
        log_message(f"Failed to move motor: {str(e)}")

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

# Create the main window
window = tk.Tk()
window.geometry('1220x470')
window.title('Angle Alignment')
window.resizable(False, False)

# Label for table header
header_label = tk.Label(window, text="Triggers", font=("Arial", 11, "bold"), anchor="center")
header_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
for i in range(1, 21):
    header = tk.Label(window, text=f"{i}", font=("Arial", 11, "bold"), anchor="center", relief="ridge")
    header.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

# Create Degrees row
degree_entries = []
degrees_label = tk.Label(window, text="Degrees", font=("Arial", 10), anchor="center")
degrees_label.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
for i in range(1, 21):
    degree_entry = tk.Entry(window, font=("Arial", 9), width=7, state="readonly", justify="center", relief="ridge")
    degree_entry.grid(row=1, column=i, padx=2, pady=2, sticky="nsew")
    degree_entries.append(degree_entry)

# Create Counts row
usercount_entries = []
count_entries = tk.Label(window, text="Counts", font=("Arial", 10), anchor="center")
count_entries.grid(row=2, column=0, padx=1, pady=1, sticky="nsew")

# Validation function
vcmd = (window.register(validate_entry), '%P')

for i in range(1, 21):
    count_entry_widget = tk.Entry(window, font=("Arial", 9), width=5, justify="center", relief="ridge", validate="key", validatecommand=vcmd)
    count_entry_widget.grid(row=2, column=i, padx=1, pady=1, sticky="nsew")
    
    # Bind the KeyRelease event to update the corresponding Degree entry
    count_entry_widget.bind('<KeyRelease>', lambda e, idx=i-1: update_degree_entry(idx))
    
    usercount_entries.append(count_entry_widget)

# Label and Entry field for Counts
count_label = tk.Label(window, text="Move motor to count:", font=("Arial", 11))
count_label.place(x=120, y=250)
move_entry = tk.Entry(window, width=10, validate='key', validatecommand=vcmd)
move_entry.place(x=270, y=250)

# Button to save the value
move_button = tk.Button(window, text="Enter", command=move_position)
move_button.place(x=350, y=245)

#set and edit buttons
set_button = tk.Button(window, text="SET", command=record)
set_button.place(x=100, y=110)
edit_button = tk.Button(window, text="EDIT", command=edit_button)
edit_button.place(x=200, y=110)

#home and reset motor buttons
home_button = tk.Button(window, text='Go to Home Position', command=home, bg='dark green', fg='white')
home_button.place(x=900, y=110)
reset_button = tk.Button(window, text="Reset", command=reset_controller, bg='dark orange', fg='white')
reset_button.place(x=1100, y=110)

# Error display section
event_label = tk.Label(window, text="Event Logs", font=("Arial", 11))
event_label.place(x=700, y=170)
error_display_frame = tk.Frame(window)
error_display_frame.place(x=700, y=200, width=450, height=220)
error_display = ScrolledText(error_display_frame, wrap=tk.WORD, height=10, width=100)
error_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
clear_button = tk.Button(window, text="Clear", command=clear_error_display)
clear_button.place(x=700, y=430)

initialize_ui()

# Run the GUI loop
window.mainloop()