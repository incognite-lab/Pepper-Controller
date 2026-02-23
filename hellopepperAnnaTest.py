# -*- coding: utf-8 -*-
from pepper.robot import Pepper
from demo import uploadPhotoToWeb
import random, os, time
import qi

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

def basic_demo(robot):
    """ Shows how to work with the Pepper class and how to use the basic functions."""
    robot.set_english_language()
    robot.set_volume(50)
    robot.say("Hello, I am Pepper robot. This is a demo for upcoming experiment.")
    #robot.start_animation(random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"]))

    robot.say("First, I will try to recognize you. If I know you, I will greet you by your name. If not, I will say that I don't know you yet.")



    robot.say("The last important thing is to switch between autonomous mode. Now it is turned on and thanks to that I'm interactive. If "
              "I should move, the autonomous regime needs to be turned off so that it doesn't confuse me.")
    #robot autonimous life is off
    robot.autonomous_life_off()
    #contextual gestures off when bodylanguage is disabled
    robot.say("Thats it.My Autonimous life is off and contextual gestures is disabled ", 
    bodylanguage="disabled")


    robot.move_joint_by_angle(["LShoulderRoll", "LShoulderPitch", "RShoulderRoll", "RShoulderPitch"], [-2.9,-1, -2.9, -1], 0.4)
    time.sleep(2)
    robot.stand()
    robot.autonomous_life_on()


if __name__ == "__main__":
    # Press Pepper's chest button once and he will tell you his IP address
    ip_address = "192.168.0.200"
    port = 9559
    
    robot = Pepper(ip_address, port)
    basic_demo(robot)





