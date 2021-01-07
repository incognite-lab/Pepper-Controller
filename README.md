# Pepper Controller

This is a software to control Pepper humanoid robot from Python. You can easily connect to robot and control it from the command line or GUI interface. This software has to be replacement for Choreographe tool, that offer only graphical programming instead of full Python support. You can also control robot, run apps or teleoperate the robot from the GUI interface. The example scripts will help  you to learn how to write Pepper app in few lines Python of code without necessity to use Softbank software.   

## System requirements

Ubuntu up to 20.04 

Python 2.7

Pepper humanoid robot


## Installation

Install Pepper SDK 2.5.10 library for Python 2.7 from: https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares


Add path to your .bashrc: 


`export PYTHONPATH=${PYTHONPATH}:~/pynaoqi/lib/python2.7/site-packages` 


Restart terminal and test the library:


`python2`


`import naoqi`


Clone this repository to your computer:

`git clone https://github.com/incognite-lab/Pepper-Controller.git`

`cd Pepper-Controller`

Install dependencies

`pip2 install -r ./requirements.txt` 

## GUI Interface

The easist way to control Pepper robot is via the GUI interface:


`python2 main.py`


The window will appear:


![Image](gui.png)


Firstly you need to enter corrent IP address (press the robot chest button to obtain it) to the upper left box and press "Connect"


After succesfull connection you can control the robot by pressing the buttons.

If you want to change the behavior of the GUI just edit (conf.yaml[conf.yaml]) file.


## Command line examples

If you want to control robot from command line just run Python and type:





## Usage

Enter Pepper's IP address and press "Připojit". You will be connected to your local robot. \

Then you can start the application by clicking the button with it's name in the section "Aplikace". Most of them are in choreogrpahe and in 90% of the time it is not possible to launch them. 

In order to choose the language in which Pepper speaks (Czech or English) you should press "Nastav češtinu/angličtinu" \

If you want Pepper to say the phrase chosen by you enter it in the field above "řict text" button and then press it.

As you can see, everything is pretty intuitive (if you know the Czech language).
