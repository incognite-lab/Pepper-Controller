#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a wrapper around `qi` framework by Aldebaran
to control Pepper the humanoid robot with Python 2.7.

Package uses high-level commands to move robot, take
camera input or run Google Recognition API to get speech
recognition.

It also includes a virtual robot for testing purposes.
"""
import qi
import time
import random
import numpy
import paramiko
import speech_recognition
from nose import tools
from scp import SCPClient
import cv2
import playsound
import subprocess
import socket
from PIL import Image
from pepper.callbacks import HumanGreeter, ReactToTouch
import os

tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_files")
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)
    print("Created temporary folder Pepper_Controller/pepper/tmp_files/ for retrieved data")

class Pepper:
    """
    **Real robot controller**

    Create an instance of real robot controller by specifying
    a robot's IP address and port. IP address can be:

    - hostname (hostname like `pepper.local`)
    - IP address (can be obtained by pressing robot's *chest button*)

    Default port is usually used, e.g. `9559`.

    :Example:

    >>> pepper = Pepper("pepper.local")
    >>> pepper = Pepper("192.169.0.1", 1234)

    """

    def __init__(self, ip_address, port=9559):
        self.session = qi.Session()

        self.session.connect("tcp://{0}:{1}".format(ip_address, port))

        self.ip_address = ip_address
        self.port = port
        connection_url = "tcp://" + ip_address + ":" + str(port)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=self.ip_address, username="nao", password="nao")
        self.scp = SCPClient(ssh.get_transport())
        self.app = qi.Application(["ReactToTouch","HumanGreeter", "--qi-url=" + connection_url])
        self.human_reco = HumanGreeter(self.app)
        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service = self.session.service("ALMotion")
        self.tracker_service = self.session.service("ALTracker")
        self.tts_service = self.session.service("ALAnimatedSpeech")
        self.tablet_service = self.session.service("ALTabletService")
        self.autonomous_life_service = self.session.service("ALAutonomousLife")
        self.system_service = self.session.service("ALSystem")
        self.navigation_service = self.session.service("ALNavigation")
        self.battery_service = self.session.service("ALBattery")
        self.awareness_service = self.session.service("ALBasicAwareness")
        self.led_service = self.session.service("ALLeds")
        self.audio_device = self.session.service("ALAudioDevice")
        self.camera_device = self.session.service("ALVideoDevice")
        self.face_detection_service = self.session.service("ALFaceDetection")
        self.memory_service = self.session.service("ALMemory")
        self.audio_service = self.session.service("ALAudioPlayer")
        self.animation_service = self.session.service("ALAnimationPlayer")
        self.behavior_service = self.session.service("ALBehaviorManager")
        self.face_characteristic = self.session.service("ALFaceCharacteristics")
        self.people_perception = self.session.service("ALPeoplePerception")
        self.speech_service = self.session.service("ALSpeechRecognition")
        self.dialog_service = self.session.service("ALDialog")
        self.audio_recorder = self.session.service("ALAudioRecorder")


        self.slam_map = None
        self.localization = None
        self.camera_link = None

        self.recognizer = speech_recognition.Recognizer()
        self.autonomous_blinking_service = self.session.service("ALAutonomousBlinking")
        self.eye_blinking_enabled = True

        self.voice_speed = 100
        self.voice_shape = 100

        print("[INFO]: Robot is initialized at " + ip_address + ":" + str(port))

    def show_image(self, image):
        self.tablet_service.showImage(image)

    def play_video(self, url):
        self.tablet_service.playVideo(url)

    def stop_video(self):
        self.tablet_service.stopVideo()

    def set_czech_language(self):
        self.dialog_service.setLanguage("Czech")
        print("Czech language was set up")

    def set_english_language(self):
        self.dialog_service.setLanguage("English")
        print("English language was set up")

    def say(self, text, bodylanguage="contextual"):
        """Animated say text"""
        configuration = {"bodyLanguageMode":bodylanguage}
        self.tts_service.say(
            "\\RSPD={0}\\ \\VCT={1} \\{2}".format(self.voice_speed, self.voice_shape, text), configuration
        )

    def getVoiceSpeed(self):
        return self.voice_speed

    def getVoiceShape(self):
        return self.voice_shape

    def getVoiceVolume(self):
        return self.audio_device.getOutputVolume()

    def test_say(self, sentence, speed=100, shape=100):
        self.tts_service.say(
            ("\\RSPD={0}\\ \\VCT={1} \\" + sentence).format(speed, shape)
        )

    def stand(self):
        """Get robot into default standing position known as `StandInit` or `Stand`"""
        self.posture_service.goToPosture("Stand", 1.0)
        print("[INFO]: Robot is in default position")

    def rest(self):
        """Get robot into default resting position know as `Crouch`"""
        self.posture_service.goToPosture("Crouch", 1.0)
        print("[INFO]: Robot is in resting position")

    def point_at(self, x, y, z, effector_name, frame):
        """
        Point end-effector in cartesian space
        :Example:
        >>> pepper.point_at(1.0, 1.0, 0.0, "RArm", 0)
        """
        speed = 0.5  # 50 % of speed
        self.tracker_service.pointAt(effector_name, [x, y, z], frame, speed)

    def turn_around(self, speed):
        """
        Turn around its axis
        :param speed: Positive values to right, negative to left # other way
        :type speed: float
        """
        self.motion_service.move(0, 0, speed)

    def autonomous_blinking(self):
        self.eye_blinking_enabled = not self.eye_blinking_enabled
        if self.speech_service.getAudioExpression():
            print("Disable eye blinking and beeping when listening...")
            self.speech_service.setAudioExpression(False)
            self.speech_service.setVisualExpression(False)
        else:
            print("Enable eye blinking and beeping when listening...")
            self.speech_service.setAudioExpression(True)
            self.speech_service.setVisualExpression(True)

    def greet(self):
        """
        Robot will randomly pick and greet user
        :return: True or False if action was successful
        """
        print("Robot is into greet")
        animation = numpy.random.choice(["Hey_1", "Hey_3", "Hey_4", "Hey_6"])
        try:
            animation_finished = self.animation_service.run("animations/[posture]/Gestures/" + animation, _async=True)
            animation_finished.value()
            return True
        except Exception as error:
            print(error)
            return False

    def show_web(self, website):
        print("Showing a website on the tablet")
        self.tablet_service.showWebview(website)

    def detect_touch(self):
        react_to_touch = ReactToTouch(self.app)
        print("Waiting for touch...")
        while not react_to_touch.activated_sensor:
            if react_to_touch.touch != None:
                pass
            else:
                print("Touch callback does not yet work with Python3, please run the code with Python2.7")
                return None
        return react_to_touch.activated_sensor

    def tablet_show_settings(self):
        """Show robot settings on the tablet"""
        self.tablet_service.showWebview("http://198.18.0.1/")

    def reset_tablet(self):
        print("Resetting a tablet view")
        self.tablet_service.hideWebview()
        self.tablet_service.hideImage()

    def stop_behaviour(self):
        """Stop all behaviours currently running"""
        print("Stopping all behaviors")
        self.behavior_service.stopAllBehaviors()

    def dance(self):
        """Start dancing with robot"""
        print("Robot is about to dance a little")
        self.behavior_service.startBehavior("date_dance-896e88/.")
    
    def mood_happy(self):
        """ is happy """
        print("Robot is in happy mood")
        animation_finished = self.animation_service.run("animations/Stand/Emotions/Positive/Happy_4", _async=True)
        animation_finished.value()
        
    
    def autonomous_life(self):
        """
        Switch autonomous life on/off
        """
        state = self.autonomous_life_service.getState()
        if state == "disabled":
            print("Enabling the autonomous life")
            self.autonomous_life_service.setState("interactive")
        else:
            print("Disabling the autonomous life")
            self.autonomous_life_service.setState("disabled")
            self.stand()

    def restart_robot(self):
        """Restart robot (it takes several minutes)"""
        print("[WARN]: Restarting the robot")
        self.system_service.reboot()

    def shutdown_robot(self):
        """Turn off the robot completely"""
        print("[WARN]: Turning off the robot")
        self.system_service.shutdown()

    def autonomous_life_off(self):
        """
        Switch autonomous life off

        .. note:: After switching off, robot stays in resting posture. After \
        turning autonomous life default posture is invoked
        """
        self.autonomous_life_service.setState("disabled")
        self.stand()
        print("[INFO]: Autonomous life is off")

    def autonomous_life_on(self):
        """Switch autonomous life on"""
        self.autonomous_life_service.setState("interactive")
        print("[INFO]: Autonomous life is on")

    def set_volume(self, volume):
        """
        Set robot volume in percentage

        :param volume: From 0 to 100 %
        :type volume: integer
        """
        self.audio_device.setOutputVolume(volume)
        #self.say("Volume is set to " + str(volume) + " percent")
        #self.say("Volume is set to " + str(volume) + " percent")

    def battery_status(self):
        """Say a battery status"""
        battery = self.battery_service.getBatteryCharge()
        language = self.dialog_service.getLanguage()
        if language == "Czech":
            self.say("Mám nabitých " + str(battery) + " procent baterie")
        elif language == "English":
            self.say("My battery level is " + str(battery) + " %")
        
    def blink_eyes(self, rgb):
        """
        Blink eyes with defined color

        :param rgb: Color in RGB space
        :type rgb: integer

        :Example:

        >>> pepper.blink_eyes([255, 0, 0])

        """
        self.led_service.fadeRGB('AllLeds', rgb[0], rgb[1], rgb[2], 1.0)

    def turn_off_leds(self):
        """Turn off the LEDs in robot's eyes"""
        self.blink_eyes([0, 0, 0])
    
    
    
    def start_animation(self, animation):
        """
        Starts a animation which is stored on robot

        .. seealso:: Take a look a the animation names in the robot \
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer.html#alanimationplayer

        :param animation: Animation name
        :type animation: string
        :return: True when animation has finished
        :rtype: bool
        """
        try:

            if self.eye_blinking_enabled:
                self.speech_service.setAudioExpression(True)
                self.speech_service.setVisualExpression(True)
            else:
                self.speech_service.setAudioExpression(False)
                self.speech_service.setVisualExpression(False)

            animation_finished = self.animation_service.run("animations/[posture]/Gestures/" + animation, _async=True)
            animation_finished.value()

            return True
        except Exception as error:
            print(error)
            return False
    
    def start_behavior(self, behavior):
        """
        Starts a behavior stored on robot

        :param behavior: Behavior name (id/behavior_1 (first part in Choregraphe)
        :type behavior: string
        """
        self.behavior_service.startBehavior(behavior)

    def list_behavior(self):
        """Prints all installed behaviors on the robot"""
        print(self.behavior_service.getBehaviorNames())

    def get_robot_name(self):
        """
        Gets a current name of the robot

        :return: Name of the robot
        :rtype: string
        """
        name = self.system_service.robotName()
        if name:
            self.say("My name is " + name)
        return name

    def hand(self, hand, close):
        """
        Close or open hand

        :param hand: Which hand
            - left
            - right
        :type hand: string
        :param close: True if close, false if open
        :type close: boolean
        """
        hand_id = None
        if hand == "left":
            hand_id = "LHand"
        elif hand == "right":
            hand_id = "RHand"

        if hand_id:
            if close:
                self.motion_service.setAngles(hand_id, 0.0, 0.2)
                print("[INFO]: Hand " + hand + "is closed")
            else:
                self.motion_service.setAngles(hand_id, 1.0, 0.2)
                print("[INFO]: Hand " + hand + "is opened")
        else:
            print("[INFO]: Cannot move a hand")

    def track_object(self, object_name, effector_name, diameter=0.05):
        """
        Track a object with a given object type and diameter. If `Face` is
        chosen it has a default parameters to 15 cm diameter per face. After
        staring tracking in will wait until user press ctrl+c.

        .. seealso:: For more info about tracking modes, object names and other:\
        http://doc.aldebaran.com/2-5/naoqi/trackers/index.html#tracking-modes

        :Example:

        >>> pepper.track_object("Face", "Arms")

        Or

        >>> pepper.track_object("RedBall", "LArm", diameter=0.1)

        :param object_name: `RedBall`, `Face`, `LandMark`, `LandMarks`, `People` or `Sound`
        :param effector_name: `LArm`, `RArm`, `Arms`
        :param diameter: Diameter of the object (default 0.05, for face default 0.15)
        """
        if object == "Face":
            self.tracker_service.registerTarget(object_name, 0.15)
        else:
            self.tracker_service.registerTarget(object_name, diameter)

        self.tracker_service.setMode("Move")
        self.tracker_service.track(object_name)
        self.tracker_service.setEffector(effector_name)

        self.say("Show me a " + object_name)
        print("[INFO]: Use Ctrl+c to stop tracking")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[INFO]: Interrupted by user")
            self.say("Stopping to track a " + object_name)

        self.tracker_service.stopTracker()
        self.unsubscribe_effector()
        self.say("Let's do something else!")

    def take_picture(self):
        self.subscribe_camera("camera_top", 2, 30)
        img = self.get_camera_frame(show=False)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.unsubscribe_camera()
        self.play_sound("/home/nao/camera1.ogg")
        im = Image.fromarray(img)
        photoName = str(random.randint(0, 1000)) + ".png"
        print("Image saved as {}".format(photoName))
        im.save(photoName)
        return photoName

    def exploration_mode(self, radius):
        """
        Start exploration mode when robot it performing a SLAM
        in specified radius. Then it saves a map into robot into
        its default folder.

        .. seealso:: When robot would not move maybe it only needs \
        to set smaller safety margins. Take a look and `set_security_distance()`

        .. note:: Default folder for saving maps on the robot is: \
        `/home/nao/.local/share/Explorer/`

        :param radius: Distance in meters
        :type radius: integer
        :return: image
        :rtype: cv2 image
        """
        self.say("Starting exploration in " + str(radius) + " meters")
        self.navigation_service.explore(radius)
        map_file = self.navigation_service.saveExploration()

        print("[INFO]: Map file stored: " + map_file)

        self.navigation_service.startLocalization()
        self.navigation_service.navigateToInMap([0., 0., 0.])
        self.navigation_service.stopLocalization()

        # Retrieve and display the map built by the robot
        result_map = self.navigation_service.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        self.slam_map = img

    def show_map(self, on_robot=False, remote_ip=None):
        """
        Shows a map from robot based on previously loaded one
        or explicit exploration of the scene. It can be viewed on
        the robot or in the computer by OpenCV.

        :param on_robot: If set shows a map on the robot
        :type on_robot: bool
        :param remote_ip: IP address of remote (default None)
        :type remote_ip: string

        .. warning:: Showing map on the robot is not fully supported at the moment.
        """
        result_map = self.navigation_service.getMetricalMap()
        map_width = result_map[1]
        map_height = result_map[2]
        img = numpy.array(result_map[4]).reshape(map_width, map_height)
        img = (100 - img) * 2.55  # from 0..100 to 255..0
        img = numpy.array(img, numpy.uint8)

        resolution = result_map[0]

        self.robot_localization()

        offset_x = result_map[3][0]
        offset_y = result_map[3][1]
        x = self.localization[0]
        y = self.localization[1]

        goal_x = (x - offset_x) / resolution
        goal_y = -1 * (y - offset_y) / resolution

        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        cv2.circle(img, (int(goal_x), int(goal_y)), 3, (0, 0, 255), -1)

        robot_map = cv2.resize(img, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

        print("[INFO]: Showing the map")

        if on_robot:
            # TODO: It requires a HTTPS server running. This should be somehow automated.
            cv2.imwrite(os.path.join(tmp_path, "map.png"), robot_map)
            self.show_web(remote_ip + ":8000/map.png")
            print("[INFO]: Map is available at: " + str(remote_ip) + ":8000/map.png")
        else:
            cv2.imshow("RobotMap", robot_map)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def robot_localization(self):
        """
        Localize a robot in a map

        .. note:: After loading a map into robot or after new exploration \
        robots always need to run a self localization. Even some movement in \
        cartesian space demands localization.
        """
        # TODO: There should be localizeInMap() with proper coordinates
        try:
            self.navigation_service.startLocalization()
            localization = self.navigation_service.getRobotPositionInMap()
            self.localization = localization[0]
            print("[INFO]: Localization complete")
            self.navigation_service.stopLocalization()
        except Exception as error:
            print(error)
            print("[ERROR]: Localization failed")

    def stop_localization(self):
        """Stop localization of the robot"""
        self.navigation_service.stopLocalization()
        print("[INFO]: Localization stopped")

    def load_map(self, file_name, file_path="/home/nao/.local/share/Explorer/"):
        """
        Load stored map on a robot. It will find a map in default location,
        in other cases alternative path can be specifies by `file_name`.

        .. note:: Default path of stored maps is `/home/nao/.local/share/Explorer/`

        .. warning:: If file path is specified it is needed to have `\` at the end.

        :param file_name: Name of the map
        :type file_name: string
        :param file_path: Path to the map
        :type file_path: string
        """
        self.slam_map = self.navigation_service.loadExploration(file_path + file_name)
        print("[INFO]: Map '" + file_name + "' loaded")

    def subscribe_camera(self, camera, resolution, fps):
        """
        Subscribe to a camera service. You need to subscribe a camera
        before you reach a images from it. If you choose `depth_camera`
        only 320x240 resolution is enabled.

        .. warning:: Each subscription has to have a unique name \
        otherwise it will conflict it and you will not be able to \
        get any images due to return value None from stream.

        :Example:

        >>> pepper.subscribe_camera(0, 1, 15)
        >>> image = pepper.get_camera_frame(False)
        >>> pepper.unsubscribe_camera()

        :param camera: `camera_depth`, `camera_top` or `camera_bottom`
        :type camera: string
        :param resolution:
            0. 160x120
            1. 320x240
            2. 640x480
            3. 1280x960
        :type resolution: integer
        :param fps: Frames per sec (5, 10, 15 or 30)
        :type fps: integer
        """
        color_space = 13

        camera_index = None
        if camera == "camera_top":
            camera_index = 0
        elif camera == "camera_bottom":
            camera_index = 1
        elif camera == "camera_depth":
            camera_index = 2
            resolution = 1
            color_space = 11
        
        self.camera_link = self.camera_device.subscribeCamera("Camera_Stream" + str(numpy.random.random()),
                                                              camera_index, resolution, color_space, fps)
        if self.camera_link:
            print("[INFO]: Camera is initialized")
        else:
            print("[ERROR]: Camera is not initialized properly")

    def unsubscribe_camera(self):
        """Unsubscribe to camera after you don't need it"""
        self.camera_device.unsubscribe(self.camera_link)
        print("[INFO]: Camera was unsubscribed")

    def get_camera_frame(self, show):
        """
        Get camera frame from subscribed camera link.

        .. warning:: Please subscribe to camera before getting a camera frame. After \
        you don't need it unsubscribe it.

        :param show: Show image when recieved and wait for `ESC`
        :type show: bool
        :return: image
        :rtype: cv2 image
        """
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image

    def get_depth_frame(self, show):
        """
        Get depth frame from subscribed camera link.

        .. warning:: Please subscribe to camera before getting a camera frame. After \
        you don't need it unsubscribe it.

        :param show: Show image when recieved and wait for `ESC`
        :type show: bool
        :return: image
        :rtype: cv2 image
        """
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image

    def show_tablet_camera(self, text):
        """
        Show image from camera with SpeechToText annotation on the robot tablet

        .. note:: For showing image on robot you will need to share a location via HTTPS and \
        save the image to ./tmp_pepper.

        .. warning:: It has to be some camera subscribed and ./tmp folder in root directory \
        exists for showing it on the robot.

        :Example:

        >>> pepper = Pepper("10.37.1.227")
        >>> pepper.share_localhost("/Users/michael/Desktop/Pepper/tmp_pepper/")
        >>> pepper.subscribe_camera("camera_top", 2, 30)
        >>> while True:
        >>>     pepper.show_tablet_camera("camera top")
        >>>     pepper.tablet_show_web("http://10.37.2.241:8000/tmp_pepper/camera.png")

        :param text: Question of the visual question answering
        :type text: string
        """
        remote_ip = socket.gethostbyname(socket.gethostname())
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)
        image = cv2.resize(image, (800, 600))
        cv2.putText(image, "Visual question answering", (30, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, "Question: " + text, (30, 550), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(tmp_path, "camera.png"), image)

        self.show_web("http://" + remote_ip + ":8000/%s" % os.path.join(tmp_path, "camera.png"))

    def navigate_to(self, x, y):
        """
        Navigate robot in map based on exploration mode
        or load previously mapped enviroment.

        .. note:: Before navigation you have to run localization of the robot.

        .. warning:: Navigation to 2D point work only up to 3 meters from robot.

        :Example:

        >>> pepper.robot_localization()
        >>> pepper.navigate_to(1.0, 0.3)

        :param x: X axis in meters
        :type x: float
        :param y: Y axis in meters
        :type y: float
        """
        print("[INFO]: Trying to navigate into specified location")
        try:
            self.navigation_service.startLocalization()
            self.navigation_service.navigateToInMap([x, y, 0])
            self.navigation_service.stopLocalization()
            print("[INFO]: Successfully got into location")
            self.say("At your command")
        except Exception as error:
            print(error)
            print("[ERROR]: Failed to got into location")
            self.say("I cannot move in that direction")

    def unsubscribe_effector(self):
        """
        Unsubscribe a end-effector after tracking some object

        .. note:: It has to be done right after each tracking by hands.
        """
        self.tracker_service.unregisterAllTargets()
        self.tracker_service.setEffector("None")
        print("[INFO]: End-effector is unsubscribed")

    def learn_face(self, name):
        """
        Tries to learn the face with the provided name.
        :param name:str, name to learn with face
        :return: str, name of human
        """
        self.set_awareness(True)
        self.human_reco.subscribe_2reco()
        print("Waiting to see a human...")
        success = self.human_reco.learnFace(str(name))
        return success

    def recognize_person(self):
        """
        Tries to recognize the name of the person in front of Pepper
        :return: str, name of human
        """
        self.set_awareness(True)
        self.human_reco.subscribe_2reco()
        print("Waiting to see a human...")
        while not self.human_reco.human_name:
            pass
        name = self.human_reco.human_name if self.human_reco.human_name != "noone" else None
        return name

    def pick_a_volunteer(self):
        """
        Complex movement for choosing a random people.

        If robot does not see any person it will automatically after several
        seconds turning in one direction and looking for a human. When it detects
        a face it will says 'I found a volunteer' and raise a hand toward
        her/him and move forward. Then it get's into a default 'StandInit'
        pose.

        :Example:

        >>> pepper.pick_a_volunteer()

        """
        volunteer_found = False
        self.unsubscribe_effector()
        self.stand()
        self.say("I need a volunteer.")

        proxy_name = "FaceDetection" + str(numpy.random)

        print("[INFO]: Pick a volunteer mode started")

        while not volunteer_found:
            wait = numpy.random.randint(500, 1500) / 1000
            theta = numpy.random.randint(-10, 10)
            self.turn_around(theta)
            time.sleep(wait)
            self.stop_moving()
            self.stand()
            self.face_detection_service.subscribe(proxy_name, 500, 0.0)
            for memory in range(5):
                time.sleep(0.5)
                output = self.memory_service.getData("FaceDetected")
                print("...")
                if output and isinstance(output, list) and len(output) >= 2:
                    print("Face detected")
                    volunteer_found = True

        self.say("I found a volunteer! It is you!")
        self.stand()
        try:
            self.tracker_service.registerTarget("Face", 0.15)
            self.tracker_service.setMode("Move")
            self.tracker_service.track("Face")
            self.tracker_service.setEffector("RArm")
            self.get_face_properties()

        finally:
            time.sleep(2)
            self.unsubscribe_effector()
            self.stand()
            self.face_detection_service.unsubscribe(proxy_name)

    @staticmethod
    def share_localhost(folder):
        """
        Shares a location on localhost via HTTPS to Pepper be
        able to reach it by subscribing to IP address of this
        computer.

        :Example:

        >>> pepper.share_localhost("/Users/pepper/Desktop/web/")

        :param folder: Root folder to share
        :type folder: string
        """
        # TODO: Add some elegant method to kill a port if previously opened
        subprocess.Popen(["cd", folder])
        try:
            subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
        except Exception as error:
            subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
        print("[INFO]: HTTPS server successfully started")

    def play_sound(self, sound):
        """
        Play a `mp3` or `wav` sound stored on Pepper

        .. note:: This is working only for songs stored in robot.

        :param sound: Absolute path to the sound
        :type sound: string
        """
        print("[INFO]: Playing " + sound)
        self.audio_service.playFile(sound)

    def stop_sound(self):
        """Stop sound"""
        print("[INFO]: Stop playing the sound")
        self.audio_service.stopAll()

    def get_face_properties(self):
        """
        Gets all face properties from the tracked face in front of
        the robot.

        It tracks:
        - Emotions (neutral, happy, surprised, angry and sad
        - Age
        - Gender

        .. note:: It also have a feature that it substracts a 5 year if it talks to a female.

        .. note:: If it cannot decide which gender the user is, it just greets her/him as "Hello human being"

        ..warning:: To get this feature working `ALAutonomousLife` process is needed. In this methods it is \
        called by default
        """
        self.autonomous_life_on()
        emotions = ["neutral", "happy", "surprised", "angry", "sad"]
        face_id = self.memory_service.getData("PeoplePerception/PeopleList")
        recognized = None
        try:
            recognized = self.face_characteristic.analyzeFaceCharacteristics(face_id[0])
        except Exception as error:
            print("[ERROR]: Cannot find a face to analyze.")
            self.say("I cannot recognize a face.")

        if recognized:
            properties = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/ExpressionProperties")
            gender = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/GenderProperties")
            age = self.memory_service.getData("PeoplePerception/Person/" + str(face_id[0]) + "/AgeProperties")

            # Gender properties
            if gender[1] > 0.4:
                if gender[0] == 0:
                    self.say("Hello lady!")
                elif gender[0] == 1:
                    self.say("Hello sir!")
            else:
                self.say("Hello human being!")

            # Age properties
            if gender[1] == 1:
                self.say("You are " + str(int(age[0])) + " years old.")
            else:
                self.say("You look like " + str(int(age[0])) + " oops, I mean " + str(int(age[0]-5)))

            # Emotion properties
            emotion_index = (properties.index(max(properties)))

            if emotion_index > 0.5:
                self.say("I am quite sure your mood is " + emotions[emotion_index])
            else:
                self.say("I guess your mood is " + emotions[emotion_index])

    def listen_to(self, vocabulary, language="Cz"):
        """
        Listen and match the vocabulary which is passed as parameter.

        :Example:

        >>> words = pepper.listen_to(["what color is the sky", "yes", "no"]

        :param vocabulary: List of phrases or words to recognize
        :type vocabulary: list
        :return: Recognized phrase or words
        :rtype: string
        """
        self.speech_service.pause(True)
        if language == "En":
            self.speech_service.setLanguage("English")
        self.speech_service.removeAllContext()
        self.speech_service.deleteAllContexts()
        try:
            self.speech_service.setVocabulary(vocabulary,False)
        except:
            try:
                self.speech_service.subscribe("Test_ASR")
                self.speech_service.setVocabulary(vocabulary, False)
            except:
                self.speech_service.unsubscribe("Test_ASR")
                self.speech_service.setVocabulary(vocabulary, False)
        self.speech_service.subscribe("Test_ASR")
        print("[INFO]: Robot is listening to you...")
        self.speech_service.pause(False)
        time.sleep(4)
        words = self.memory_service.getData("WordRecognized")
        print("[INFO]: Robot understood: '" + words[0] + "'")
        self.speech_service.unsubscribe("Test_ASR")
        return words

    def listen(self, lang):
        """
        DOES NOT WORK WITHOUT LICENSE (that is our case :( )
        Wildcard speech recognition via internal Pepper engine

        .. warning:: To get this proper working it is needed to disable or uninstall \
        all application which can modify a vocabulary in a Pepper.

        .. note:: Note this version only rely on time but not its internal speak processing \
        this means that Pepper will 'bip' at the begining and the end of human speak \
        but it is not taken a sound in between the beeps. Search for 'Robot is listening to \
        you ... sentence in log console

        :Example:

        >>> words = pepper.listen()

        :return: Speech to text
        :rtype: string
        """
        self.speech_service.setAudioExpression(False)
        self.speech_service.setVisualExpression(False)
        self.audio_recorder.stopMicrophonesRecording()
        print("[INFO]: Speech recognition is in progress. Say something.")
        while True:
            print(self.memory_service.getData("ALSpeechRecognition/Status"))
            if self.memory_service.getData("ALSpeechRecognition/Status") == "SpeechDetected":
                self.audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))
                print("[INFO]: Robot is listening to you")
                self.blink_eyes([255, 255, 0])
                break

        while True:
            if self.memory_service.getData("ALSpeechRecognition/Status") == "EndOfProcess":
                self.audio_recorder.stopMicrophonesRecording()
                print("[INFO]: Robot is not listening to you")
                self.blink_eyes([0, 0, 0])
                break

        self.download_file("speech.wav")
        self.speech_service.setAudioExpression(True)
        self.speech_service.setVisualExpression(True)

        return self.speech_to_text("speech.wav", lang)

    def ask_wikipedia(self):
        """
        Ask for question and then robot will say first two sentences from Wikipedia

        ..warning:: Autonomous life has to be turned on to process audio
        """
        self.speech_service.setAudioExpression(False)
        self.speech_service.setVisualExpression(False)
        self.set_awareness(False)
        self.say("Give me a question")
        question = self.listen()
        self.say("I will tell you")
        answer = tools.get_knowledge(question)
        self.say(answer)
        self.set_awareness(True)
        self.speech_service.setAudioExpression(True)
        self.speech_service.setVisualExpression(True)

    def rename_robot(self):
        """Change current name of the robot"""
        choice = raw_input("Are you sure you would like to rename a robot? (yes/no)\n")
        if choice == "yes":
            new_name = raw_input("Enter a new name for the robot. Then it will reboot itself.\nName: ")
            self.system_service.setRobotName(new_name)
            self.restart_robot()

    def upload_file(self, file_name):
        """
        Upload file to the home directory of the robot

        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.put(file_name)
        print("[INFO]: File " + file_name + " uploaded")
        self.scp.close()

    def download_file(self, file_name):
        """
        Download a file from robot to ./tmp folder in root.

        ..warning:: Folder ./tmp has to exist!
        :param file_name: File name with extension (or path)
        :type file_name: string
        """
        self.scp.get(file_name, local_path=tmp_path)
        print("[INFO]: File " + file_name + " downloaded")
        self.scp.close()

    def speech_to_text(self, audio_file, lang="en-US"):
        """
        Translate speech to text via Google Speech API

        :param audio_file: Name of the audio (default `speech.wav`)
        :param lang: Code of the language (e.g. "en-US", "cs-CZ")
        :type audio_file: string
        :return: Text of the speech
        :rtype: string
        """
        audio_file = speech_recognition.AudioFile(os.path.join(tmp_path, audio_file))
        with audio_file as source:
            audio = self.recognizer.record(source)
            recognized = self.recognizer.recognize_google(audio, language=lang)
        return recognized

    def chatbot(self):
        """
        Run chatbot with text to speech and speech to text

        ..warning:: This is not currently working
        """
        tools.chatbot_init()
        while True:
            try:
                self.set_awareness(False)
                question = self.listen()
                print("[USER]: " + question)
                answer = tools.chatbot_ask(question)
                print("[ROBOT]: "+ answer)
                self.say(answer)
            except KeyboardInterrupt:
                self.set_awareness(True)

    def streamCamera(self):
        self.subscribe_camera("camera_top", 2, 30)

        while True:
            image = self.get_camera_frame(show=False)
            cv2.imshow("frame", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.unsubscribe_camera()
        cv2.destroyAllWindows()

    def recognize_google(self, lang):
        """
        Uses external SpeechRecognition library to transcribe speech to text. The sound is first recorded into .wav file and then analysed with Google cloud service.
        :param lang: str
        """
        self.recordSound()
        return self.speech_to_text("speech.wav", lang)

    def recordSound(self):
        self.audio_recorder.stopMicrophonesRecording()
        print ("start recording")
        self.audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))
        time.sleep(5)
        self.audio_recorder.stopMicrophonesRecording()
        print ("record over")
        self.download_file("speech.wav")

    def changeVoice(self, volume, speed, shape):
        self.set_volume(volume)
        self.voice_speed = speed
        self.voice_shape = shape
        language = self.dialog_service.getLanguage()
        if language == "Czech":
            self.say("Zkouška hlasu")
        elif language == "English":
            self.say("Sound check")
        

    def set_awareness(self, on=True):
        """
        Turn on or off the basic awareness of the robot,
        e.g. looking for humans, self movements etc.

        :param state: If True set on, if False set off
        :type state: bool
        """
        if on is True:
            self.awareness_service.resumeAwareness()
            print("[INFO]: Awareness is turned on")
        else:
            self.awareness_service.pauseAwareness()
            print("[INFO]: Awareness is paused")

    def move_forward(self, speed):
        """
        Move forward with certain speed
        :param speed: Positive values forward, negative backwards
        :type speed: float
        """
        self.motion_service.move(speed, 0, 0)

    def set_security_distance(self, distance=0.05):
        """
        Set security distance. Lower distance for passing doors etc.

        .. warning:: It is not wise to turn `security distance` off.\
        Robot may fall from stairs or bump into any fragile objects.

        :Example:

        >>> pepper.set_security_distance(0.01)

        :param distance: Distance from the objects in meters
        :type distance: float
        """
        self.motion_service.setOrthogonalSecurityDistance(distance)
        print("[INFO]: Security distance set to " + str(distance) + " m")

    def move_head_down(self):
        """Look down"""
        self.motion_service.setAngles("HeadPitch", 0.46, 0.2)

    def move_head_up(self):
        """Look up"""
        self.motion_service.setAngles("HeadPitch", -0.4, 0.2)

    def move_head_default(self):
        """Put head into default position in 'StandInit' pose"""
        self.motion_service.setAngles("HeadPitch", 0.0, 0.2)

    def move_to_circle(self, clockwise, t=10):
        """
        Move a robot into circle for specified time

        .. note:: This example only count on time not finished circles.

        >>> pepper.move_to_circle(clockwise=True, t=5)

        :param clockwise: Specifies a direction to turn around
        :type clockwise: bool
        :param t: Time in seconds (default 10)
        :type t: float
        """
        if clockwise:
            self.motion_service.moveToward(0.5, 0.0, 0.6)
        else:
            self.motion_service.moveToward(0.5, 0.0, -0.6)
        time.sleep(t)
        self.motion_service.stopMove()

    def move_joint_by_angle(self, joints, angles, fractionMaxSpeed=0.2, blocking=False):
        """
        :param joints: list of joint types to be moved according to http://doc.aldebaran.com/2-0/_images/juliet_joints.png
        :param angles: list of angles for each joint
        :param fractionMaxSpeed: fraction of the maximum speed for joint motion, i.e. an integer (0-1)
        """
        #self.motion_service.setStiffnesses("Head", 1.0)
        # Example showing how to set angles, using a fraction of max speed
        self.motion_service.setAngles(joints, angles, fractionMaxSpeed)
        
        # TODO: zmena dist
        
        if blocking:
            epsilon = 0.12
            last_angles = [-100]*len(joints)
            while True:
                time.sleep(0.1)
                now_angles = self.motion_service.getAngles(joints, True)
                dist = 0
                change = 0
                for i in range(len(joints)):
                    dist += (now_angles[i]-angles[i])**2
                    change += abs(now_angles[i]-last_angles[i])
                last_angles = [angle for angle in now_angles]
                #print("change", change)
                if dist < 0.15 and change < 0.005:
                    #print("konec", dist)
                    break
        
        #    print()
            #self.motion_service.angleInterpolation(joints, angles, len(joints)*[end_time], True);
        #time.sleep(3.0)
        #motion_service.setStiffnesses("Head", 0.0)

    def do_hand_shake(self):
        self.move_joint_by_angle(["RElbowRoll", "RShoulderPitch", "RElbowYaw", "RWristYaw"], [1, 1, 1, 1], 0.4)
        self.hand("right", False)
        time.sleep(3)
        self.hand("right", True)
        self.move_joint_by_angle(["RElbowRoll", "RShoulderPitch", "RElbowYaw", "RWristYaw"], [0, 1.5, 1, 1], 0.4)


    class VirtualPepper:
        """Virtual robot for testing"""

        def __init__(self):
            """Constructor of virtual robot"""
            print("[INFO]: Using virtual robot!")

        @staticmethod
        def say(text):
            """
            Say some text trough text to speech

            :param text: Text to speech
            :type text: string
            """
            import gtts
            tts = gtts.gTTS(text, lang="en")
            tts.save("./tmp_speech.mp3")
            playsound.playsound("./tmp_speech.mp3")

        @staticmethod
        def listen(lang="en-US"):
            """Speech to text by Google Speech Recognition"""
            recognizer = speech_recognition.Recognizer()
            with speech_recognition.Microphone() as source:
                print("[INFO]: Say something...")
                audio = recognizer.listen(source)
                speech = recognizer.recognize_google(audio, language=lang)

                return speech

        @staticmethod
        def stream_camera():
            """Stream web camera of the computer (if any)"""
            print("[INFO]: Press q to quit camera stream")

            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()

        @staticmethod
        def camera_image():
            """Show one frame from web camera (if any)"""
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow("input", img)

                key = cv2.waitKey(10)
                if key == 27:
                    break

            cv2.destroyAllWindows()
            cv2.VideoCapture(0).release()
