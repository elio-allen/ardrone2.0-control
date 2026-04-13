
import tkinter as tk
import socket
import time
import math
from ttf_opensans import OPENSANS_SEMIBOLDITALIC

# Drone IP and command port
drone_ip = "192.168.1.1"
command_port = 5556

# Initialize the command socket
sock_command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq = 1
start = 0
takeoff = False  # Initialize takeoff state

# Function to send commands to the drone
def send_command(command):
    global seq
    sock_command.sendto(command.encode(), (drone_ip, command_port))
    seq += 1

# Console Output class to capture print outputs in GUI
class ConsoleOutput(tk.Text):
    def write(self, message):
        self.insert(tk.END, message + "\n")
        self.see(tk.END)  # Auto-scroll to the end

# Emergency stop command function
def emergency_stop():
    global start, takeoff
    stop_command = f"AT*REF={seq},290717952\r"  # Emergency stop command
    send_command(stop_command)
    console_output.write("Emergency stop command sent!")
    end = time.time()
    console_output.write("Flight time: " + str(round(end - start)))
    takeoff = False

# Takeoff and hover command function
def takeoff_drone():
    global start, seq, takeoff
    start = time.time()
    takeoff_command = f"AT*REF={seq},290718208\r"  # Takeoff command
    send_command(takeoff_command)
    console_output.write("Takeoff command sent!")
    seq += 1
    time.sleep(3)
    hover_command = f"AT*PCMD={seq},1,0,0,0,0\r"
    send_command(hover_command)
    console_output.write("Hover command sent!")
    seq += 1
    takeoff = True

# Normal landing command function
def land():
    global takeoff
    land_command = f"AT*REF={seq},290718464\r"  # Landing command
    send_command(land_command)
    console_output.write("Landing command sent!")
    takeoff = False

# Deadzone value for altitude and rotation
deadzone = 10

# Move command based on joystick for forward, backward, left, and right
def move_with_joystick(dx, dy):
    if not takeoff:
        console_output.write("Joystick input blocked: drone is not in the air.")
        return
    if dx == 0 and dy == 0:
        console_output.write("No movement command sent.")
        return
    distance = min(math.sqrt(dx**2 + dy**2) / max_distance, 1)
    speed_x = int(distance * dx / max_distance * 1077936128)
    speed_y = int(distance * dy / max_distance * 1077936128)
    move_command = f"AT*PCMD={seq},1,{speed_x},{-speed_y},0,0\r"
    send_command(move_command)
    console_output.write(f"Move command sent! Speed X: {speed_x}, Speed Y: {-speed_y}")

# Altitude and rotation control based on joystick
def control_altitude_rotation(dx, dy):
    if not takeoff:
        console_output.write("Joystick input blocked: drone is not in the air.")
        return
    if abs(dx) < deadzone:
        dx = 0
    if abs(dy) < deadzone:
        dy = 0
    if dx == 0 and dy == 0:
        console_output.write("Within deadzone, no altitude/rotation command sent.")
        return
    distance = min(math.sqrt(dx**2 + dy**2) / max_distance2, 1)
    rotation_speed = int(distance * dx / max_distance2 * 1077936128)
    altitude_speed = int(distance * dy / max_distance2 * 1077936128)
    control_command = f"AT*PCMD={seq},1,0,0,{altitude_speed},{rotation_speed}\r"
    send_command(control_command)
    console_output.write(f"Altitude: {altitude_speed}, Rotation: {rotation_speed}")

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
    joystick.coords(knob, center[0] - 10, center[0] + 10, center[1] - 10, center[1] + 10)
    joystick.unbind("<B1-Motion>")

# GUI Setup
root = tk.Tk()
root.title("Drone Controller")
root.configure(bg="black")

# Stop button at the top
stop_button = tk.Label(root, text="STOP", bg="red", fg="white", font=("Arial", 30, "bold"), width=10, height=2)
stop_button.pack(pady=10)
stop_button.bind("<Button-1>", lambda event: emergency_stop())

# Frame for joystick and buttons
control_frame = tk.Frame(root, bg="black")
control_frame.pack(pady=10)

# Joystick for altitude and rotation on the left
canvas2_width, canvas2_height = 200, 200
canvas2 = tk.Canvas(control_frame, width=canvas2_width, height=canvas2_height, bg="gray")
canvas2.pack(side=tk.LEFT)

bg_image2 = tk.PhotoImage(file="joystick_bg_mobile.png")  # Use the appropriate file path
canvas2.create_image(canvas2_width // 2, canvas2_height // 2, image=bg_image2)

joystick_center2 = (canvas2_width // 2, canvas2_height // 2)
joystick_knob2 = canvas2.create_oval(joystick_center2[0] - 10, joystick_center2[1] - 10,
                                     joystick_center2[0] + 10, joystick_center2[1] + 10, fill="green")

max_distance2 = math.sqrt((canvas2_width // 2) ** 2 + (canvas2_height // 2) ** 2)

canvas2.bind("<Button-1>", lambda e: on_joystick_press(e, canvas2, joystick_knob2, joystick_center2, control_altitude_rotation))
canvas2.bind("<ButtonRelease-1>", lambda e: on_joystick_release(e, canvas2, joystick_knob2, joystick_center2))

# Frame for buttons (Takeoff and Land) and XY movement joystick
button_frame = tk.Frame(control_frame, bg="black")
button_frame.pack(side=tk.LEFT, padx=(10, 0))

# Takeoff and landing buttons
takeoff_button = tk.Label(button_frame, text="Takeoff", bg="blue", fg="white", font=("Arial", 18, "bold"), width=7, height=4)
takeoff_button.pack(side=tk.LEFT)
takeoff_button.bind("<Button-1>", lambda event: takeoff_drone())

landing_button = tk.Label(button_frame, text="Land", bg="green", fg="white", font=("Arial", 18, "bold"), width=7, height=4)
landing_button.pack(side=tk.LEFT, padx=(10, 10))
landing_button.bind("<Button-1>", lambda event: land())

# Joystick for XY movement on the right
canvas_width, canvas_height = 200, 200
canvas = tk.Canvas(control_frame, width=canvas_width, height=canvas_height, bg="gray")
canvas.pack(side=tk.LEFT)

bg_image = tk.PhotoImage(file="joystick_bg_mobile.png")  # Use the appropriate file path
canvas.create_image(canvas_width // 2, canvas_height // 2, image=bg_image)

joystick_center = (canvas_width // 2, canvas_height // 2)
joystick_knob = canvas.create_oval(joystick_center[0] - 10, joystick_center[1] - 10,
                                   joystick_center[0] + 10, joystick_center[1] + 10, fill="blue")

max_distance = math.sqrt((canvas_width // 2) ** 2 + (canvas_height // 2) ** 2)

canvas.bind("<Button-1>", lambda e: on_joystick_press(e, canvas, joystick_knob, joystick_center, move_with_joystick))
canvas.bind("<ButtonRelease-1>", lambda e: on_joystick_release(e, canvas, joystick_knob, joystick_center))

# Console Output Text Box
console_output = ConsoleOutput(root, height=6, width=60, bg="black", fg="white", font=("OPENSANS_SEMIBOLDITALIC", 10))
console_output.pack(pady=10)

# Keep references to images
canvas.bg_image = bg_image
canvas2.bg_image = bg_image2

# Run the GUI loop
root.mainloop()
