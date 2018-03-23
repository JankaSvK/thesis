import threading
import tkinter as tk

import sys

import numpy as np
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

    def do_nothing(self):
        pass

    def draw_cameras(self, cameras):
        for i, cam in enumerate(cameras):
            s, e = cam['start'], cam['end']
            self.subplot.scatter(s['x'], s['y'], s['z'], s=0.1) # Plot is not changing camera view to see arrows, so creating point to include
            a = Arrow3D([s['x'], e['x']], [s['y'], e['y']], [s['z'], e['z']], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")
            self.subplot.add_artist(a)
            self.subplot.text(s['x'] + 5, s['y'], s['z'], i)

    #@staticmethod
    def click_callback(self, event, id):
        print ("clicked at", id,'-', event.x, event.y)
        QueuesProvider.add_mouse_click(window_index=id, x=event.x, y=event.y)

    def start(self, image_streams, localization_data = []):
        self.root = tk.Tk()

        self.streams = image_streams
        self.localization_data = localization_data

        count = len(self.streams)
        self.create_labels_for_streams(count)

        f = Figure(figsize=(5, 4), dpi=100)
        self.subplot = f.add_subplot(111, projection = '3d')

        self.graph = FigureCanvasTkAgg(f, master=self.root)
        self.subplot.mouse_init()
        self.organize_labels()

        #TODO: preco sa zakladaju dva thready?!?!?!
        thread = threading.Thread(target=self.start_streaming, args=())
        thread.start()
        self.root.mainloop()


    def start_streaming(self):
        minimal_distance = 20
        last_point_drawn = None
        while True:
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
                    self.subplot.scatter(point[0], point[1], point[2])
                    self.graph.show()

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
