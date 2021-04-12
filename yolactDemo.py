'''Working in python2'''
import argparse

from pepper.robot import Pepper
import time
from PIL import Image
import cv2
import json
import threading
import sys

hasFinished = False


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--speak_constantly', default='False', type=str,
                        help='If true Pepper will say what he sees each 10 seconds')
    args = parser.parse_args(argv)
    return args

def dumpData(data):
    with open('classes.json', 'w') as f:
        try:
            json.dump(data, f)
        except:
            dumpData(data)


def getData():
    with open("classes.json") as f:
        try:
            return json.load(f)
        except:
            return getData()

def analyzeWhere(robot, question):
    data = getData()
    availableClasses = data["class_names_upd"]
    directions = data["directions_upd"]
    classesToName = []
    for w in question:
        if w in availableClasses:
            classesToName.append(w)
        elif w[:-1] in availableClasses:  # case of multiple objects like chairS
            classesToName.append(w[:-1])
    if classesToName == []:
        robot.say("I do not know", bodylanguage='disabled')
    for c_name in classesToName:
        robot.say(c_name + " is on the " + directions[c_name], bodylanguage='disabled')


def answerQuestion(robot, q_code, question):
    data = getData()
    try:
        class_names = data["class_names"]
        directions = data["directions"]
    except:
        return
    if q_code == 0:
        analyzeWhere(robot, question)
    elif q_code == 1 or q_code == 2:
        compareImages(robot, data, isQuesion=True, c_code=q_code)
        updateJson(data["class_names_upd"], data["directions_upd"])
    elif q_code == 3:
        countedObjects = countObjects(class_names)
        robot.say("I see ", bodylanguage='disabled')
        firstNameClasses(robot, countedObjects, directions)
        updateJson(data["class_names_upd"], data["directions_upd"])
    elif q_code == 4:
        compareImages(robot, data, isQuesion=True, c_code=0)
        updateJson(data["class_names_upd"], data["directions_upd"])


def recogniseQuestion(robot):
    questions = {"where": 0, "add": 1, "added": 1, "edit":1, "new":1,
                 "remove": 2, "take": 2, "took": 2, "removed": 2,
                 "taken": 2, "see": 3, "seen" :3, "seem":3,
                 "change": 4, "changed": 4, "changes": 4}
    global hasFinished
    while not hasFinished:
        robot.set_english_language()
        try:
            robot.blink_eyes([255, 255, 0])
            words = robot.recordSound()
            robot.blink_eyes([0, 0, 0])
        except:
            continue
        if words is None:
            #robot.say("I don't understand you, human")
            continue
        print("Pepper has recognised " + words)
        words = words.lower()
        words = words.split(" ")
        for q in questions:
            if q in words:
                answerQuestion(robot, questions[q], words)
                break
        time.sleep(2)

def nameClasses(robot, name, count, direction, dirP):
    robot.say(count, bodylanguage='disabled')
    word = name if count == 1 else name + "s"
    robot.say(word, bodylanguage='disabled')
    robot.say(dirP + direction, bodylanguage='disabled')


def firstNameClasses(robot, countedObjects, directions):
    for name in countedObjects.keys():
        count = countedObjects[name]
        direction = directions[name]
        nameClasses(robot, name, count, direction, "on the ")


def updateJson(class_names, directions):
    newData = getData()
    data = {'init': 'false', 'class_names': class_names, 'directions': directions,
            'class_names_upd': newData["class_names_upd"],
            'directions_upd': newData["directions_upd"]}
    dumpData(data)


def getChanges(oldClasses, newClasses):
    return list(set(newClasses) - set(oldClasses)), \
           list(set(oldClasses) - set(newClasses))


def announce(robot, changedClasses, countFirstStrings,
             countSecondStrings, directions, dirP, phrase):
    phraseFlag = 0
    for c in changedClasses:
        firstPair = countFirstStrings[c]
        flag = 0
        for secondPair in countSecondStrings.values():
            if secondPair[0] == firstPair[0]:
                flag = 1
                count = firstPair[1] - secondPair[1]
                if count > 0:
                    if phraseFlag == 0:
                        phraseFlag = 1
                        robot.say(phrase, bodylanguage='disabled')
                    name = firstPair[0]
                    nameClasses(robot, name, count, directions[name], dirP)
        if flag == 0:
            if phraseFlag == 0:
                phraseFlag = 1
                robot.say(phrase, bodylanguage='disabled')
            name = firstPair[0]
            count = firstPair[1]
            nameClasses(robot, name, count, directions[name], dirP)


def announceChanges(robot, countNewStrings, countOldStrings,
                    addedClasses, deletedClasses, oldDirections, newDirections):
    if not len(addedClasses) == 0:
        announce(robot, addedClasses, countNewStrings, countOldStrings,
                 newDirections, "on the ", "You have added ")

    if not len(deletedClasses) == 0:
        announce(robot, deletedClasses, countOldStrings, countNewStrings,
                 oldDirections, "from the ", "You have removed ")


def compareImages(robot, data, isQuesion, c_code):
    oldClasses = data["class_names"]
    newClasses = data["class_names_upd"]
    countedOld = countObjects(oldClasses)
    countedNew = countObjects(newClasses)
    countOldStrings = {i + str(countedOld[i]): (i, countedOld[i]) for i in countedOld.keys()}
    countNewStrings = {i + str(countedNew[i]): (i, countedNew[i]) for i in countedNew.keys()}
    addedClasses, deletedClasses = getChanges(countOldStrings.keys(), countNewStrings.keys())
    if c_code == 1:
        deletedClasses = []
    elif c_code == 2:
        addedClasses = []
    if isQuesion and (len(addedClasses) == len(deletedClasses) == 0):
        robot.say("I see no changes", bodylanguage='disabled')
        return
    announceChanges(robot, countNewStrings, countOldStrings, addedClasses,
                    deletedClasses, data["directions"], data["directions_upd"])


def countObjects(class_names):
    return {i: class_names.count(i) for i in class_names}


def processClasses(robot):
    data = getData()
    try:
        class_names = data["class_names"]
        directions = data["directions"]
    except:
        return
    countedObjects = countObjects(class_names)
    if data["init"] == "true":
        if len(countedObjects) == 0:
            return
        data["init"] = "false"
        dumpData(data)
        robot.say("Let's start! I see ", bodylanguage='disabled')
        firstNameClasses(robot, countedObjects, directions)
    else:
        compareImages(robot, data, isQuesion=False, c_code=0)
        updateJson(data["class_names_upd"], data["directions_upd"])


def camera_stream(robot):
    robot.subscribe_camera("camera_top", 2, 30)
    while True:
        image = robot.get_camera_frame(show=False)
        cv2.imshow("frame", image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        im = Image.fromarray(image)
        im.save("./camera.jpg")
    robot.unsubscribe_camera()
    cv2.destroyAllWindows()
    global hasFinished
    hasFinished = True


def constantlyCheckObjects(robot):
    global hasFinished
    while not hasFinished:
        processClasses(robot)
        time.sleep(4)


if __name__ == "__main__":
    robot = Pepper("10.37.1.237")
    args = parse_args()
    #robot.autonomous_life_off()
    robot.set_english_language()
    robot.move_head_default()
    if args.speak_constantly == 'False':
        listenThread = threading.Thread(target=recogniseQuestion, args=(robot,))
        listenThread.start()
    else:
        talkingThread = threading.Thread(target=constantlyCheckObjects, args=(robot,))
        talkingThread.start()
    camera_stream(robot)
