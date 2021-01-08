# -*- coding: utf-8 -*-
from pepper.robot import Pepper
from demo import uploadPhotoToWeb
import random, os, time

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


# Press Pepper's chest button once and he will tell you his IP address
ip_address = "10.37.1.100"
port = 9559
robot = Pepper(ip_address, port)

robot.set_volume(50)
robot.say("Hello, I am Pepper robot.")
robot.start_animation(random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"]))

robot.say("I can make your photograph.")
local_img_path = robot.take_picture()

# To display image on tablet, you need to provide URL of the image - i.e., upload the image online
robot.say("The picture will be saved in the project folder.")
#photo_link = uploadPhotoToWeb(local_img_path)
#robot.show_image(photo_link)
#time.sleep(3)
#robot.reset_tablet()

robot.say("I can also show the internet page on my tablet.")
robot.show_web("https://www.google.com/")
time.sleep(5)
robot.reset_tablet()

robot.say("Do you want to see how I can recognize language?")
positive_answers = ["yes", "yep", "ok", "i want", "sure", "definitely"]
vocab = positive_answers + ["no", "not", "i dont", "i do not know", "not sure"]
answer = robot.listen_to(vocabulary=vocab)

if answer[0] in positive_answers:
     robot.say("Ok, now you have to count up to five")
     recognised = robot.recordSound()
     robot.say("I recognized {}".format(recognised.encode('utf-8')))
else: robot.say("Cool.")

while True:
    robot.say("Touch my right palm.")
    touched_sensor = robot.detect_touch()
    if touched_sensor[0] == "RArm":
        robot.say("Perfect, I can detect touch.")
        break
    else:
        robot.say("Now you touched different part of my body.")

robot.say("The last important thing is to switch between autonomous mode. Now I have it turned on and thanks to that I'm interactive. If "
          "I should move, the autonomous regime needs to be turned off so that it doesn't confuse me.")
robot.autonomous_life_off()
robot.say("Thats it.", bodylanguage="disabled")
robot.move_joint_by_angle(["LShoulderRoll", "LShoulderPitch", "RShoulderRoll", "RShoulderPitch"], [-2.9,-1, -2.9, -1], 0.4)
time.sleep(2)
robot.stand()
robot.autonomous_life_on()





