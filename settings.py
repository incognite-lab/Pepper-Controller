# -*- coding: utf-8 -*-
from pepper.robot import Pepper
from demo import uploadPhotoToWeb
import random, os, time
import qi




if __name__ == "__main__":
    # Press Pepper's chest button once and he will tell you his IP address
    ip_address = "192.168.0.200"
    port = 9559
    robot = Pepper(ip_address, port)
    robot.tablet_show_settings()
    sleep(5000)





