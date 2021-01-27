# Pepper Controller

This is a software to control Pepper humanoid robot from Python. You can easily connect to the robot and control it from the command line or GUI interface. This software serves as a replacement for the Choregraphe tool, which offers only graphical programming instead of full Python support. You can also control the robot, launch apps installed on the robot or teleoperate the robot from the GUI interface. The example scripts will help you to learn how to write your own Pepper app in a few lines of Python code, without the necessity to use Softbank software.   

## System requirements

Ubuntu up to 20.04 

Python 2.7

Pepper humanoid robot


## Installation

Install dependencies:


`sudo apt install python-tk opencv-python`


Install Pepper SDK 2.5.10 library for Python 2.7 from: https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares


Add path to your .bashrc: 


`export PYTHONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages` 


Test the library:


`python2`


`import naoqi`


Clone this repository to your computer:

`git clone https://github.com/incognite-lab/Pepper-Controller.git`


`cd Pepper-Controller`

Install dependencies

`pip2 install -r ./requirements.txt` 

## GUI Interface

The easist way to control Pepper robot is via the GUI interface:


`python2 peppergui.py`


The window will appear:


![Image](gui.png)


Firstly, you need to enter the correct IP address (press the robot's chest button to obtain it) to the upper left box and press "Connect"


After a successful connection, you can control the robot by pressing the buttons.

If you want Pepper to say any phrase, enter it in the text edit field and then press the "Say text" button.


The GUI provides support for running Choregraphe projects that are already installed on the robot. We currently do not provide any installable Choregraphe projects, but you can configure the GUI buttons for your own applications. To do that, please edit [conf.yaml](conf.yaml). For each application, you need to provide a name for the button and a path to your Choregraphe app in the form of <applicationID>/<behaviorName>. If you are not sure how to get these, please refer to [Choregraphe documentation](http://doc.aldebaran.com/2-1/software/choregraphe/panels/robot_applications.html). 


Other properties of the GUI can be edited through the [conf.yaml](conf.yaml) file.


## Command line examples

If you want to control the robot from command line, just run Python 2 and type:

`import naoqi`

`from pepper.robot import Pepper`

`robot = Pepper(PeppperIP,9559)`


Now you can control Pepper from the command line. Pepper can say something:


`robot.say("Hello, I am Pepper robot.")`


If you want Pepper to show a website on tablet, type:


`robot.show_web("https://www.google.com/")`


You can also easily switch Autonomous life on or off:


`robot.autonomous_life_off()`

`robot.autonomous_life_on()`


## Example of Pepper semantic segmentation based on Yolact under Python 3


Under onstruction


## Writing custom application

As you can see from previous examples, it is pretty straigforward to write an application in Python without Choregraphe.

We prepared two examples that you can use as templates for the developmnent of your own application. 

First one presents basic robot capabilities:


`python hellopepper.py`


Feel free to edit the script [file](hellopepper.py) according to your needs.


The second example shows a more complex application:


`python demo.py`


You can also use this [script](demo.py) as a starting point to write your application.


## List of methods


The core of our software is Pepper class, a wrapper around naoqi. It will help you to write Python applications. Here is a list all methods in Pepper class.

| Language | Vision | Motorics | System |
| - | - | - | - |
| getVoiceShape | streamCamera | stand | show_image | 
| getVoiceVolume | get_face_properties | rest | autonomous_life |
|  set_volume | turn_off_leds  | turn_around | autonomous_blinking |
| getVoiceSpeed | blink_eyes | detect_touch | show_web |
| greet | take_picture | dance | point_at | reset_tablet |
| test_say  | show_map | stop_behaviour | tablet_show_settings | 
| play_sound | load_map | start_animation | restart_robot | 
| stop_sound | subscribe_camera | start_behavior | shutdown_robot |
| listen_to | unsubscribe_camera | hand | autonomous_life_off |
| listen | get_camera_frame | track_object | autonomous_life_on|
| ask_wikipedia | get_depth_frame | exploration_mode | battery_status |
| speech_to_text |  show_tablet_camera | robot_localization | list_behavior |
| chatbot | | stop_localization | get_robot_name | 
| pick_a_volunteer | | navigate_to | unsubscribe_effector |
| recordSound | | move_forward | share_localhost |
| changeVoice | | move_to_circle| rename_robot |
| | | set_security_distance | upload_file |
| | | move_head_down | download_file |
| | | move_head_up | set_awareness |
| | | move_head_default | |
| | | move_joint_by_angle | |


## Authors


![alt text](incognitelogo.png "test_work")


[Incognite lab - CIIRC CTU](https://incognite.ciirc.cvut.cz) 


[Michal Vavrecka](https://kognice.wixsite.com/vavrecka)

[Gabriela Sejnova](https://kognice.wixsite.com/vavrecka)

[Michael Tesar](https://www.linkedin.com/in/megi-mejdrechova)


[Anastasia Ostapenko](https://www.linkedin.com/in/megi-mejdrechova)
















