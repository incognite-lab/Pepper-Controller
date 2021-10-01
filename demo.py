# - *- coding: utf- 8 - *-
import time

from pepper.robot import Pepper
try:
    import urllib
except:
    import urllib.request as urllib
import base64
import json
from PIL import Image
import random


def uploadPhotoToWeb(photo):
    """we need to upload photo to web as we (me) are not able to open it from local folder"""
    f = open(photo, "rb")  # open our image file as read only in binary mode
    image_data = f.read()  # read in our image file
    b64_image = base64.standard_b64encode(image_data)
    client_id = "af482612ae6d1c1"  # this the id which we've got after registrating the app on imgur
    headers = {'Authorization': 'Client-ID ' + client_id}
    data = {'image': b64_image, 'title': 'test'}
    request = urllib.Request(url="https://api.imgur.com/3/upload.json", data=urllib.urlencode(data),
                              headers=headers)
    response = urllib.urlopen(request).read()
    parse = json.loads(response)
    return parse['data']['link'] #returns a url of the photo


def getRandName():
    """returns a random name for the picture in order not to replace the old photo"""
    randNum = random.randint(0, 1000)
    return "demoPictures/photo" + str(randNum) + ".png"


class PepperDemo:
    def __init__(self, ip_address, port=9559):
        self.robot = None
        self.robot = Pepper(ip_address, port)
        self.robot.set_czech_language()
        self.photoName = None
        self.greetings = ["Good afternoon", "Hello", "Hi", "Hello everobody", "Welcome"]
        self.asks = ["May I photograph you?","May I take your picture?", "Do you want to make your picture?"]


    def wantToTakePic(self):
        """recognise answer with google speech reco"""
        answers = {"no": ["no", "no way", "not", "no no", " i don't", "i dont know", "not today", "later", "tommorow"],
                   "yes": ["yes", "definitely", "yep", "ok", "okey dokey", "sure", "all yes", "you must",
                          "absolutely", "i want", "i think so", "i agree", "if you want", "if you insist", "probably", "maybe",
                          "yes sir"]}
        recorded = self.robot.recognize_google(lang="en-US")
        answer = self.getAnswer(answers, recorded)
        if answer == "no":
            return False
        elif answer == "yes":
            return True
        else:
            return None


    def getAnswer(self, dic, recorded):
        """looks for a recorded answer in a dictionar"""
        for x in dic.keys():
            if dic[x] in recorded.lower():
                return x
        return None

    def welcomeAndAsk(self):
        self.robot.say(random.choice(self.greetings))
        self.robot.greet()
        self.robot.say(random.choice(self.asks))

    def takePicture(self):
        self.robot.subscribe_camera("camera_top", 2, 30)
        img = self.robot.get_camera_frame(show=False)
        self.robot.unsubscribe_camera()
        self.robot.play_sound("/home/nao/camera1.ogg")
        im = Image.fromarray(img)
        self.photoName = getRandName()
        im.save(self.photoName)

    def showPicture(self):
        link = uploadPhotoToWeb(self.photoName)
        self.robot.show_image(link)
        time.sleep(5)
        self.robot.reset_tablet()

    def recogniseAnswerAndDecide(self):
        isTakePic = self.wantToTakePic()
        if isTakePic:
            self.robot.say("Perfect. On your marks. 3, 2, 1 .")
            self.takePicture()
            self.showPicture()
        elif isTakePic is None:
            self.robot.say("Sorry, I did not understand you. Please repeat.")
            self.recogniseAnswerAndDecide()
        else:
            self.robot.say("Maybe next time")

    def dealWithRecoErrors(self):
        """there is a modifiable grammar error sometimes occurred.
        In order to deal with it you should change language to english and back"""
        self.robot.set_english_language()
        self.robot.set_czech_language()

    def run(self):
        self.dealWithRecoErrors()
        self.welcomeAndAsk()
        self.recogniseAnswerAndDecide()

if __name__ == "__main__":
    pepperDemo = PepperDemo("10.37.1.232")
    pepperDemo.run()

