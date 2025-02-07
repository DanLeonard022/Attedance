import time
import board
import busio
from digitalio import DigitalInOut, Direction
import serial
import adafruit_fingerprint
from RPLCD.i2c import CharLCD

# Assume that the attendance system already has some student data stored in a dictionary or database
students = {}  # Replace with actual student data storage method

# Set up the onboard LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Set up UART communication for the fingerprint sensor
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
    finger = None

# LCD setup (16x2 size)
lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
lcd.clear()

def display_on_lcd(message):
    """Display a message on the LCD screen."""
    lcd.clear()
    lcd.write_string(message)
    time.sleep(3)

def enroll_fingerprint(finger, student_id):
    """
    Enroll a fingerprint for a student in the attendance system.
    """
    if finger is None:
        print("Fingerprint sensor not initialized.")
        return False

    display_on_lcd(f"Registering: {student_id}")

    print(f"Place your finger on the sensor to register (Student ID: {student_id})...")

    # Step 1: Capture the fingerprint image
    while True:
        result = finger.gen_img()
        if result == 0:
            print("Fingerprint image captured successfully.")
            break
        elif result == 2:
            print("No finger detected. Please try again.")
        elif result == 3:
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
        print(f"Result from gen_img: {result}")  # Debugging print
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
    try:
        location_id = int(student_id)  # Ensure location_id is an integer
        result = finger.store(location_id, location_id)  # Pass location_id as integer
        if result == 0:
            print(f"Fingerprint registered successfully for Student ID {student_id}!\n\n")
            students[student_id] = {'fingerprint': location_id}  # Add student to the system
            display_on_lcd(f"Student {student_id} enrolled.")
            return True
        else:
            print(f"Failed to store fingerprint. Error code: {result}")
            return False
    except Exception as e:
        print(f"Error while storing fingerprint: {e}")
        return False


def mark_attendance(student_id):
    """
    Mark attendance for the student based on their fingerprint.
    """
    if student_id in students:
        print(f"Attendance marked for Student ID: {student_id} \n\n")
        display_on_lcd(f"Attendance marked for {student_id}")
    else:
        print(f"Student ID {student_id} not found in system.")
        display_on_lcd(f"Student {student_id} not found.")

# Menu loop for attendance system
while True:
    display_on_lcd("Nagkaon kana    love?")
    display_on_lcd("MISSS YOU NA")
    print("Welcome to the Attendance Management System")
    print("1. Enroll Fingerprint")
    print("2. Mark Attendance")
    print("3. Exit")
    choice = input("Please choose an option: ")

    if choice == '1':
        student_id = input("Enter Student ID to register fingerprint: ")
        enroll_fingerprint(finger, student_id)
    elif choice == '2':
        student_id = input("Enter Student ID to mark attendance: ")
        mark_attendance(student_id)
    elif choice == '3':
        print("Exiting the system.")
        display_on_lcd("Exiting system...")
        break
    else:
        print("Invalid choice, please try again.")
