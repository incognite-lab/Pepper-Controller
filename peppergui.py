# -*- coding: utf-8 -*-
from motion_parser import MotionParser
import os
try:
  import Tkinter as tk
  import ttk
except:
    import tkinter as tk
    import tkinter.ttk as ttk
import pygubu
from PIL import Image, ImageTk
from pepper.robot import Pepper
import numpy as np
import yaml
import cv2
import threading
from hellopepper import basic_demo, take_picture_show, recognize_person, learn_person
import subprocess
import random

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_UI = os.path.join(PROJECT_PATH, "pepper_controller.ui")


class Configuration:

    def __init__(self, config_file=os.path.join(PROJECT_PATH,"conf.yaml")):
        self.config_file = config_file
        self.conf = yaml.safe_load(open(self.config_file))


class PepperControllerApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('toplevel1', master)

        # pygubu variables
        self.move_speed = None
        self.text_to_say = None
        self.volume = None
        self.voice_pitch = None
        self.voice_speed = None
        self.ipaddress = None
        self.port = None
        builder.import_variables(self, [u'move_speed', u'text_to_say',
                                        u'volume', u'voice_pitch', u'voice_speed', u'ipaddress', u'port'])

        builder.connect_callbacks(self)

        # robot properties
        self.configuration = Configuration()
        self.robot = None
        self.ip_address = None
        self.port = None
        self.language = self.configuration.conf["language"]["lang"]

        # default settings
        self.builder.tkvariables['ipaddress'].set(
            self.configuration.conf["configuration"]["default_ip"])
        self.builder.tkvariables['port'].set(
            self.configuration.conf["configuration"]["default_port"])
        self.builder.tkvariables['text_to_say'].set(
            self.configuration.conf["configuration"]["default_sentence"])

        # title
        top_level = self.builder.get_object('toplevel1')
        self.top_level = top_level
        top_level.title("Pepper Controller " +
                        self.configuration.conf["configuration"]["version"])

        # gesture names:
        i = 1
        while True:
            try:
                button = self.builder.get_object('gesture_' + str(i))
                name = self.configuration.conf["gesture_" + str(i)]["name"]
                button.config(text=name)
                i += 1
            except:
                break

        # app names
        i = 1
        while True:
            try:
                button = self.builder.get_object('application_' + str(i))
                name = self.configuration.conf["application_" + str(i)]["name"]
                button.config(text=name)
                i += 1
            except:
                break

        # video properties
        self.canvas = builder.get_object('canvas1')
        self.video_thread = threading.Thread(target=self.start_stream)
        self._stop_event = threading.Event()
        #self.thread_alive = False
        self.stream_on = -1  # -1 == initial, 0 == off, 1 == on

        # movement
        self.movement_state = "stop"

        self.motorics = self.builder.get_object('motorics')

        # close action
        top_level.protocol("WM_DELETE_WINDOW", self.on_closing)

        # pick camera settings
        self.builder.get_object('pick_camera').current(0)

        # workout settings
        self.arms_combobox = self.builder.get_object('arms_submove')
        self.torso_combobox = self.builder.get_object('torso_submove')
        self.head_combobox = self.builder.get_object('head_submove')

        reps = self.builder.get_object('reps').get()
        reps_label = self.builder.get_object('reps_label')
        reps_label.config(text="Reps: " + str(int(float(reps))))

    def run(self):
        self.mainwindow.mainloop()

    def on_closing(self):
        """ Close operation. """
        # self.stream_on = 0
        #self.thread_alive = False
        
        self._stop_event.set()
        #self.video_thread.join()
        
        #time.sleep(10)
        # print("tu")
        # while self.video_thread.is_alive():
        #     self.video_thread.join()
        # print("over")
        self.top_level.destroy()

    def output_text(self, text):
        """ Write to GUI console. """
        output = self.builder.get_object('output')
        output.config(text=text)

    def change_language(self, lang):
        fncts = {"cz": self.robot.set_czech_language,
                 "en": self.robot.set_english_language}
        fncts[lang]()
        self.language = lang

    # key and mouse callbacks
    def on_motorics_clicked(self, even=None):  # take focus
        self.motorics.focus_set()

    def on_w_pressed(self, event=None):
        self.on_forward_clicked()

    def on_a_pressed(self, event=None):
        self.on_left_clicked()

    def on_s_pressed(self, event=None):
        self.on_backward_clicked()

    def on_d_pressed(self, event=None):
        self.on_right_clicked()

    def on_space_pressed(self, event=None):
        self.on_stop_clicked()

    # widget callbacks

    def on_connect_clicked(self):
        PepperIP = self.builder.tkvariables['ipaddress'].get()
        port = self.builder.tkvariables['port'].get()
        if self.robot == None:
            self.ip_address = PepperIP
            self.port = port
            self.robot = Pepper(self.ip_address, self.port)
            self.change_language(self.language)
            self.set_scales()
            # auto life setup
            state = self.robot.autonomous_life_service.getState()
            label = self.builder.get_object('auto_life')
            if state == "disabled":
                label.config(text="Auto Life: OFF")
                self.output_text("[INFO]: Autonomous life off.")
            else:
                label.config(text="Auto Life: ON")
                self.output_text("[INFO]: Autonomous life on.")
            self.output_text("[INFO]: Robot is initialized at " +
                             self.ip_address + ":" + str(port))
            # motion parser
            self.mp = MotionParser(os.path.join(PROJECT_PATH,"workout_conf.json"), self.robot)
            self.arms_combobox['values'] = self.mp.get_conf(
            )["positions"]["arms"]["data_list"].keys()
            self.head_combobox['values'] = self.mp.get_conf(
            )["positions"]["head"]["data_list"].keys()
            self.torso_combobox['values'] = self.mp.get_conf(
            )["positions"]["torso"]["data_list"].keys()
            self.work_dict = {"short_neck": random.sample(range(len(self.mp.get_conf()["workouts"]["short_neck"])), len(self.mp.get_conf()["workouts"]["short_neck"])),
                              "short_arms": random.sample(range(len(self.mp.get_conf()["workouts"]["short_arms"])), len(self.mp.get_conf()["workouts"]["short_arms"])),
                              "short_torso": random.sample(range(len(self.mp.get_conf()["workouts"]["short_torso"])), len(self.mp.get_conf()["workouts"]["short_torso"])),
                              "short_shoulders": random.sample(range(len(self.mp.get_conf()["workouts"]["short_shoulders"])), len(self.mp.get_conf()["workouts"]["short_shoulders"]))
                              }
            #print(self.work_dict)
        else:
            self.output_text("[INFO]: Already connected to " + self.ip_address)

    def on_czech_clicked(self):
        self.output_text("[INFO]: Language changed to czech.")
        self.change_language("cz")

    def on_english_clicked(self):
        self.change_language("en")
        self.output_text("[INFO]: Language changed to english.")

    def on_blink_clicked(self):
        self.robot.autonomous_blinking()
        self.output_text("[INFO]: Changed blinking.")

    def on_stay_clicked(self):
        self.robot.stand()
        self.output_text("[INFO]: Robot is in default position.")

    def on_wave_clicked(self):
        self.robot.start_animation(
            np.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"]))
        self.output_text("[INFO]: Waving animation.")

    def on_say_clicked(self):
        text_to_say = self.builder.tkvariables['text_to_say'].get()
        self.robot.say(text_to_say.encode("utf-8"))
        self.output_text("[INFO]: Saying \'" + text_to_say + "\'")

    def on_yes_clicked(self):
        text_list = self.configuration.conf["language"][self.language]["yes_list"]
        text = np.random.choice(text_list).encode("utf-8")
        self.robot.say(text)
        self.output_text("[INFO]: Saying yes.")

    def on_no_clicked(self):
        text_list = self.configuration.conf["language"][self.language]["no_list"]
        text = np.random.choice(text_list).encode("utf-8")
        self.robot.say(text)
        self.output_text("[INFO]: Saying no.")

    def on_greet_clicked(self):
        text_list = self.configuration.conf["language"][self.language]["hello"]
        text = np.random.choice(text_list).encode("utf-8")
        self.robot.say(text)
        self.output_text("[INFO]: Greeting.")

    def on_idk_clicked(self):
        text_list = self.configuration.conf["language"][self.language]["dont_know_list"]
        text = np.random.choice(text_list).encode("utf-8")
        self.robot.say(text)
        self.output_text("[INFO]: Saying I don\'t know.")

    def start_stream(self):
        self.robot.subscribe_camera(self.get_picked_camera(), 0, 30)
        #self.thread_alive = True
        while not self._stop_event.is_set():
            #print(self.thread_alive)
            if not self.stream_on == 1:
                self._stop_event.wait(1)
                continue
            image = self.robot.get_camera_frame(show=False)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (320, 240))
            im = Image.fromarray(image)
            #name = "camera.jpg"
            #im.save(name)
            try:
                # Load image in canvas
                #fpath = os.path.join(PROJECT_PATH, 'camera.jpg')
                #aux = Image.open(fpath)
                #aux = aux.resize((320, 240), Image.ANTIALIAS)
                #self.img = ImageTk.PhotoImage(aux)
                self.img = ImageTk.PhotoImage(im)
                self.canvas.create_image(0, 0, image=self.img, anchor='nw')
            except:
                print("The application has finished")
                break
            
        #print("thread alive " + str(self.thread_alive))

    def on_start_stream_clicked(self):
        self.output_text("[INFO]: Starting camera stream.")
        if self.stream_on == -1:
            self.stream_on = 1
            self.video_thread.start()
        else:
            self.stream_on = 1

    def on_stop_stream_clicked(self):
        self.output_text("[INFO]: Stopping camera stream.")
        self.stream_on = 0

    def on_left_clicked(self):
        koeff = self.builder.tkvariables['move_speed'].get()
        if self.movement_state != "left":
            self.robot.motion_service.stopMove()
            self.robot.turn_around(0.55*koeff)
            self.movement_state = "left"
        self.output_text("[INFO]: Turn left.")

    def on_right_clicked(self):
        koeff = self.builder.tkvariables['move_speed'].get()
        if self.movement_state != "right":
            self.robot.motion_service.stopMove()
            self.robot.turn_around(-0.55*koeff)
            self.movement_state = "right"
        self.output_text("[INFO]: Turn right.")

    def on_forward_clicked(self):
        koeff = self.builder.tkvariables['move_speed'].get()
        if self.movement_state != "forw":
            self.robot.motion_service.stopMove()
            self.robot.move_forward(0.2*koeff)
            self.movement_state = "forw"
        self.output_text("[INFO]: Move forward.")

    def on_backward_clicked(self):
        koeff = self.builder.tkvariables['move_speed'].get()
        if self.movement_state != "back":
            self.robot.motion_service.stopMove()
            self.robot.move_forward(-0.2*koeff)
            self.movement_state = "back"
        self.output_text("[INFO]: Move backward.")

    def on_stop_clicked(self):
        self.movement_state = "stop"
        self.robot.motion_service.stopMove()
        self.output_text("[INFO]: Stopping movement.")

    def on_auto_life_clicked(self):
        self.robot.autonomous_life()
        state = self.robot.autonomous_life_service.getState()
        label = self.builder.get_object('auto_life')
        if state == "disabled":
            label.config(text="Auto Life: OFF")
            self.output_text("[INFO]: Autonomous life off.")
        else:
            label.config(text="Auto Life: ON")
            self.output_text("[INFO]: Autonomous life on.")

    def on_reset_tablet_clicked(self):
        self.robot.reset_tablet()
        self.output_text("[INFO]: Reseting tablet.")

    def on_aware_on_clicked(self):
        self.robot.set_awareness(on=True)
        self.output_text("[INFO]: Awarness on.")

    def on_aware_off_clicked(self):
        self.robot.set_awareness(on=False)
        self.output_text("[INFO]: Awarness off.")

    def on_close_app_clicked(self):
        self.robot.stop_behaviour()
        self.output_text("[INFO]: Stopping all behaviour.")

    def on_battery_level_clicked(self):
        self.robot.battery_status()
        self.output_text("[INFO]: Saying my battery level.")

    def on_app_clicked(self, widget_id):
        self.output_text("[INFO]: Running app: " +
                         self.configuration.conf[widget_id]["name"] + ".")
        self.robot.start_behavior(
            self.configuration.conf[widget_id]["package"])

    def on_gesture_clicked(self, widget_id):
        self.output_text("[INFO]: Doing gesture: " +
                         self.configuration.conf[widget_id]["name"] + ".")
        path = np.random.choice(
            self.configuration.conf[widget_id]["path_list"])
        self.animation_from_path(path)

    def on_learn_face_clicked(self):
        self.output_text("[INFO]: Learning face.")
        learn_person(self.robot, self.language)

    def on_recognize_clicked(self):
        self.output_text("[INFO]: Recognizing human.")
        recognize_person(self.robot, self.language)

    def on_take_picture_clicked(self):
        self.output_text("[INFO]: Taking picture.")
        take_picture_show(self.robot)

    def on_basic_demo_clicked(self):
        self.output_text("[INFO]: Running basic demo.")
        basic_demo(self.robot)

    def on_update_sound_clicked(self):
        self.output_text("[INFO]: Updating sound settings.")
        volume = self.builder.tkvariables['volume'].get()
        voice_pitch = self.builder.tkvariables['voice_pitch'].get()
        voice_speed = self.builder.tkvariables['voice_speed'].get()
        self.robot.changeVoice(volume, voice_speed, voice_pitch)

    def set_scales(self):
        self.builder.tkvariables['voice_speed'].set(self.robot.getVoiceSpeed())
        self.builder.tkvariables['voice_pitch'].set(self.robot.getVoiceShape())
        self.builder.tkvariables['volume'].set(self.robot.getVoiceVolume())

    def animation_from_path(self, path):
        try:
            if self.robot.eye_blinking_enabled:
                self.robot.speech_service.setAudioExpression(True)
                self.robot.speech_service.setVisualExpression(True)
            else:
                self.robot.speech_service.setAudioExpression(False)
                self.robot.speech_service.setVisualExpression(False)

            animation_finished = self.robot.animation_service.run(
                "animations/[posture]/" + path, _async=True)
            animation_finished.value()

            return True
        except Exception as error:
            print(error)
            return False

    def on_pick_camera_clicked(self, a, b):
        camera_id = self.builder.get_object('pick_camera').current()
        if camera_id == 2:
            camera = "camera_depth"
        elif camera_id == 1:
            camera = "camera_bottom"
        else:
            camera = "camera_top"
        self.robot.subscribe_camera(camera, 1, 30)

    def get_picked_camera(self):
        """ Get picked camera from combobox. """
        camera_id = self.builder.get_object('pick_camera').current()
        if camera_id == 2:
            camera = "camera_depth"
        elif camera_id == 1:
            camera = "camera_bottom"
        else:
            camera = "camera_top"
        return camera

    def on_picked_camera(self, event):
        """ Combobox event. """
        camera_name = event.widget.get()
        if camera_name == "Camera Depth":
            camera = "camera_depth"
        elif camera_name == "Camera Bottom":
            camera = "camera_bottom"
        else:
            camera = "camera_top"
        self.robot.subscribe_camera(camera, 1, 30)

    def on_handshake_clicked(self):
        self.robot.do_hand_shake()

    def on_do_move_clicked(self):
        arms = self.builder.get_object('arms_submove').get()
        torso = self.builder.get_object('torso_submove').get()
        head = self.builder.get_object('head_submove').get()
        self.mp.go_to_position(head, torso, arms, 0.2)

    def on_random_work_clicked(self, group):
        #work = self.work_list[widget_id]
        reps = self.builder.get_object('reps').get()
        reps = int(float(reps))
        # order = {0: "short_neck",
        #          1: "short_torso",
        #          2: "short_arms",
        #          3: "short_shoulders"}
        #group = order[widget_id]
        #print(self.work_dict[group])
        index = self.work_dict[group].pop(0)
        self.work_dict[group].append(index)
        #print(self.work_dict[group])
        self.mp.do_workout(group, index, reps)
        # for i in range(len(work)):
        #    head = work[0][i][0]
        #    torso = work[0][i][1]
        #    arms = work[0][i][2]
        #    workout.go_to_position(head, torso, arms, 0.2)
        # work = work[1:]+[work[0]]
        # print(work)
        # print(self.work_list[widget_id])

    def on_reps_changed(self, scale_value):
        label = self.builder.get_object('reps_label')
        label.config(text="Reps: " + str(int(float(scale_value))))

    def on_chatbot_clicked(self):
        print("running chatbot")
        path = self.builder.get_object('path_to_chatbot').cget("path")
        src_path = os.path.join(path, "src")
        main_path = os.path.join(src_path, "main.py")
        data_path = os.path.join(path, "data")
        logs_path = os.path.join(path, "logs")
        #subprocess.call('gnome-terminal -- {} --mode robot_remote --data-dir {} --logs-dir {} --loglevel-file trace --loglevel-console info'.format(main_path, data_path, logs_path), shell=True, cwd=src_path)
        #print('gnome-terminal -- {} --mode robot_remote --data-dir {} --logs-dir {} --loglevel-file trace --loglevel-console info'.format(main_path, data_path, logs_path))
        
        #command = "python " + main_path + " -m robot_remote -l " + logs_path +" -d " + data_path
        command = "python " + main_path + " --robot-credentials " + self.ip_address + " --mode robot_remote --data-dir " + data_path + " --logs-dir " + logs_path +" --loglevel-file trace --loglevel-console info"
        subprocess.call("gnome-terminal -- " + command, shell=True)

        #subprocess.call("gnome-terminal -- ./run_chatbot.sh " + main_path + " " + data_path + " " + logs_path, shell=True)

    def on_default_path_clicked(self):
        conf = self.configuration.conf
        path = conf["default_chatbot_path"]
        self.builder.get_object('path_to_chatbot')["path"] = conf["default_chatbot_path"]

if __name__ == '__main__':
    app = PepperControllerApp()
    app.run()
