#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '..')
import naoqi
from pepper.robot import Pepper
import time
import random
import teleoperation as teleop


language = "cs-CZ"

PeppperIP = "10.37.1.243"
robot = Pepper(PeppperIP,9559)

teleop.teleoperate_robot(robot)

