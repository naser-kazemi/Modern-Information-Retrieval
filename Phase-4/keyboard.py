import RPi.GPIO as GPIO


# Desc: Contains the GPIO pin numbers for the keypad

keypad_rows = [26, 19, 13, 6]
keypad_columns = [5, 0, 1, 12]


# Desc: Sets up the GPIO pins for the keypad
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for row in keypad_rows:
    GPIO.setup(row, GPIO.OUT)

for column in keypad_columns:
    GPIO.setup(column, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    
# Desc: Returns the key pressed on the keypad
def get_key():
    key = None
    
    for row in keypad_rows:
        GPIO.output(row, GPIO.HIGH)
        for column in keypad_columns:
            if GPIO.input(column) == GPIO.HIGH:
                key = (keypad_rows.index(row), keypad_columns.index(column))
        GPIO.output(row, GPIO.LOW)
        
    return key


# Desc: Returns the key pressed on the keypad as a string
def get_key_string():
    key = get_key()
    
    if key == (0, 0):
        return '1'
    elif key == (0, 1):
        return '2'
    elif key == (0, 2):
        return '3'
    elif key == (0, 3):
        return 'A'
    elif key == (1, 0):
        return '4'
    elif key == (1, 1):
        return '5'
    elif key == (1, 2):
        return '6'
    elif key == (1, 3):
        return 'B'
    elif key == (2, 0):
        return '7'
    elif key == (2, 1):
        return '8'
    elif key == (2, 2):
        return '9'
    elif key == (2, 3):
        return 'C'
    elif key == (3, 0):
        return '*'
    elif key == (3, 1):
        return '0'
    elif key == (3, 2):
        return '#'
    elif key == (3, 3):
        return 'D'
    else:
        return None
    
    
    
if __name__ == '__main__':
    while True:
        print(get_key_string())
