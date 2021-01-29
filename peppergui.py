#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import base64
import json
import random
import time
from Tkinter import *

import cv2
import numpy
import yaml
from PIL import ImageTk, Image

from pepper.robot import Pepper
import numpy as np
from hellopepper import basic_demo, take_picture_show, recognize_person, learn_person
import threading


class Configuration:

    def __init__(self, config_file="./conf.yaml"):
        self.config_file = config_file
        self.conf = yaml.safe_load(open(self.config_file))


class PepperController:

    def __init__(self, root):
        self.configuration = Configuration()
        self.robot = None
        self.ip_address = None
        self.port = None
        self.language = self.configuration.conf["language"]["lang"]

        self.root = root
        self.root.option_add('*Font', 'Arial 12')
        self.root.geometry("1000x800")
        self.root.title("Pepper Controller " + self.configuration.conf["configuration"]["version"])
        self.root.bind('<Escape>', lambda e: root.destroy())
        self.root.resizable(True, True)
        self.root.configure(background='#EFF5FB')

        '''System customization'''
        self.group_connection = LabelFrame(root, text="Connection")
        self.group_connection.grid(row=0, column=0, columnspan=4, rowspan=2, padx=5, pady=5)
        self.group_connection.place(x=5, y=10)
        self.entry_address = Entry(self.group_connection)
        self.entry_port = Entry(self.group_connection)
        if self.configuration.conf["configuration"]["virtual"]:
            self.entry_address.insert(END, "localhost")
            self.entry_port.insert(END, "34223")
        else:
            self.entry_address.insert(END, self.configuration.conf["configuration"]["default_ip"])
            self.entry_port.insert(END, self.configuration.conf["configuration"]["default_port"])
        self.label_address = Label(self.group_connection, text="IP adress")
        self.label_port = Label(self.group_connection, text="Port")
        self.button_connect = Button(self.group_connection, text="Connect", command=self.connect)

        self.label_address.grid(row=0, column=0, sticky="nse")
        self.entry_address.grid(row=0, column=1)
        self.label_port.grid(row=1, column=0, sticky="nse")
        self.entry_port.grid(row=1, column=1)
        self.button_connect.grid(row=1, column=2)

        self.set_colour_for_frame([self.group_connection, self.label_address, self.label_port], [self.button_connect])

        self.group_system = LabelFrame(root, text="System", width=340, height=125)
        self.group_system.grid_propagate(False)
        self.group_system.grid(columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_system.place(x=5, y=100)

        self.button_switch_al = Button(self.group_system, text="Autonomous life",
                                       command=lambda: self.robot.autonomous_life(),
                                       width=15)
        self.button_battery = Button(self.group_system, text="Battery level",
                                     command=lambda: self.robot.battery_status(), width=15)
        self.button_stop_all = Button(self.group_system, text="Close app",
                                      command=lambda: self.robot.stop_behaviour(), width=16)
        self.button_web_reset = Button(self.group_system, text="Reset tablet",
                                       command=lambda: self.robot.reset_tablet())
        self.awareness_on = Button(self.group_system, text="Awareness On",
                                   command=lambda: self.robot.set_awareness(on=True))
        self.awareness_off = Button(self.group_system, text="Awareness Off",
                                    command=lambda: self.robot.set_awareness(on=False))

        self.button_switch_al.grid(row=0, column=0, sticky=EW)
        self.button_web_reset.grid(row=0, column=1, sticky=EW)
        self.awareness_off.grid(row=1, column=0, sticky=EW)
        self.awareness_on.grid(row=1, column=1, sticky=EW)
        self.button_stop_all.grid(row=2, column=0, sticky=EW)
        self.button_battery.grid(row=2, column=1, sticky=EW)

        self.set_colour_for_frame([self.group_system],
                                  [self.button_switch_al,
                                   self.button_stop_all,
                                   self.button_battery,
                                   self.button_web_reset,
                                   self.awareness_off,
                                   self.awareness_on
                                   ]
                                  )

        self.group_application = LabelFrame(root, text="Aplications")
        self.group_application.grid(row=1, column=20, columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_application.place(x=450, y=10)

        self.button_app_1 = Button(self.group_application, text=self.configuration.conf["application_1"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_1"]["package"]))
        self.button_app_2 = Button(self.group_application, text=self.configuration.conf["application_2"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_2"]["package"]))
        self.button_app_3 = Button(self.group_application, text=self.configuration.conf["application_3"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_3"]["package"]))
        self.button_app_4 = Button(self.group_application, text=self.configuration.conf["application_4"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_4"]["package"]))
        self.button_app_5 = Button(self.group_application, text=self.configuration.conf["application_5"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_5"]["package"]))
        self.button_app_6 = Button(self.group_application, text=self.configuration.conf["application_6"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_6"]["package"]))
        self.button_app_7 = Button(self.group_application, text=self.configuration.conf["application_7"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_7"]["package"]))
        self.button_app_8 = Button(self.group_application, text=self.configuration.conf["application_8"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_8"]["package"]))
        self.button_app_9 = Button(self.group_application, text="Learn face",
                                   command=lambda: learn_person(self.robot, self.language))
        self.button_app_10 = Button(self.group_application, text="Recognize human",
                                    command=lambda: recognize_person(self.robot, self.language))
        self.button_app_11 = Button(self.group_application, text="Take a Picture",
                                    command=lambda: take_picture_show(self.robot))
        self.button_app_12 = Button(self.group_application, text="Basic Demo",
                                    command=lambda: basic_demo(self.robot))

        self.button_app_1.grid(row=0, column=1, sticky=NSEW)
        self.button_app_2.grid(row=0, column=2, sticky=NSEW)
        self.button_app_3.grid(row=0, column=3, sticky=NSEW)
        self.button_app_4.grid(row=0, column=4, sticky=NSEW)
        self.button_app_5.grid(row=1, column=1, sticky=NSEW)
        self.button_app_6.grid(row=1, column=2, sticky=NSEW)
        self.button_app_7.grid(row=1, column=3, sticky=NSEW)
        self.button_app_8.grid(row=1, column=4, sticky=NSEW)
        self.button_app_9.grid(row=2, column=1, sticky=NSEW)
        self.button_app_10.grid(row=2, column=2, sticky=NSEW)
        self.button_app_11.grid(row=2, column=3, sticky=NSEW)
        self.button_app_12.grid(row=2, column=4, sticky=NSEW)

        self.set_colour_for_frame([self.group_application],
                                  [self.button_app_1,
                                   self.button_app_2,
                                   self.button_app_3,
                                   self.button_app_4,
                                   self.button_app_5,
                                   self.button_app_6,
                                   self.button_app_7,
                                   self.button_app_8,
                                   self.button_app_9,
                                   self.button_app_10,
                                   self.button_app_11,
                                   self.button_app_12,
                                   ]
                                  )

        self.group_language = LabelFrame(root, text="Language")
        self.group_language.grid(row=1, column=20, columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_language.place(x=5, y=270)

        self.language_button_cz = Button(self.group_language, text="Czech language",
                                         command=lambda: self.change_language("cz"))
        self.language_button_en = Button(self.group_language, text="English language",
                                         command=lambda: self.change_language("en"))
        self.button_say_no = Button(self.group_language, text="No", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["no_list"]).encode("utf-8"))))
        self.button_say_yes = Button(self.group_language, text="Yes",
                                     command=lambda: self.robot.say(
                                         str(np.random.choice(
                                             self.configuration.conf["language"][self.language]["yes_list"]).encode(
                                             "utf-8"))))
        self.button_say_dont_know = Button(self.group_language, text="I don't know", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["dont_know_list"]).encode("utf-8"))))
        self.button_say_hello = Button(self.group_language, text="Greetings", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["hello"]).encode("utf-8"))))
        self.button_say_welcome = Button(self.group_language, text="Welcome", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["welcome"]).encode("utf-8"))))
        self.entry_say_text = Entry(self.group_language)
        self.entry_say_text.insert(END, self.configuration.conf["configuration"]["default_sentence"])

        self.language_button_cz.grid(row=0, column=0, sticky=EW)
        self.language_button_en.grid(row=0, column=1, sticky=EW)
        self.button_say_hello.grid(row=0, column=2, sticky=EW)
        self.button_say_no.grid(row=1, column=0, sticky=EW)
        self.button_say_yes.grid(row=1, column=1, sticky=EW)
        self.button_say_dont_know.grid(row=1, column=2, sticky=EW)

        self.voice_shaping_scale = Scale(self.root, from_=0, to=200, orient=HORIZONTAL, label="Voice pitch", length=115)
        self.voice_speed_scale = Scale(self.root, from_=0, to=200, orient=HORIZONTAL, label="Voice speed", length=115)
        self.voice_volume_scale = Scale(self.root, from_=0, to=100, orien=HORIZONTAL, label="Volume", length=115)
        self.button_confirm = Button(self.root, text="Ok", command=lambda: self.robot.changeVoice(
            self.voice_volume_scale.get(), self.voice_speed_scale.get(), self.voice_shaping_scale.get()), height=2,width=3)

        self.voice_speed_scale.place(x=5, y=380)
        self.voice_shaping_scale.place(x=130, y=380)
        self.voice_volume_scale.place(x=255, y=380)
        self.button_confirm.place(x=375, y=385)

        self.entry_gr = LabelFrame(root, text="")
        self.entry_say_text = Entry(self.entry_gr, width=45, bd=7)
        self.entry_say_text.grid_propagate(False)
        self.entry_say_text.insert(END, self.configuration.conf["configuration"]["default_sentence"])
        self.entry_gr.place(x=5, y=470)
        self.entry_say_text.grid(row=0,column=0,ipady=20)
        self.button_say_custom_text = Button(self.root, text="Say text", command=lambda: self.robot.say(
            self.entry_say_text.get().encode("utf-8")), width=10, height=2)
        self.button_say_custom_text.place(x=120, y=560)

        self.set_colour_for_frame([self.group_language, self.entry_say_text],
                                  [self.language_button_cz,
                                   self.language_button_en,
                                   self.language_button_cz,
                                   self.language_button_en,
                                   self.button_say_hello,
                                   self.button_say_no,
                                   self.button_say_yes,
                                   self.button_say_dont_know,
                                   self.voice_speed_scale,
                                   self.voice_shaping_scale,
                                   self.voice_volume_scale,
                                   self.button_confirm,
                                   self.button_say_custom_text
                                   ]
                                  )
        '''Motorics'''
        self.group_motorics = LabelFrame(root, text="Motorics")
        self.group_motorics.grid(row=1, column=20, columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_motorics.place(x=450, y=180)
        self.button_wave = Button(self.group_motorics, text="Wave hand", command=lambda: self.robot.start_animation(
            np.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"])))
        self.button_stay = Button(self.group_motorics, text="Stay", command=lambda: self.robot.stand())
        self.button_rest = Button(self.group_motorics, text="Blink",
                                  command=lambda: self.robot.autonomous_blinking())

        self.button_wave.grid(row=0, column=0, sticky=EW)
        self.button_stay.grid(row=0, column=1, sticky=EW)
        self.button_rest.grid(row=0, column=2, sticky=EW)

        self.set_colour_for_frame([self.group_motorics],
                                  [self.button_wave,
                                   self.button_rest,
                                   self.button_stay
                                   ]
                                  )

        self.drawLines(x=440, y=0, len=1000, vertical=True)
        self.drawLines(x=0, y=250, len=440, vertical=False)
        self.drawLines(x=440, y=170, len=560, vertical=False)
        self.drawLines(x=440, y=250, len=560, vertical=False)

        x = threading.Thread(target=self.streamVideo)
        #y = threading.Thread(target=self.streamTablet)
        self.button_stream = Button(self.root, text="Camera Stream", command=lambda: x.start(), width=12, height=2)
        self.button_stream.place(x=450, y=260)

    def getRandName(self):
        randNum = random.randint(0, 1000)
        return "demoPictures/photo" + str(randNum) + ".png"

    def uploadPhotoToWeb(self, photo):
        f = open(photo, "rb")  # open our image file as read only in binary mode
        image_data = f.read()  # read in our image file
        b64_image = base64.standard_b64encode(image_data)
        client_id = "af482612ae6d1c1"  # this the id which we've got after registrating the app on imgur
        headers = {'Authorization': 'Client-ID ' + client_id}
        data = {'image': b64_image, 'title': 'test'}
        request = urllib2.Request(url="https://api.imgur.com/3/upload.json", data=urllib.urlencode(data),
                                  headers=headers)
        response = urllib2.urlopen(request).read()
        parse = json.loads(response)
        return parse['data']['link']  # returns a url of the photo

    def showPicture(self):
        link = self.uploadPhotoToWeb(self.photoName)
        self.robot.show_image(link)
        time.sleep(5)
        self.robot.reset_tablet()

    def takePicture(self):
        self.robot.subscribe_camera("camera_top", 2, 30)
        img = self.robot.get_camera_frame(show=False)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.robot.unsubscribe_camera()
        self.robot.play_sound("/home/nao/camera1.ogg")
        im = Image.fromarray(img)
        self.photoName = self.getRandName()
        im.save(self.photoName)

    def pictureToTablet(self):
        self.takePicture()
        self.showPicture()

    def streamVideo(self):
        self.robot.subscribe_camera("camera_top", 2, 30)
        while True:
            image = self.robot.get_camera_frame(show=False)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(image)
            name = "camera.jpg"
            im.save(name)
            load = Image.open(name)
            try:
                render = ImageTk.PhotoImage(load)
                img = Label(self.root, image=render)
                img.image = render
                img.place(x=450, y=350)
            except:
                print ("The application has finished")
                break

    def streamTablet(self):
        self.robot.subscribe_camera("camera_top", 2, 30)
        while True:
            self.robot.show_tablet_camera(text="")


    def drawLines(self, x, y, len, vertical):
        if vertical:
            verticalLine = Frame(self.root, bg='black', height=len,
                                 width=2)
            verticalLine.place(x=x, y=y)
        else:
            horizontalLine = Frame(self.root, bg='black', height=2,
                                   width=len)
            horizontalLine.place(x=x, y=y)

    def set_colour_for_frame(self, objects_light, objects_dark):
        for o in objects_light:
            o.configure(background='#EFF5FB')

        for o in objects_dark:
            o.configure(background='#FFFFFF')

    def connect(self):
        self.ip_address = self.entry_address.get()
        self.port = self.entry_port.get()
        self.robot = Pepper(self.ip_address, self.port)
        self.change_language(self.language)
        self.setScales()

    def invitation(self):
        self.robot.show_image(self.configuration.conf["configuration"]["pozvanka"])
        self.robot.say(str(
            np.random.choice(self.configuration.conf["language"][self.language]["invitation_morning"]).encode("utf-8")))

    def change_language(self, lang):
        fncts = {"cz": self.robot.set_czech_language, "en": self.robot.set_english_language}
        fncts[lang]()
        self.language = lang

    def setScales(self):
        self.voice_speed_scale.set(self.robot.getVoiceSpeed())
        self.voice_shaping_scale.set(self.robot.getVoiceShape())
        self.voice_volume_scale.set(self.robot.getVoiceVolume())


if __name__ == "__main__":
    application = Tk()
    PepperController(application)
    application.mainloop()
