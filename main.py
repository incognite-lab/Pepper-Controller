#!/usr/bin/python
# -*- coding: utf-8 -*-
from Tkinter import *

import cv2
import yaml
from PIL import ImageTk, Image

from pepper.robot import Pepper
import numpy as np
import demoForClass as foto


class Configuration:

    def __init__(self, config_file="./conf.yaml"):
        self.config_file = config_file
        self.conf = yaml.safe_load(open(self.config_file))


class PepperController:

    def __init__(self, root):
        self.configuration = Configuration()
        self.robot = None
        self.language = self.configuration.conf["language"]["lang"]

        self.root = root
        self.root.option_add('*Font', 'Arial 12')
        self.root.geometry("1000x800")
        self.root.title("Pepper Controller " + self.configuration.conf["configuration"]["version"])
        self.root.bind('<Escape>', lambda e: root.destroy())
        self.root.resizable(True, True)
        self.root.configure(background='#F0E68C')

        '''System customization'''
        self.group_connection = LabelFrame(root, text="Připojení")
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
        self.label_address = Label(self.group_connection, text="IP adresa")
        self.label_port = Label(self.group_connection, text="Port")
        self.button_connect = Button(self.group_connection, text="Připojit", command=self.connect)

        self.label_address.grid(row=0, column=0, sticky="nse")
        self.entry_address.grid(row=0, column=1)
        self.label_port.grid(row=1, column=0, sticky="nse")
        self.entry_port.grid(row=1, column=1)
        self.button_connect.grid(row=1, column=2)

        self.set_colour_for_frame([self.group_connection, self.label_address, self.label_port], [self.button_connect])

        self.group_system = LabelFrame(root, text="Systém", width=340, height=125)
        self.group_system.grid_propagate(False)
        self.group_system.grid(columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_system.place(x=5, y=100)

        self.button_switch_al = Button(self.group_system, text="Autonomní režim",
                                       command=lambda: self.robot.autonomous_life(),
                                       width=15)
        self.button_battery = Button(self.group_system, text="Stav baterie",
                                     command=lambda: self.robot.battery_status(), width=15)
        self.button_stop_all = Button(self.group_system, text="Ukonči aplikace",
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

        self.group_application = LabelFrame(root, text="Aplikace")
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
        self.button_app_9 = Button(self.group_application, text=self.configuration.conf["application_9"]["name"],
                                   command=lambda: self.robot.start_behavior(
                                       self.configuration.conf["application_9"]["package"]))
        self.button_app_10 = Button(self.group_application, text=self.configuration.conf["application_10"]["name"],
                                    command=lambda: self.robot.start_behavior(
                                        self.configuration.conf["application_10"]["package"]))
        self.button_app_11 = Button(self.group_application, text="Foto",
                                    command=lambda: foto.PepperDemo(None, self.robot).run())
        self.button_app_12 = Button(self.group_application, text="Tancuj",
                                    command=lambda: self.robot.dance())

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

        self.group_language = LabelFrame(root, text="Mluvení")
        self.group_language.grid(row=1, column=20, columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_language.place(x=5, y=270)

        self.language_button_cz = Button(self.group_language, text="Nastav češtinu",
                                         command=lambda: self.change_language("cz"))
        self.language_button_en = Button(self.group_language, text="Nastav angličtinu",
                                         command=lambda: self.change_language("en"))
        self.button_say_no = Button(self.group_language, text="Ne", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["no_list"]).encode("utf-8"))))
        self.button_say_yes = Button(self.group_language, text="Ano",
                                     command=lambda: self.robot.say(
                                         str(np.random.choice(
                                             self.configuration.conf["language"][self.language]["yes_list"]).encode(
                                             "utf-8"))))
        self.button_say_dont_know = Button(self.group_language, text="Nevím", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["dont_know_list"]).encode("utf-8"))))
        self.button_say_hello = Button(self.group_language, text="Pozdrav", command=lambda: self.robot.say(
            str(np.random.choice(
                self.configuration.conf["language"][self.language]["hello"]).encode("utf-8"))))
        self.button_say_welcome = Button(self.group_language, text="Vítej", command=lambda: self.robot.say(
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

        self.voice_shaping_scale = Scale(self.root, from_=0, to=200, orient=HORIZONTAL, label="Výška hlasu", length=115)
        self.voice_speed_scale = Scale(self.root, from_=0, to=200, orient=HORIZONTAL, label="Rychlost hlasu", length=115)
        self.voice_volume_scale = Scale(self.root, from_=0, to=100, orien=HORIZONTAL, label="Hlasitost", length=115)
        self.button_confirm = Button(self.root, text="OK", command=lambda: self.robot.changeVoice(
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
        self.button_say_custom_text = Button(self.root, text="Říct text", command=lambda: self.robot.say(
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
        '''motorika'''
        self.group_motorics = LabelFrame(root, text="Motorika")
        self.group_motorics.grid(row=1, column=20, columnspan=16, rowspan=2, padx=5, pady=5)
        self.group_motorics.place(x=450, y=180)
        self.button_wave = Button(self.group_motorics, text="Zamávej", command=lambda: self.robot.start_animation(
            np.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"])))
        self.button_stay = Button(self.group_motorics, text="Stůj", command=lambda: self.robot.stand())
        self.button_rest = Button(self.group_motorics, text="Blikání",
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
        '''
        camera
        lmain = Label(self.root)
        lmain.grid()
        cap = cv2.VideoCapture(0)
        self.video_stream(lmain, cap)
        '''
        self.button_obraz = Button(self.root, text="Obraz", command=lambda: self.robot.streamCamera(), width=7, height=2)
        self.button_obraz.place(x=450, y=260)

        self.set_colour_for_frame([], [self.button_obraz])


    def video_stream(self, lmain, cap):
        _, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(1, self.video_stream)

    def drawLines(self, x, y, len, vertical):
        if vertical:
            verticalLine = Frame(self.root, bg='red', height=len,
                                 width=2)
            verticalLine.place(x=x, y=y)
        else:
            horizontalLine = Frame(self.root, bg='red', height=2,
                                   width=len)
            horizontalLine.place(x=x, y=y)

    def set_colour_for_frame(self, objects_light, objects_dark):
        for o in objects_light:
            o.configure(background='#FFD700')

        for o in objects_dark:
            o.configure(background='#EC9800')

    def connect(self):
        ip_address = self.entry_address.get()
        port = self.entry_port.get()
        self.robot = Pepper(ip_address, port)
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
