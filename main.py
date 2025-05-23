import time
import pyfirmata2  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

# Set Arduino's COM port
port = 'COM3'
board = pyfirmata2.Arduino(port)
board.samplingOn(100)

# Define input pins
pin_numbers = [2, 3, 4, 8]
pin_names = {
    2: "Top Right",
    3: "Bottom Right",
    4: "Top Left",
    8: "Bottom Left"
}

# Setup pins and state tracking
pins = {}
pin_states = {}
press_counts = {num: 0 for num in pin_numbers}
last_press_time = {num: 0 for num in pin_numbers}
DEBOUNCE_MS = 200  # debounce time in milliseconds

for num in pin_numbers:
    pin = board.get_pin(f'd:{num}:i')
    pin.enable_reporting()
    pins[num] = pin
    pin_states[num] = False

# Callback factory with debounce logic
def make_callback(pin_number):
    def pin_callback(value):
        current_time = time.time() * 1000  # time in ms
        if value and not pin_states[pin_number]:  # Rising edge
            if current_time - last_press_time[pin_number] >= DEBOUNCE_MS:
                print(f"Completed {pin_names[pin_number]}")
                press_counts[pin_number] += 1
                last_press_time[pin_number] = current_time
        pin_states[pin_number] = value
    return pin_callback

# Register callbacks
for num in pin_numbers:
    pins[num].register_callback(make_callback(num))

print("Checking for button presses. Press Ctrl+C to stop.")

try:
    while True:
        board.iterate()
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nExiting and closing board connection.")
    board.exit()

    # Plot the press counts
    print("Generating chart of completions.")
    labels = [pin_names[n] for n in pin_numbers]
    counts = [press_counts[n] for n in pin_numbers]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, counts, color='skyblue', edgecolor='black')
    plt.title("Button Completions per Pin")
    plt.xlabel("Pin")
    plt.ylabel("Number of Completions")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()