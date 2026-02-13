# -*- coding: utf-8 -*-
from pepper.robot import Pepper
from demo import uploadPhotoToWeb
import random, os, time
import qi
import cv2
import numpy as np
import threading
import subprocess

''' 
This is a minimal demo showing you how to work with Pepper class and reach some of the frequently used functions.

Please keep in mind that this code only works with Python 2!

To launch the demo on your computer, you need to have the Pepper SDK 2.5.10 library for Python 2.7 
(imported as qi or naoqi). It can be installed from: 
https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares
Also, if you have Linux, add the path to qi in your .bashrc:
export PYTHONPATH=${PYTHONPATH}:/home/yourusername/pynaoqi/lib/python2.7/site-packages

Then install all the other requirements using:
pip2 install -r ./requirements.txt 
'''


def recognize_person(robot_cls, language="en"):
    """
    Try to recognize the person in front of Pepper and greet him.

    :param robot_cls: instance of the Pepper class
    :param: language: str, "en" for English, "cz" for Czech
    """
    name = robot_cls.recognize_person()
    responses = {"en":{"faceKnown":["Glad to see you, {}", "I am happy to see you again, {}", "Hello, {}"],
                       "faceUnknown":["I don't think we've met before.","I am sorry, I don't know you yet."]},
                 "cz":{"faceKnown":["Rád tě vidím, {}", "Je hezké tě zase vidět, {}", "Ahoj, {}"],
                       "faceUnknown":["Myslím, že my dva se zatím neznáme.","Promiň, ale asi tě zatím neznám."]}}

    if name is not None:
        name = name.lower()
        robot_cls.say(random.choice(responses[language]["faceKnown"]).format(name))
    else:
        robot_cls.say(random.choice(responses[language]["faceUnknown"]))


def learn_person(robot_cls, language="en"):
    """
    Try to learn the name of the person in front of Pepper.

    :param robot_cls: instance of the Pepper class
    :param: language: str, "en" for English, "cz" for Czech
    """
    dialog = {"en":{"1":"What is your name?", "2":["That's a pretty name.", "I will remember that.", "Nice to meet you."], '3':'Your name is {}, am I right?', "lang":"en-US"},
              "cz":{"1":"Jak se jmenuješ?", "2":["To je hezké jméno.", "Budu si to pamatovat.", "Rád tě poznávám."],'3':'Jmenuješ se {}, slyšel jsem správně?', "lang":"cs-CZ"}}
    robot_cls.say(dialog[language]["1"])
    while True:
        name = robot_cls.recognize_google(lang=dialog[language]["lang"])
        if name != "":
            for word in [ "jmenuju ", "jemnuji ","jsem ", "je ", "mi ", "se ", "name is", "is", "I am", "I'm"]:
                if word.lower() in name.lower():
                    name = name.split(word)[-1]
            break
        else:
            continue
    print("Recognized name {}".format(name.encode('utf-8')))
    robot_cls.say(name.encode('utf-8'))
    while True:
        success = robot_cls.learn_face(name)
        if success:
            break
    robot_cls.say(random.choice(dialog[language]["2"]))

def take_picture_show(robot):
    local_img_path = robot.take_picture()
    photo_link = uploadPhotoToWeb(local_img_path)
    robot.show_image(photo_link)
    time.sleep(3)
    robot.reset_tablet()

def load_trials(trials_path):
    trials = []
    if not os.path.exists(trials_path):
        raise IOError("Trials file not found: {}".format(trials_path))
    with open(trials_path, "r") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "," not in line:
                raise ValueError("Invalid trial format (missing comma): {}".format(line))
            parts = line.rsplit(",", 2)  # Split into max 3 parts: question, position, image_path
            if len(parts) < 2:
                raise ValueError("Invalid trial format: {}".format(line))
            
            question = parts[0].strip()
            position_str = parts[1].strip()
            image_path = parts[2].strip() if len(parts) == 3 else None

            if image_path and not os.path.isabs(image_path):
                image_path = os.path.join(os.path.dirname(os.path.abspath(trials_path)), image_path)
            
            if not question:
                raise ValueError("Empty question in line: {}".format(line))
            try:
                position = int(position_str)
            except ValueError:
                raise ValueError("Invalid position (not an int): {}".format(line))
            if position < 1 or position > 5:
                raise ValueError("Position out of range (1-5): {}".format(line))
            
            # Validate image path exists if provided
            if image_path and not os.path.exists(image_path):
                raise IOError("Image file not found: {}".format(image_path))
            
            trials.append((question, position, image_path))
    return trials

# Global variables for persistent image display
g_display_window = {"name": None, "index": 1, "x_offset": 0, "y_offset": 0, "active": False}
g_current_image_path = {"path": None}

def update_display_image(image_path):
    """
    Update the currently displayed image while keeping the window open.
    
    :param image_path: Path to the new image file to display
    """
    if not image_path or not os.path.exists(image_path):
        print("Warning: Image file not found: {}".format(image_path))
        return
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            print("Warning: Could not read image: {}".format(image_path))
            return
        
        if g_display_window["active"] and g_display_window["name"]:
            cv2.imshow(g_display_window["name"], image)
            cv2.waitKey(1)  # Process the display update
            g_current_image_path["path"] = image_path
            print("Image updated to: {}".format(image_path))
        else:
            print("Display window not active. Cannot update image.")
    except Exception as e:
        print("Error updating image: {}".format(str(e)))

def display_image_fullscreen_persistent(image_path, display_index=1):
    """
    Display an image fullscreen in a persistent window that can be updated.
    Runs in a separate thread to not block robot operations.
    
    :param image_path: Path to the initial image file to display
    :param display_index: Display index (0 for primary, 1 for secondary/external screen)
    """
    try:
        if not image_path or not os.path.exists(image_path):
            print("Warning: Image file not found: {}".format(image_path))
            return
        
        # Read the initial image
        image = cv2.imread(image_path)
        if image is None:
            print("Warning: Could not read image: {}".format(image_path))
            return
        
        # Detect external screen resolution and offset using xrandr
        display_info = get_display_info(display_index)
        screen_width, screen_height, x_offset, y_offset = display_info
        print("Displaying on screen {} at position ({}, {}) with resolution {}x{}".format(
            display_index, x_offset, y_offset, screen_width, screen_height))
        
        # Create fullscreen window with unique name
        window_name = "Experiment Display"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Move window to the correct screen position BEFORE showing content
        cv2.moveWindow(window_name, x_offset, y_offset)
        
        # Set to fullscreen
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Show initial image
        cv2.imshow(window_name, image)
        cv2.waitKey(100)  # Allow window to render
        
        # Update global display window info
        g_display_window["name"] = window_name
        g_display_window["index"] = display_index
        g_display_window["x_offset"] = x_offset
        g_display_window["y_offset"] = y_offset
        g_display_window["active"] = True
        g_current_image_path["path"] = image_path
        
        print("Persistent display window created. Window will stay open for image updates.")
        
        # Keep the window open by processing events at intervals
        while g_display_window["active"]:
            key = cv2.waitKey(100)  # Check for events every 100ms
            if key != -1 and key != 255:  # If a key was pressed
                print("Key pressed, but window remains open for image updates.")
        
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Process window destruction
        
    except Exception as e:
        print("Error in persistent display: {}".format(str(e)))
        g_display_window["active"] = False
        cv2.destroyAllWindows()
        cv2.waitKey(1)

def display_image_fullscreen(image_path, display_index=1):
    """
    Display an image fullscreen on an external screen using OpenCV.
    Automatically detects external screen resolution and displays without duration.
    Does not destroy windows at the end.
    
    :param image_path: Path to the image file to display
    :param display_index: Display index (0 for primary, 1 for secondary/external screen)
    """
    try:
        if not image_path or not os.path.exists(image_path):
            print("Warning: Image file not found: {}".format(image_path))
            return
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print("Warning: Could not read image: {}".format(image_path))
            return
        
        # Detect external screen resolution and offset using xrandr
        display_info = get_display_info(display_index)
        screen_width, screen_height, x_offset, y_offset = display_info
        print("Displaying on screen {} at position ({}, {}) with resolution {}x{}".format(
            display_index, x_offset, y_offset, screen_width, screen_height))
        
        # Create fullscreen window with unique name
        window_name = "Question Image {}".format(time.time())
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Move window to the correct screen position BEFORE showing content
        cv2.moveWindow(window_name, x_offset, y_offset)
        
        # Set to fullscreen
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Show image
        cv2.imshow(window_name, image)
        cv2.waitKey(100)  # Allow window to render
        
        # Update global display window info
        g_display_window["name"] = window_name
        g_display_window["index"] = display_index
        g_display_window["x_offset"] = x_offset
        g_display_window["y_offset"] = y_offset
        g_current_image_path["path"] = image_path
        
        print("Image displayed on screen {}".format(display_index))
        
    except Exception as e:
        print("Error displaying image: {}".format(str(e)))

def redraw_image(image_path):
    """
    Redraw an already opened image in the active display window.
    Updates the currently displayed image without closing the window.
    
    :param image_path: Path to the image file to display
    """
    try:
        if not image_path or not os.path.exists(image_path):
            print("Warning: Image file not found: {}".format(image_path))
            return
        
        image = cv2.imread(image_path)
        if image is None:
            print("Warning: Could not read image: {}".format(image_path))
            return
        
        if g_display_window["name"]:
            cv2.imshow(g_display_window["name"], image)
            cv2.waitKey(1)  # Process the display update
            g_current_image_path["path"] = image_path
            print("Image redrawn: {}".format(image_path))
        else:
            print("Display window not active. Cannot redraw image.")
    except Exception as e:
        print("Error redrawing image: {}".format(str(e)))

def destroy_display_windows():
    """
    Destroy all OpenCV windows and update global display state.
    """
    try:
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Process window destruction
        g_display_window["name"] = None
        g_display_window["active"] = False
        g_current_image_path["path"] = None
        time.sleep(0.1)  # Small delay to ensure cleanup
        print("All display windows destroyed")
    except Exception as e:
        print("Error destroying windows: {}".format(str(e)))

def get_display_info(display_index=1):
    """
    Get external screen resolution and offset using xrandr.
    
    :param display_index: 0 for primary, 1 for secondary/external screen
    :return: Tuple of (width, height, x_offset, y_offset)
    """
    try:
        # Run xrandr command to get display information
        result = subprocess.check_output(['xrandr']).decode('utf-8')
        lines = result.strip().split('\n')
        
        displays = []
        current_display = 0
        
        for line in lines:
            if 'connected' in line:
                parts = line.split()
                display_name = parts[0]
                
                # Parse resolution and offset from lines like "HDMI-1 connected 1920x1080+1920+0"
                for part in parts:
                    if 'x' in part and '+' in part:
                        # Format: WIDTHxHEIGHT+XOFFSET+YOFFSET
                        res_part = part.split('+')[0]
                        width, height = map(int, res_part.split('x'))
                        x_offset = int(part.split('+')[1])
                        y_offset = int(part.split('+')[2])
                        displays.append((width, height, x_offset, y_offset))
                        current_display += 1
                        break
        
        # Sort by x_offset to ensure correct order (left to right)
        displays.sort(key=lambda x: x[2])
        
        if len(displays) > display_index:
            return displays[display_index]
        elif displays:
            print("Display index {} not found, using last display".format(display_index))
            return displays[-1]
        else:
            print("No displays detected with xrandr, using default secondary display")
            return (1920, 1080, 1920, 0)
            
    except Exception as e:
        print("Error detecting display info: {}. Using default secondary display".format(str(e)))
        return (1920, 1080, 1920, 0)


def tell_and_show(robot, position, mode="answer"):
    """
    Robot tells the answer or hint and points to the position.
    
    :param robot: instance of the Pepper class
    :param position: Position of the correct answer (1 for right, 2 for left)
    :param mode: "hint" for hint message or "answer" for answer message
    """
    if mode == "hint":
        if position == 1:
            robot.say("I think that correct answer is right picture")
            robot.point_at(1.0, 0.0, 0.0, "RArm", 0)
        elif position == 2:
            robot.say("I think that correct answer is left picture")
            robot.point_at(1.0, 0.0, 0.0, "LArm", 0)
    elif mode == "wrong_hint":
        if position == 1:
            robot.say("I think that correct answer is left picture")
            robot.point_at(1.0, 0.0, 0.0, "LArm", 0)
        elif position == 2:
            robot.say("I think that correct answer is right picture")
            robot.point_at(1.0, 0.0, 0.0, "RArm", 0)
    elif mode == "answer":
        if position == 1:
            robot.say("Which object is different?")
            time.sleep(4)
            robot.say("Correct answer is right picture")
            robot.point_at(1.0, 0.0, 0.0, "RArm", 0)
        elif position == 2:
            robot.say("Which object is different?")
            time.sleep(4)
            robot.say("Correct answer is left picture")
            robot.point_at(1.0, 0.0, 0.0, "LArm", 0)
    elif mode == "late":
        if position == 1:
            robot.say("You are late. Correct answer was right picture")
            robot.point_at(1.0, 0.0, 0.0, "RArm", 0)
        elif position == 2:
            robot.say("Correct answer was left picture")
            robot.point_at(1.0, 0.0, 0.0, "LArm", 0)

def run_trials(robot, path,type="hint"):
    """
    Run the trials loop with keypress/hint/answer timing.

    :param robot: instance of the Pepper class
    :param trials_path: Path to trials file
    """
    trials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    trials = load_trials(trials_path)
    total_trials = min(10, len(trials))

    for index in range(total_trials):
        question, position, image_path = trials[index]
        redraw_image(image_path)
        robot.say(question)
        print("Waiting for keypress or timeout...")
        start_time = time.time()
        hint_shown = False
        answer_shown = False

        while True:
            elapsed = time.time() - start_time

            # After 20 seconds, show answer if not already shown
            if elapsed >= 20 and not answer_shown:
                tell_and_show(robot, position, mode="late")
                answer_shown = True
                break

            # After 5 seconds without keypress, show hint
            if elapsed >= 5 and not hint_shown:
                tell_and_show(robot, position, mode=type)
                hint_shown = True

            # Check for keypress with short timeout (100ms)
            key = cv2.waitKey(100)
            if key != -1 and key != 255:  # Key was pressed
                if not answer_shown:
                    tell_and_show(robot, position, mode="answer")
                    answer_shown = True
                break

        # Wait for keypress before next trial
        redraw_image("trials/background.png")
        time.sleep(3)  # Small delay to ensure answer is processed
        robot.say("Lets go to the next trial")
        time.sleep(3)  # Small delay before next trial starts

def experiment(robot):
    """ HRI exeperiment 2026."""
    destroy_display_windows()  # Ensure no previous windows are open
    display_image_fullscreen("trials/background.png")
    robot.set_english_language()
    robot.reset_tablet()
    robot.set_volume(60)

    #robot.say("Hello, I am Pepper robot.")
    #robot.say("I will make an experiment with you.")

    #robot.greet()
    #robot.say("This experiment is about collaboration.")
    #robot.say("I will give you tasks and help you to solve them.")
    robot.say("We will go through ten trials together.")
    
    #Block 1 - Robot moving/Hint correct
    run_trials(robot, path="block1.txt", type = "hint")
    #Block 2 - Robot moving/Hint wrong
    run_trials(robot, path="block2.txt", type = "wrong_hint")
    #Block 3 - Robot stopped/Hint wrong
    robot.autonomous_life_off()
    run_trials(robot, path="block2.txt", type = "wrong_hint")
    destroy_display_windows()
    robot.say("That was the end of the experiment. Thank you for your participation.")
    robot.autonomous_life_on()

if __name__ == "__main__":
    # Press Pepper's chest button once and he will tell you his IP address
    ip_address = "192.168.0.200"
    port = 9559
    robot = Pepper(ip_address, port)
    experiment(robot)





