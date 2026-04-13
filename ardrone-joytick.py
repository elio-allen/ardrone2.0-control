
import tkinter as tk
import socket
import time
import math

# Drone IP and command port
drone_ip = "192.168.1.1"
command_port = 5556

# Initialize the command socket
sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq = 1
start = 0
takeoff = False  # Initialize takeoff state

def send_command(command):
    """Send AT command to the drone and increment sequence number."""
    global seq
    sock_command.sendto(command.encode(), (drone_ip, command_port))
    seq += 1

# Emergency stop command function
def emergency_stop():
    global start, takeoff
    stop_command = f"AT*REF={seq},290717952\r"  # Emergency stop command
    send_command(stop_command)
    print("Emergency stop command sent!")
    end = time.time()
    print("Flight time: " + str(round(end - start)))
    takeoff = False  # Set takeoff to False

# Takeoff and hover command function
def takeoff_drone():
    global start, seq, takeoff
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
    takeoff = True  # Set takeoff to True

# Normal landing command function
def land():
    """Send landing command to the drone."""
    global takeoff
    land_command = f"AT*REF={seq},290718464\r"  # Landing command
    send_command(land_command)
    print("Landing command sent!")
    takeoff = False  # Set takeoff to False

# Deadzone value for altitude and rotation
deadzone = 10

# Move command based on joystick for forward, backward, left, and right
def move_with_joystick(dx, dy):
    if not takeoff:  # Block movement if not in takeoff state
        print("Joystick input blocked: drone is not in the air.")
        return
    
    # Ignore movement if both axes are effectively 0
    if dx == 0 and dy == 0:
        print("No movement command sent.")
        return
    
    # Calculate movement scaling
    distance = min(math.sqrt(dx**2 + dy**2) / max_distance, 1)
    speed_x = int(distance * dx / max_distance * 1077936128)
    speed_y = int(distance * dy / max_distance * 1077936128)
    
    move_command = f"AT*PCMD={seq},1,{speed_x},{-speed_y},0,0\r"
    send_command(move_command)
    print(f"Move command sent! Speed X: {speed_x}, Speed Y: {-speed_y}")

# Altitude and rotation control based on joystick
def control_altitude_rotation(dx, dy):
    if not takeoff:  # Block movement if not in takeoff state
        print("Joystick input blocked: drone is not in the air.")
        return
    
    # Apply deadzone for both axes
    if abs(dx) < deadzone:
        dx = 0
    if abs(dy) < deadzone:
        dy = 0
    
    # Ignore movement if both axes are effectively 0
    if dx == 0 and dy == 0:
        print("Within deadzone, no altitude/rotation command sent.")
        return
    
    # Calculate control scaling
    distance = min(math.sqrt(dx**2 + dy**2) / max_distance2, 1)
    rotation_speed = int(distance * dx / max_distance2 * 1077936128)
    altitude_speed = int(distance * dy / max_distance2 * 1077936128)
    
    control_command = f"AT*PCMD={seq},1,0,0,{altitude_speed},{rotation_speed}\r"
    send_command(control_command)
    print(f"Altitude: {altitude_speed}, Rotation: {rotation_speed}")

# Joystick control functions
def on_joystick_press(event, joystick, knob, center, move_func):
    joystick.bind("<B1-Motion>", lambda e: on_joystick_drag(e, joystick, knob, center, move_func))

def on_joystick_drag(event, joystick, knob, center, move_func):
    dx = event.x - center[0]
    dy = event.y - center[1]
    x = min(max(event.x, 10), joystick.winfo_width() - 10)
    y = min(max(event.y, 10), joystick.winfo_height() - 10)
    joystick.coords(knob, x - 10, y - 10, x + 10, y + 10)
    move_func(dx, dy)

def on_joystick_release(event, joystick, knob, center):
    joystick.coords(knob, center[0] - 10, center[1] - 10, center[0] + 10, center[1] + 10)
    joystick.unbind("<B1-Motion>")

# GUI Setup
root = tk.Tk()
root.title("Drone Controller")
root.geometry("400x700")
root.configure(bg="black")

# Stop button at the top alone
stop_button = tk.Label(root, text="STOP 🛑", bg="red", fg="white", font=("Arial", 24, "bold"), width=10, height=2)
stop_button.pack(pady=10)
stop_button.bind("<Button-1>", lambda event: emergency_stop())

# Frame for takeoff and landing buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=5)

takeoff_button = tk.Label(button_frame, text="Takeoff 🛫", bg="blue", fg="white", font=("Arial", 18, "bold"), width=10, height=2)
takeoff_button.pack(side=tk.LEFT, padx=(0, 20))  # Add space to the right
takeoff_button.bind("<Button-1>", lambda event: takeoff_drone())

landing_button = tk.Label(button_frame, text="Land 🛬", bg="green", fg="white", font=("Arial", 18, "bold"), width=10, height=2)
landing_button.pack(side=tk.LEFT)
landing_button.bind("<Button-1>", lambda event: land())

# Frame for the joystick controls
joystick_frame = tk.Frame(root, bg="black")
joystick_frame.pack(pady=10)

# First Joystick (Altitude and Rotation control) on the left
canvas2_width, canvas2_height = 150, 150
canvas2 = tk.Canvas(joystick_frame, width=canvas2_width, height=canvas2_height, bg="gray")
canvas2.pack(side=tk.LEFT, padx=5)

bg_image2 = tk.PhotoImage(file="joystick_bg.png")  # Same or different image file for the second joystick
canvas2.create_image(canvas2_width // 2, canvas2_height // 2, image=bg_image2)

joystick_center2 = (canvas2_width // 2, canvas2_height // 2)
joystick_knob2 = canvas2.create_oval(joystick_center2[0] - 10, joystick_center2[1] - 10,
                                     joystick_center2[0] + 10, joystick_center2[1] + 10, fill="green")

max_distance2 = math.sqrt((canvas2_width // 2) ** 2 + (canvas2_height // 2) ** 2)

canvas2.bind("<Button-1>", lambda e: on_joystick_press(e, canvas2, joystick_knob2, joystick_center2, control_altitude_rotation))
canvas2.bind("<ButtonRelease-1>", lambda e: on_joystick_release(e, canvas2, joystick_knob2, joystick_center2))

# Second Joystick (Directional control) on the right
canvas_width, canvas_height = 150, 150
canvas = tk.Canvas(joystick_frame, width=canvas_width, height=canvas_height, bg="gray")
canvas.pack(side=tk.LEFT, padx=5)

bg_image = tk.PhotoImage(file="joystick_bg.png")  # Replace with your image file path
canvas.create_image(canvas_width // 2, canvas_height // 2, image=bg_image)

joystick_center = (canvas_width // 2, canvas_height // 2)
joystick_knob = canvas.create_oval(joystick_center[0] - 10, joystick_center[1] - 10,
                                   joystick_center[0] + 10, joystick_center[1] + 10, fill="blue")

max_distance = math.sqrt((canvas_width // 2) ** 2 + (canvas_height // 2) ** 2)

canvas.bind("<Button-1>", lambda e: on_joystick_press(e, canvas, joystick_knob, joystick_center, move_with_joystick))
canvas.bind("<ButtonRelease-1>", lambda e: on_joystick_release(e, canvas, joystick_knob, joystick_center))

# Keep references to images
canvas.bg_image = bg_image
canvas2.bg_image = bg_image2

root.mainloop()
