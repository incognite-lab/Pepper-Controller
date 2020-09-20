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
import numpy
import cv2


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

        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service = self.session.service("ALMotion")
        self.tts_service = self.session.service("ALAnimatedSpeech")
        self.autonomous_life_service = self.session.service("ALAutonomousLife")
        self.battery_service = self.session.service("ALBattery")
        self.awareness_service = self.session.service("ALBasicAwareness")
        self.led_service = self.session.service("ALLeds")
        self.tablet_service = self.session.service("ALTabletService")
        self.animation_service = self.session.service("ALAnimationPlayer")
        self.behavior_service = self.session.service("ALBehaviorManager")
        self.autonomous_blinking_service = self.session.service("ALAutonomousBlinking")
        self.speech_service = self.session.service("ALSpeechRecognition")
        self.dialog_service = self.session.service("ALDialog")
        self.camera_device = self.session.service("ALVideoDevice")
        self.eye_blinking_enabled = True


        print("[INFO]: Robot is initialized at " + ip_address + ":" + str(port))
        
        
    def show_image(self, image):
        self.tablet_service.showImage(image)
        
    def set_czech_language(self):
        self.dialog_service.setLanguage("Czech")
        print("Czech language was set up")

    def set_english_language(self):
	    self.dialog_service.setLanguage("English")
	    print("English language was set up")

    def say(self, text):
        """Animated say text"""
        speed = 100
        shape = 100
        self.tts_service.say(
            "\\RSPD={0}\\ \\VCT={1} \\{2}".format(speed, shape, text)
        )
        
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
        self.posture_service.goToPostures("Crouch", 1.0)
        print("[INFO]: Robot is in resting position")
        
    def turn_around(self, speed):
        """
        Turn around its axis
        :param speed: Positive values to right, negative to left
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
        self.say("Volume is set to " + str(volume) + " percent")

    def battery_status(self):
        """Say a battery status"""
        battery = self.battery_service.getBatteryCharge()
        self.say("Mám nabitých " + str(battery) + " procent baterie")

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
            
    def move_forward(self, speed):
        """
        Move forward with certain speed
        :param speed: Positive values forward, negative backwards
        :type speed: float
        """
        self.motion_service.move(speed, 0, 0)

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

    def subscribe_camera(self, camera, resolution, fps):
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
        self.camera_device.unsubscribe(self.camera_link)
        print("[INFO]: Camera was unsubscribed")

    def get_camera_frame(self, show):
        image_raw = self.camera_device.getImageRemote(self.camera_link)
        image = numpy.frombuffer(image_raw[6], numpy.uint8).reshape(image_raw[1], image_raw[0], 3)

        if show:
            cv2.imshow("Pepper Camera", image)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()

        return image

    def streamCamera(self):
        self.subscribe_camera("camera_top", 2, 30)
        while True:
            image = self.get_camera_frame(show=False)
            cv2.imshow("frame", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.unsubscribe_camera()
        cv2.destroyAllWindows()

