
import tkinter as tk
import socket
import time

# Drone IP and command port
drone_ip = "192.168.1.1"
command_port = 5556

# Initialize the command socket
sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq = 1
start = 0

def send_command(command):
    """Send AT command to the drone and increment sequence number."""
    global seq
    sock_command.sendto(command.encode(), (drone_ip, command_port))
    seq += 1

# Emergency stop command function
def emergency_stop():
    global start
    stop_command = f"AT*REF={seq},290717952\r"  # Emergency stop command
    send_command(stop_command)
    print("Emergency stop command sent!")
    end = time.time()
    print("Flight time: " + str(round(end - start)))

# Takeoff and hover command function
def takeoff():
    global start, seq
    start = time.time()
    takeoff_command = f"AT*REF={seq},290718208\r"  # Takeoff command
    send_command(takeoff_command)
    print("Takeoff command sent!")
    seq += 1
    time.sleep(3)
    hover_command = f"AT*PCMD={seq},1,0,0,0,0\r"
    send_command(hover_command)
    print("Hover command sent!")
    seq += 1

# Normal landing command function
def land():
    """Send landing command to the drone."""
    land_command = f"AT*REF={seq},290718464\r"  # Landing command
    send_command(land_command)
    print("Landing command sent!")

# Directional control functions
def move_foward():
    move_command = f"AT*PCMD={seq},1,0,-1082130432,0,0\r"  # Move forward
    send_command(move_command)
    print("Move Forward command sent!")

def move_back():
    move_command = f"AT*PCMD={seq},1,0,1077936128,0,0\r"  # Move backward
    send_command(move_command)
    print("Move Backward command sent!")

def move_left():
    move_command = f"AT*PCMD={seq},1,-1082130432,0,0,0\r"  # Move left
    send_command(move_command)
    print("Move Left command sent!")

def move_right():
    move_command = f"AT*PCMD={seq},1,1077936128,0,0,0\r"  # Move right
    send_command(move_command)
    print("Move Right command sent!")

def rotate_left():
    rotate_command = f"AT*PCMD={seq},1,0,0,-1082130432,0\r"  # Rotate left
    send_command(rotate_command)
    print("Rotate Left command sent!")

def rotate_right():
    rotate_command = f"AT*PCMD={seq},1,0,0,1077936128,0\r"  # Rotate right
    send_command(rotate_command)
    print("Rotate Right command sent!")

# Altitude control functions
def increase_altitude():
    altitude_command = f"AT*PCMD={seq},1,0,0,1077936128,0\r"  # Increase altitude
    send_command(altitude_command)
    print("Increase Altitude command sent!")

def decrease_altitude():
    altitude_command = f"AT*PCMD={seq},1,0,0,-1082130432,0\r"  # Decrease altitude
    send_command(altitude_command)
    print("Decrease Altitude command sent!")

# Flip command function
def flip():
    """Send flip command to the drone."""
    flip_command = f"AT*ANIM={seq},18,15\r"  # Example flip animation
    send_command(flip_command)
    print("Flip command sent!")

# Set up GUI
root = tk.Tk()
root.title("Drone Controller")
root.geometry("400x600")
root.configure(bg="black")
# Panel Title
panel_title = tk.Label(root, text="Drone Control", bg="black", fg="white", font=("Arial", 30, "bold"), width=20, height=2)
panel_title.pack(pady=1)
# Stop button
stop_button = tk.Label(root, text="STOP 🛑", bg="red", fg="white", font=("Arial", 24, "bold"), width=10, height=2)
stop_button.pack(pady=10)
stop_button.bind("<Button-1>", lambda event: emergency_stop())

# Takeoff button
takeoff_button = tk.Label(root, text="Takeoff 🛫", bg="blue", fg="white", font=("Arial", 18, "bold"), width=10, height=2)
takeoff_button.pack(pady=10)
takeoff_button.bind("<Button-1>", lambda event: takeoff())

# Landing button
landing_button = tk.Label(root, text="Land 🛬", bg="green", fg="white", font=("Arial", 18, "bold"), width=10, height=2)
landing_button.pack(pady=10)
landing_button.bind("<Button-1>", lambda event: land())

# Directional control buttons
control_frame = tk.Frame(root, bg="black")
control_frame.pack(pady=10)

foward_button = tk.Button(control_frame, text="⇧", command=move_foward, font=("Arial", 14), width=6, height=2)
foward_button.grid(row=0, column=1, padx=5, pady=5)

left_button = tk.Button(control_frame, text="⇦", command=move_left, font=("Arial", 14), width=6, height=2)
left_button.grid(row=1, column=0, padx=5, pady=5)

back_button = tk.Button(control_frame, text="⇩", command=move_back, font=("Arial", 14), width=6, height=2)
back_button.grid(row=1, column=1, padx=5, pady=5)

right_button = tk.Button(control_frame, text="⇨", command=move_right, font=("Arial", 14), width=6, height=2)
right_button.grid(row=1, column=2, padx=5, pady=5)

rotate_left_button = tk.Button(control_frame, text="⟲", command=rotate_left, font=("Arial", 12), width=10, height=2)
rotate_left_button.grid(row=2, column=0, padx=5, pady=5)

rotate_right_button = tk.Button(control_frame, text="⟳", command=rotate_right, font=("Arial", 12), width=10, height=2)
rotate_right_button.grid(row=2, column=2, padx=5, pady=5)

# Altitude control buttons
altitude_frame = tk.Frame(root, bg="black")
altitude_frame.pack(pady=10)

increase_alt_button = tk.Button(altitude_frame, text="⍐", command=increase_altitude, font=("Arial", 14), width=12, height=2)
increase_alt_button.grid(row=0, column=0, padx=5, pady=5)

decrease_alt_button = tk.Button(altitude_frame, text="⍗", command=decrease_altitude, font=("Arial", 14), width=12, height=2)
decrease_alt_button.grid(row=0, column=1, padx=5, pady=5)

# Flip button
flip_button = tk.Label(root, text="Flip ⤼", bg="purple", fg="white", font=("Arial", 18, "bold"), width=10, height=2)
flip_button.pack(pady=10)
flip_button.bind("<Button-1>", lambda event: flip())

# Run the GUI loop
root.mainloop()
