try:
    import adafruit_fingerprint
    print("Adafruit Fingerprint library is installed.")
except ImportError:
    print("Adafruit Fingerprint library not found. Please install it using 'pip install adafruit-circuitpython-fingerprint'.")
    exit()

import time
import board
import busio
from digitalio import DigitalInOut, Direction
import serial

# Set up the onboard LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Set up UART communication
try:
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
except serial.SerialException as e:
    print(f"Error initializing serial connection: {e}")
    exit()

# Initialize the fingerprint sensor
try:
    finger = adafruit_fingerprint.AdafruitFingerprint(uart)
    print("Fingerprint sensor initialized successfully.")
except Exception as e:
    print(f"Failed to initialize the fingerprint sensor: {e}")
    finger = None  # Avoid undefined errors

def enroll_fingerprint(finger, location_id):
    """
    Enroll a fingerprint at a given location ID.
    """
    if finger is None:
        print("Fingerprint sensor not initialized.")
        return False

    print(f"Place your finger on the sensor to register (ID: {location_id})...")

    # Step 1: Capture the fingerprint image
    while True:
        result = finger.gen_img()
        if result == 0:  # 0 = Success
            print("Fingerprint image captured successfully.")
            break
        elif result == 2:  # 2 = No finger detected
            print("No finger detected. Please try again.")
        elif result == 3:  # 3 = Image capture failed
            print("Image capture failed. Try again.")
        else:
            print(f"Unexpected error: {result}")
            return False

    # Step 2: Convert the image to a template
    result = finger.img_2Tz(1)
    if result != 0:
        print(f"Failed to convert image to template. Error: {result}")
        return False

    print("Fingerprint template created.")

    # Step 3: Ask user to lift and place their finger again for confirmation
    print("Lift your finger and place it again for confirmation...")
    time.sleep(2)

    while True:
        result = finger.gen_img()
        print(f"Result from gen_img: {result}")  # Debugging print to verify image capture
        if result == 0:
            print("Second fingerprint image captured successfully.")
            break
        elif result == 2:
            print("No finger detected. Please try again.")
        elif result == 3:
            print("Image capture failed. Try again.")
        else:
            print(f"Unexpected error: {result}")
            return False

    # Step 4: Convert the second image
    result = finger.img_2Tz(2)
    print(f"Result of img_2Tz: {result}")  # Debugging print
    if result != 0:
        print(f"Failed to convert second image. Error: {result}")
        return False

    # Step 5: Create a fingerprint model from both images
    result = finger.reg_model()
    if result != 0:
        print(f"Failed to create fingerprint model. Error: {result}")
        return False

        # Step 6: Store the fingerprint in the specified location
    result = finger.store(location_id, location_id)  # Pass location_id for both arguments
    if result == 0:
        print(f"Fingerprint registered successfully at ID {location_id}!")
        return True
    else:
        print(f"Failed to store fingerprint. Error: {result}")
        return False


# Ensure finger is initialized before calling the function
if finger is not None:
    enroll_fingerprint(finger, 1)
else:
    print("Error: Fingerprint sensor is not initialized.")