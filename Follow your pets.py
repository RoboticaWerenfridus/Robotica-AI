ascii_art = """
                                                                                                                                                                                         
         ,--.                                                                                                                                                                            
       ,--.'|               ___      ,---,                                      .--.--.               ,---,                 ,--,         ,-.                                        ,-.  
   ,--,:  : |             ,--.'|_  ,--.' |                                     /  /    '.           ,--.' |               ,--.'|     ,--/ /|                 ,--,               ,--/ /|  
,`--.'`|  ' :             |  | :,' |  |  :                      ,---,         |  :  /`. /           |  |  :               |  | :   ,--. :/ |          .---.,--.'|         .--.,--. :/ |  
|   :  :  | |             :  : ' : :  :  :                  ,-+-. /  |        ;  |  |--`            :  :  :               :  : '   :  : ' /          /. ./||  |,        .--,`|:  : ' /   
:   |   \ | :  ,--.--.  .;__,'  /  :  |  |,--.  ,--.--.    ,--.'|'   |        |  :  ;_       ,---.  :  |  |,--.  ,--.--.  |  ' |   |  '  /        .-'-. ' |`--'_        |  |. |  '  /    
|   : '  '; | /       \ |  |   |   |  :  '   | /       \  |   |  ,"' |         \  \    `.   /     \ |  :  '   | /       \ '  | |   '  |  :       /___/ \: |,' ,'|       '--`_ '  |  :    
'   ' ;.    ;.--.  .-. |:__,'| :   |  |   /' :.--.  .-. | |   | /  | |          `----.   \ /    / ' |  |   /' :.--.  .-. ||  | :   |  |   \   .-'.. '   ' .'  | |       ,--,'||  |   \   
|   | | \   | \__\/: . .  '  : |__ '  :  | | | \__\/: . . |   | |  | |          __ \  \  |.    ' /  '  :  | | | \__\/: . .'  : |__ '  : |. \ /___/ \:     '|  | :       |  | ''  : |. \  
'   : |  ; .' ," .--.; |  |  | '.'||  |  ' | : ," .--.; | |   | |  |/          /  /`--'  /'   ; :__ |  |  ' | : ," .--.; ||  | '.'||  | ' \ \.   \  ' .\   '  : |__     :  | ||  | ' \ \ 
|   | '`--'  /  /  ,.  |  ;  :    ;|  |  :_:,'/  /  ,.  | |   | |--'          '--'.     / '   | '.'||  :  :_:,'/  /  ,.  |;  :    ;'  : |--'  \   \   ' \ ||  | '.'|  __|  : ''  : |--'  
'   : |     ;  :   .'   \ |  ,   / |  | ,'   ;  :   .'   \|   |/                `--'---'  |   :    :|  | ,'   ;  :   .'   \  ,   / ;  |,'      \   \  |--" ;  :    ;.'__/\_: |;  |,'     
;   |.'     |  ,     .-./  ---`-'  `--''     |  ,     .-./'---'                            \   \  / `--''     |  ,     .-./---`-'  '--'         \   \ |    |  ,   / |   :    :'--'       
'---'        `--`---'                         `--`---'                                      `----'             `--`---'                          '---"      ---`-'   \   \  /            
                                                                                                                                                                      `--`-'   
"""

print(ascii_art)

# Import necessary libraries
import RPi.GPIO as gpio
import sys
import pygame
import picamera
import tensorflow as tf
import numpy as np
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

# Set up GPIO and motor control pins
motor1_forward_pin = 17
motor1_backward_pin = 18
motor2_forward_pin = 22
motor2_backward_pin = 23

# Initialize the GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(motor1_forward_pin, gpio.OUT)
gpio.setup(motor1_backward_pin, gpio.OUT)
gpio.setup(motor2_forward_pin, gpio.OUT)
gpio.setup(motor2_backward_pin, gpio.OUT)

# Function to stop the robot
def stop():
    gpio.output(motor1_forward_pin, False)
    gpio.output(motor1_backward_pin, False)
    gpio.output(motor2_forward_pin, False)
    gpio.output(motor2_backward_pin, False)

# Function to make the robot move forward
def move_forward():
    gpio.output(motor1_forward_pin, True)
    gpio.output(motor1_backward_pin, False)
    gpio.output(motor2_forward_pin, True)
    gpio.output(motor2_backward_pin, False)

# Function to make the robot move backward
def move_backward():
    gpio.output(motor1_forward_pin, False)
    gpio.output(motor1_backward_pin, True)
    gpio.output(motor2_forward_pin, False)
    gpio.output(motor2_backward_pin, True)

# Function to make the robot turn left
def turn_left():
    gpio.output(motor1_forward_pin, False)
    gpio.output(motor1_backward_pin, True)
    gpio.output(motor2_forward_pin, True)
    gpio.output(motor2_backward_pin, False)

# Function to make the robot turn right
def turn_right():
    gpio.output(motor1_forward_pin, True)
    gpio.output(motor1_backward_pin, False)
    gpio.output(motor2_forward_pin, False)
    gpio.output(motor2_backward_pin, True)

# Initialize the Raspberry Pi camera
camera = picamera.PiCamera()

# Load the pre-trained "Pets" model
model_path = 'path/to/your/pre-trained/pets_model'  # Replace with the actual model path
detect_fn = tf.saved_model.load(model_path)

# Load the label map for "Pets" dataset
label_map_path = 'path/to/pets_label_map.pbtxt'  # Replace with the actual label map path
category_index = label_map_util.create_category_index_from_labelmap(label_map_path, use_display_name=True)

# Function to calculate the distance and angle between two points
def calculate_distance_and_angle(x1, y1, x2, y2):
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    angle = np.arctan2(y2 - y1, x2 - x1)
    return distance, angle

# Function to adjust the robot's movements based on the position of the detected object
def adjust_robot_movement(image_np, center_x, center_y):
    # Calculate the center of the camera view
    camera_center_x = image_np.shape[1] / 2
    camera_center_y = image_np.shape[0] / 2

    # Calculate the distance and angle between the robot and the detected object
    distance, angle = calculate_distance_and_angle(camera_center_x, camera_center_y, center_x, center_y)

    # Determine the robot's movements based on the angle and distance
    # You may need to experiment and fine-tune these values for your specific robot
    if distance > 50:  # Move only if the object is far enough (adjust this distance threshold as needed)
        if angle > 0.1:
            # Turn right
            turn_right()
        elif angle < -0.1:
            # Turn left
            turn_left()
        else:
            # Move forward
            move_forward()
    else:
        # Stop when the object is close enough
        stop()

# Function to perform object detection and control the robot
def ai_control(joystick):
    # Get the joystick values
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    # Determine the robot's movement based on joystick values
    if y_axis < -0.5:
        # Move forward
        move_forward()
    elif y_axis > 0.5:
        # Move backward
        move_backward()
    elif x_axis < -0.5:
        # Turn left
        turn_left()
    elif x_axis > 0.5:
        # Turn right
        turn_right()
    else:
        # Stop
        stop()

    # Capture an image from the Raspberry Pi camera
    camera.capture("image.jpg")

    # Load the image and convert it to a NumPy array
    image_np = np.array(Image.open("image.jpg"))

    # Perform object detection using the model
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)

    # Filter detections to include only cats and dogs with high confidence scores
    min_score_thresh = 0.5
    filtered_classes = [1, 2]  # Class IDs for cats and dogs in the label map (check your label map for correct IDs)
    filtered_boxes = detections['detection_boxes'][0][detections['detection_scores'][0] > min_score_thresh]
    filtered_classes = detections['detection_classes'][0][detections['detection_scores'][0] > min_score_thresh]

    if len(filtered_boxes) > 0:
        ymin, xmin, ymax, xmax = filtered_boxes[0]
        center_x = int((xmin + xmax) * image_np.shape[1] / 2)
        center_y = int((ymin + ymax) * image_np.shape[0] / 2)

        # Call the function to adjust the robot's movements based on the detected object
        adjust_robot_movement(image_np, center_x, center_y)

def main():
    # Initialize Pygame and the joystick module
    pygame.init()
    pygame.joystick.init()

    # Check for any connected joysticks
    if pygame.joystick.get_count() == 0:
        print("No joysticks found.")
        return

    # Get the first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    try:
        while True:
            # Process Pygame events
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    # Joystick movement detected
                    ai_control(joystick)
                elif event.type == pygame.JOYBUTTONUP:
                    # Joystick button released
                    stop()
                elif event.type == pygame.QUIT:
                    # Quit event detected
                    stop()
                    pygame.quit()
                    sys.exit()
    except KeyboardInterrupt:
        # Handle Ctrl+C interruption
        stop()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()
