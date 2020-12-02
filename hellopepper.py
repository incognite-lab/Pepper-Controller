# -*- coding: utf-8 -*-
from pepper.robot import Pepper
from demoForClass import uploadPhotoToWeb
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
robot.say("Dobrý den, jsem robot pepr.")
robot.start_animation(random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"]))

robot.say("Takto si vás mohu vyfotit svojí kamerou.")
local_img_path = robot.take_picture()

# To display image on tablet, you need to provide URL of the image - i.e., upload the image online
robot.say("Obrázek najdete ve složce projektu. Kdybych ho chtěl ukázat na tabletu, musel bych ho nahrát na internet.")
#photo_link = uploadPhotoToWeb(local_img_path)
#robot.show_image(photo_link)
#time.sleep(3)
#robot.reset_tablet()

robot.say("Takto můžeme na tabletu zobrazit vebovou stránku.")
robot.show_web("https://www.seznam.cz/")
time.sleep(5)
robot.reset_tablet()

robot.say("Chcete, abych vám ukázal, jak funguje rozpoznávání řeči?")
positive_answers = ["ano", "jo", "tak jo", "chci", "chceme", "jasně"]
vocab = positive_answers + ["ne", "nechci", "nechceme", "nevím", "hm"]
answer = robot.listen_to(vocabulary=vocab)

if answer[0] in positive_answers:
     robot.say("Dobře.. pro rozpoznání libovolných promluv použijeme knihovnu od gůglu. Vyjmenujte prosím roční období.")
     recognised = robot.recordSound()
     robot.say("Rozpoznal jsem {}".format(recognised.encode('utf-8')))
else: robot.say("Dobře.")

while True:
    robot.say("Dotkněte se nyní hřbetu mojí pravé ruky.")
    touched_sensor = robot.detect_touch()
    if touched_sensor[0] == "RArm":
        robot.say("Super. Tak takhle se dá detekovat dotyk.")
        break
    else:
        robot.say("Teď jste se dotkli jiného senzoru.")

robot.say("Poslední důležitá věc je přepínání mezi autonomním režimem. Teď ho mám zapnutý a díky tomu jsem interaktivní. Pokud "
          "bych se ale měl třeba hýbat, je třeba autonomní režim vypnout, aby mě nemátl.")
robot.autonomous_life_off()
robot.say("A je to.", bodylanguage="disabled")
robot.move_joint_by_angle(["LShoulderRoll", "LShoulderPitch", "RShoulderRoll", "RShoulderPitch"], [-2.9,-1, -2.9, -1], 0.4)
time.sleep(2)
robot.stand()
robot.autonomous_life_on()





