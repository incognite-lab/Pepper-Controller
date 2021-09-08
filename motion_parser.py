#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pepper.robot import Pepper
import json
import time
import numpy as np
import yaml
import sys
import qi

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../Pepper-Controller')


class MotionParser:
    def __init__(self, conf_path, robot):
        self.robot = robot
        #self.conf = yaml.safe_load(open(conf_path))
        self.conf = json.load(open(conf_path))
        #print(self.conf)

    def get_conf(self):
        return self.conf

    def __get_position(self, body_part, position):
        """ Returns tulpe (joints, positions) based on given body part and its position"""
        joints = self.conf["positions"][body_part]["joint_list"]
        data_dict = self.conf["positions"][body_part]["data_list"]
        try:
            numbers = data_dict[position]
        except KeyError:
            print("Position: " + position + " not found")
            numbers = [0]*len(joints)
        return joints, numbers

    def go_to_position(self, head, torso, arms, speed=0.2):
        body_parts = ["head", "torso", "arms"]
        positions = [head, torso, arms]
        joints = []
        angles = []
        for i in range(len(body_parts)):
            j, a = self.__get_position(body_parts[i], positions[i])
            joints.extend(j)
            angles.extend(a)
        self.robot.move_joint_by_angle(
            joints, angles, blocking=True, fractionMaxSpeed=speed)

    def do_exercise(self, group, i, reps):
        """ Robot does specified move for several reps
            group - dict key, i - index of move, reps - number of repetitions. """
        for j in range(reps):
            for pos in self.conf["exercises"][group][i]:
                args = (pos["head"], pos["torso"], pos["arms"], pos["speed"])
                self.go_to_position(*args)

    def do_workout(self, group, i, reps=-1):
        """ Does workout based on 'i' in list of workouts. You can change number of reps written in config file by specifing. """
        objects = {"self": self, "robot": self.robot}
        workout = self.conf["workouts"][group][i]
        for instr in workout:
            args = []
            for arg in instr[2]:
                if type(arg) == unicode:
                    args.append(arg.encode("utf8"))
                else:
                    args.append(arg)
            func = getattr(objects[instr[0]], instr[1])  # (*args)
            if func == self.do_exercise and reps != -1:
                args[-1] = reps
            func(*args)
            
    def play_music(self, song):
        qi.async(lambda: mp.robot.play_sound(song))

    def stop_music(self):
        mp.robot.stop_sound()

if __name__ == "__main__":
    robot = Pepper("10.37.1.206", 9559)
    mp = MotionParser("workout_conf.json", robot)
    mp.stop_music()
    mp.do_workout("15_minutes", 0)
    