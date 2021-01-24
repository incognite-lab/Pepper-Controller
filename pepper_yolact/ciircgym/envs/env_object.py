import os, inspect
import atexit

import xml.etree.ElementTree as ET
from shutil import copyfile
import pybullet
import random
import glob
import numpy as np
import sys, shutil
from datetime import datetime
import pkg_resources
currentdir = pkg_resources.resource_filename("ciircgym", "envs")


class EnvObject:
    """Class for object in PyBullet environment.
    """

    def __init__(self, urdf_path, position=[0, 0, 0],
                 orientation=[0, 0, 0, 0], fixed=False,
                 pybullet_client=None):
        self.p = pybullet_client
        self.urdf_path = urdf_path
        self.init_position = position
        self.init_orientation = orientation
        self.fixed = fixed
        self.uid = self.load()
        self.debug_line_ids = []
        self.bounding_box = self.get_bounding_box()
        self.centroid = self.get_centroid()
        self.cuboid_dimensions = None
        self.name = os.path.splitext(os.path.basename(self.urdf_path))[0]
        #print(self.name)

    def set_color(self, color):
        self.color_rgba =  color
        self.p.changeVisualShape(self.uid, -1, rgbaColor=self.color_rgba)

    def set_random_color(self):
        self.color_rgba =  self.get_random_color()
        self.p.changeVisualShape(self.uid, -1, rgbaColor=self.color_rgba)

    def get_color_rgba(self):
        return self.color_rgba

    def set_random_texture(self, obj_id, patternPath="dtd/images"):
        """
        apply texture to pybullet object
        @param obj_id ID obtained from `p.loadURDF/SDF/..()`
        @param path relative path to *.jpg (recursive) with textures
        """
        pp = os.path.abspath(os.path.join(currentdir, str(patternPath)))
        texture_paths = glob.glob(os.path.join(pp, '**', '*.jpg'), recursive=True)
        texture_paths += glob.glob(os.path.join(pp, '**', '*.png'), recursive=True)
        random_texture_path = random.choice(texture_paths)
        texture_id = self.p.loadTexture(random_texture_path)
        try:
            self.p.changeVisualShape(obj_id, -1, rgbaColor=[1, 1, 1, 1])
            self.p.changeVisualShape(obj_id, -1, textureUniqueId=texture_id)
        except:
            print("Failed to apply texture to obj ID:" + str(obj_id) + " from path=" + str(pp))

    def set_init_position(self, position):
        self.init_position = position

    def set_init_orientation(self, orientation):
        self.init_orientation = orientation

    def get_position(self):
        return self.get_position_and_orientation()[0]

    def get_orientation(self):
        return self.get_position_and_orientation()[1]

    def get_orientation_euler(self):
        return self.p.getEulerFromQuaternion(self.get_position_and_orientation()[1])

    def get_position_and_orientation(self):
        return self.p.getBasePositionAndOrientation(self.uid)

    def set_position(self, position):
        self.p.resetBasePositionAndOrientation(self.uid, position, self.get_orientation())

    def set_orientation(self, orientation):
        self.p.resetBasePositionAndOrientation(self.uid, self.get_position(), orientation)

    def move(self, movement):
        current_position = self.get_position()
        self.set_position(np.add(current_position, movement))

    def rotate_euler(self, rotation):
        current_euler= self.p.getEulerFromQuaternion(self.get_orientation())
        next_euler = np.add(current_euler, rotation)
        self.set_orientation(self.p.getQuaternionFromEuler(next_euler))

    def get_file_path(self):
        return self.file_path

    def set_texture(self, texture):
        pass

    def load(self):
        #print(self.urdf_path)
        self.uid = self.p.loadURDF(self.urdf_path, self.init_position, self.init_orientation, useFixedBase=self.fixed,  flags=self.p.URDF_USE_SELF_COLLISION)
        return self.uid

    def get_bounding_box(self):
        # Returns list of 8 coordinates of bounding box + center of the box
        bounding_box = []
        diag = self.p.getAABB(self.uid)
        bounding_box.append(diag[0])
        bounding_box.append((diag[0][0], diag[1][1], diag[0][2]))
        bounding_box.append((diag[1][0], diag[0][1], diag[0][2]))
        bounding_box.append((diag[1][0], diag[1][1], diag[0][2]))
        bounding_box.append(diag[1])
        bounding_box.append((diag[0][0], diag[0][1], diag[1][2]))
        bounding_box.append((diag[1][0], diag[0][1], diag[1][2]))
        bounding_box.append((diag[0][0], diag[1][1], diag[1][2]))
        bounding_box.append(list(np.divide(np.add(diag[0], diag[1]), 2)))
        return bounding_box

    def get_centroid(self):
        # Returns center of mass
        return self.p.getBasePositionAndOrientation(self.uid)[0]

    def draw_bounding_box(self):
        diagonal_points = self.p.getAABB(self.uid)
        lines = self.get_lines(diagonal_points)
        if self.debug_line_ids:
            for i in range(len(lines)):
                self.p.addUserDebugLine(lines[i][0], lines[i][1], replaceItemUniqueId = self.debug_line_ids[i], lineColorRGB=(0.31, 0.78, 0.47), lineWidth = 2)
        else:
            for i in range(len(lines)):
                self.debug_line_ids.append(self.p.addUserDebugLine(lines[i][0], lines[i][1], lineColorRGB=(0.31, 0.78, 0.47), lineWidth = 2))


    def get_lines(self, diag):
        lines = []

        lines.append((diag[0], (diag[0][0], diag[0][1], diag[1][2])))
        lines.append((diag[0], (diag[0][0], diag[1][1], diag[0][2])))
        lines.append((diag[0], (diag[1][0], diag[0][1], diag[0][2])))
        lines.append((diag[1], (diag[1][0], diag[1][1], diag[0][2])))
        lines.append((diag[1], (diag[1][0], diag[0][1], diag[1][2])))
        lines.append((diag[1], (diag[0][0], diag[1][1], diag[1][2])))

        lines.append(((diag[0][0], diag[0][1], diag[1][2]), (diag[1][0], diag[0][1], diag[1][2])))
        lines.append(((diag[0][0], diag[0][1], diag[1][2]), (diag[0][0], diag[1][1], diag[1][2])))
        lines.append(((diag[1][0], diag[1][1], diag[0][2]), (diag[1][0], diag[0][1], diag[0][2])))
        lines.append(((diag[1][0], diag[1][1], diag[0][2]), (diag[0][0], diag[1][1], diag[0][2])))
        lines.append(((diag[0][0], diag[1][1], diag[1][2]), (diag[0][0], diag[1][1], diag[0][2])))
        lines.append(((diag[1][0], diag[0][1], diag[0][2]), (diag[1][0], diag[0][1], diag[1][2])))

        return lines


    def get_cuboid_dimensions(self):
        if self.cuboid_dimensions is None:
            diag = self.p.getAABB(self.uid)
            self.cuboid_dimensions = np.absolute(np.subtract(diag[0], diag[1])).tolist()
        return self.cuboid_dimensions

    def get_name(self):
        return self.name

    def get_uid(self):
        return self.uid

    @staticmethod
    def get_random_object_position(boarders):
        pos = []
        pos.append(random.uniform(boarders[0], boarders[1])) #x
        pos.append(random.uniform(boarders[2], boarders[3])) #y
        pos.append(random.uniform(boarders[4], boarders[5])) #z
        return pos

    @staticmethod
    def get_random_object_orientation():
        """
        rotate object by (X,Y,Z) axis randomly.
        By default only by "Z" (rotates on horizontal plane, aka. table top)
        """
        angleX = 3.14 * 0.5 + 3.14 * random.random()
        angleY = 3.14 * 0.5 + 3.14 * random.random()
        angleZ = 3.14 * 0.5 + 3.14 * random.random()

        return pybullet.getQuaternionFromEuler([angleX, angleY, angleZ])


    @staticmethod
    def get_random_color():
        color = []
        for i in range(3):
            color.append(random.uniform(0, 1))
        color.append(1)
        return color
