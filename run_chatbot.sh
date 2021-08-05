#!/bin/bash

echo "-------------Chatbot started------------"
#python chatbot.py
main_path=$1
data_path=$2
logs_path=$3
#./src/main.py -m robot_remote -l ./logs/ -d ./data/
command_="python $main_path -m robot_remote -l $logs_path -d $data_path"
eval $command_

echo "-------------Chatbot over---------------"