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
import RPi.GPIO as gpio
import sys
import pygame
import openai  # Install this library: pip install openai

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
    # Get the joystick values
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    # Prepare the text prompt to send to GPT-3.5-turbo
    prompt = f"Joystick X-axis: {x_axis:.2f}, Y-axis: {y_axis:.2f}. Provide a movement command."

    # Send the prompt to GPT-3.5-turbo for AI-generated response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are controlling a robot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.7,
    )

    # Extract the AI-generated response
    ai_response = response['choices'][0]['message']['content'].strip().lower()

    # Process the AI response to control the robot
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

def main():
    try:
        while True:
            # Process Pygame events
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    # Joystick movement detected
                    ai_control(joystick)  # Use AI to control the robot
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
