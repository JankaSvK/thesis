import signal
import threading
import tkinter as tk
import threading, sys, os


import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from queue import Queue
import cv2
from PIL import Image, ImageTk

from Arrow3D import Arrow3D
from Provider import Provider
from QueuesProvider import QueuesProvider


class GUI(object):
    def __init__(self, tracked_points):
        self.tracked_points = tracked_points
        self.stop_event = False

    def do_nothing(self):
        pass

    def draw_cameras(self, cameras):
        for i, cam in enumerate(cameras):
            start, end = cam
            self.subplot.text(*start, i)
            self.subplot.scatter(*start, s=0.5) # Plot is not changing camera view to see arrows, so creating point to include
            a = Arrow3D([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
            self.subplot.add_artist(a)

    def click_callback(self, event, id):
        print ("clicked at", id,'-', event.x, event.y)
        QueuesProvider.add_mouse_click(window_index=id, x=event.x, y=event.y)

    def ask_quit(self):
        self.stop_event = True
        # self.stop_event.set()
        self.exit.set()

       # raise RuntimeError

        #from Main import check_stop
        #check_stop("GUI to vyplo")


    def start(self, image_streams, exiting_program, localization_data = []):
        self.root = tk.Tk()
        self.exit = exiting_program
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)

        self.streams = image_streams
        self.localization_data = localization_data

        count = len(self.streams)
        self.create_labels_for_streams(count)

        f = Figure(figsize=(5, 4), dpi=100)
        self.subplot = f.add_subplot(111, projection = '3d')

        self.graph = FigureCanvasTkAgg(f, master=self.root)

        self.subplot.mouse_init()
        self.organize_labels()

        self.start_streaming()

        print("Ending GUI")

    def start_streaming(self):
        minimal_distance = 20
        last_point_drawn = None
        while self.stop_event == False:
            for i, stream in enumerate(self.streams):
                if len(stream) < 1:
                    image = self.create_empty_image()
                else:
                    img = stream[-1]

                    if len(self.tracked_points[i]) > 0:
                        coords = self.tracked_points[i][-1]
                        cv2.circle(img[1], coords[1], 5, (0, 0, 255), -1)

                    image = self.process_image(img)

                self.video_labels[i].configure(image = image)
                self.video_labels[i].image = image
            #configure graph label
            if len(self.localization_data) != 0:

                point = self.localization_data[-1]
                if last_point_drawn is None or np.linalg.norm(point - last_point_drawn) > minimal_distance:
                    last_point_drawn = point
                    self.subplot.scatter(*point)
                    self.graph.show()

            self.root.update_idletasks()
            self.root.update()


    def process_image(self, image):
        if isinstance(image, tuple):
            image = image[1]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        return ImageTk.PhotoImage(image)

    def create_labels_for_streams(self, count):
        self.video_labels = []
        import functools
        for i in range(count):
            label = tk.Label(self.root)
            bind = functools.partial(self.click_callback, id=i)
            label.bind("<Button-1>", bind)
            self.video_labels.append(label)

    def organize_labels(self):
        if len(self.video_labels) <= 10: #TODO: ak ich je viacej, tak nejake ine rozlozenie
            for i, label in enumerate(self.video_labels):
                label.grid(row = 0, column = i)
        #self.graph.grid(row = 0, column = len(self.video_labels))
        self.graph.get_tk_widget().grid(row = 0, column = len(self.video_labels))

    def create_empty_image(self):# TODO fix resolution
        img  = Image.new("RGB", (640, 480), "white")
        return ImageTk.PhotoImage(image = img)



if __name__ == '__main__':
    provider = Provider([0, 1])
    provider.initialize_cameras()
    provider.start_capturing()

    gui_actions_queue = Queue()
    gui = GUI(gui_actions_queue)

    queue = Queue()
    queue.put([1, 1, 1])
    queue.put([1, 1, 0])

    guiThread = threading.Thread(target=gui.start, args=(provider.images, queue), name="GUI")
    guiThread.start()
