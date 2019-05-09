from Tkinter import *

wn = Tk()
wn.title('KeyDetect')


def down(event):
    print("down")


def up(event):
    print("up")


def left(event):
    print("left")


def right(event):
    print("right")


wn.bind('<KeyPress-Up>', up)
wn.bind('<KeyPress-Down>', down)
wn.bind('<KeyPress-Left>', left)
wn.bind('<KeyPress-Right>', right)

wn.mainloop()
