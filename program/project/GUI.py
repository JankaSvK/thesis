import threading
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from queue import Queue

import cv2
from PIL import Image, ImageTk

from Provider import Provider

class GUI(object):
    def __init__(self, gui_actions_queue, tracked_points):
        self.mouse_clicks = gui_actions_queue
        self.tracked_points = tracked_points
        pass

    #@staticmethod
    def click_callback(self, event, id):
        print ("clicked at", id,'-', event.x, event.y)
        self.mouse_clicks.put((id, event.x, event.y))
      #  waitForTwoClicks()


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
