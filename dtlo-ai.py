import RPi.GPIO as gpio
import sys
import pygame
import openai
import cv2
import numpy as np

# GPIO setup (update with your actual GPIO pins)
pin1, pin2, pin3, pin4 = 17, 18, 22, 23

gpio.setmode(gpio.BCM)
gpio.setup(pin1, gpio.OUT)
gpio.setup(pin2, gpio.OUT)
gpio.setup(pin3, gpio.OUT)
gpio.setup(pin4, gpio.OUT)

# Pygame initialization for joystick control
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# OpenAI setup (Replace 'YOUR_GPT_API_KEY' with your actual API key)
openai.api_key = 'YOUR_GPT_API_KEY'

# Webcam setup using OpenCV
cap = cv2.VideoCapture(0)  # 0 is the default camera

def stop():
    gpio.output(pin1, False)
    gpio.output(pin2, False)
    gpio.output(pin3, False)
    gpio.output(pin4, False)

def move_forward():
    gpio.output(pin1, True)
    gpio.output(pin2, False)
    gpio.output(pin3, True)
    gpio.output(pin4, False)

def move_backward():
    gpio.output(pin1, False)
    gpio.output(pin2, True)
    gpio.output(pin3, False)
    gpio.output(pin4, True)

def turn_left():
    gpio.output(pin1, False)
    gpio.output(pin2, True)
    gpio.output(pin3, True)
    gpio.output(pin4, False)

def turn_right():
    gpio.output(pin1, True)
    gpio.output(pin2, False)
    gpio.output(pin3, False)
    gpio.output(pin4, True)

def ai_control(joystick):
    # Joystick AI control logic as before
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    prompt = f"Joystick X-axis: {x_axis:.2f}, Y-axis: {y_axis:.2f}. Provide a movement command."

    # GPT-3.5-turbo API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are controlling a robot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.7
    )
    ai_response = response['choices'][0]['message']['content'].strip().lower()

    # Basic movement logic based on AI response
    if "forward" in ai_response:
        move_forward()
    elif "backward" in ai_response:
        move_backward()
    elif "left" in ai_response:
        turn_left()
    elif "right" in ai_response:
        turn_right()
    else:
        stop()

def detect_obstacles_in_region(frame):
    """
    This function detects obstacles in a given frame region.
    Returns the number of detected obstacles.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours)

def choose_clearest_path(frame):
    """
    This function splits the frame into three regions (left, center, right),
    and chooses the clearest path based on obstacle detection in each region.
    """
    height, width, _ = frame.shape
    third_width = width // 3

    # Split the frame into left, center, and right regions
    left_region = frame[:, :third_width]
    center_region = frame[:, third_width:2*third_width]
    right_region = frame[:, 2*third_width:]

    # Detect obstacles in each region
    left_obstacles = detect_obstacles_in_region(left_region)
    center_obstacles = detect_obstacles_in_region(center_region)
    right_obstacles = detect_obstacles_in_region(right_region)

    # Debugging output for the obstacle counts
    print(f"Left: {left_obstacles}, Center: {center_obstacles}, Right: {right_obstacles}")

    # Choose the direction with the fewest obstacles
    if left_obstacles < center_obstacles and left_obstacles < right_obstacles:
        return "left"
    elif center_obstacles < left_obstacles and center_obstacles < right_obstacles:
        return "forward"
    else:
        return "right"

def main():
    try:
        while True:
            # Capture frame-by-frame from the webcam
            ret, frame = cap.read()

            if ret:
                # Determine the clearest path based on obstacle detection
                direction = choose_clearest_path(frame)

                # Move the robot based on the clearest path
                if direction == "left":
                    turn_left()
                elif direction == "right":
                    turn_right()
                elif direction == "forward":
                    move_forward()
                else:
                    stop()

                # Show the frame for debugging purposes
                cv2.imshow('Frame', frame)

            # Process Pygame events
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    ai_control(joystick)
                elif event.type == pygame.JOYBUTTONUP:
                    stop()
                elif event.type == pygame.QUIT:
                    stop()
                    pygame.quit()
                    sys.exit()

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        stop()
    finally:
        # Cleanup GPIO and OpenCV resources
        stop()
        cap.release()
        cv2.destroyAllWindows()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()
