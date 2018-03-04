import threading
import tkinter as tk

import logging
import cv2
from PIL import Image, ImageTk
from Provider import Provider

class GUI(object):
    def __init__(self):
        pass

    def start(self, image_streams):
        self.root = tk.Tk()
        self.streams = image_streams

        count = len(self.streams)
        self.create_labels_for_streams(count)

        thread = threading.Thread(target=self.start_streaming, args=())
        thread.start()
        self.root.mainloop()
  #      self.root.mainloop()


    def start_streaming(self):
        while True:
            for i, stream in enumerate(self.streams):
                if len(stream) < 1:
                    image = self.create_empty_image()
                else :
                    image = self.process_image(stream[-1])
                self.video_labels[i].configure(image = image)
                self.video_labels[i].image = image

    def process_image(self, image):
        if isinstance(image, tuple):
            image = image[1]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        return ImageTk.PhotoImage(image)

    def create_labels_for_streams(self, count):
        self.video_labels = []
        for i in range(count):
            self.video_labels.append(tk.Label(self.root))

        self.organize_labels()

    def organize_labels(self):
        if len(self.video_labels) <= 10: #TODO: ak ich je viacej, tak nejake ine rozlozenie
            for i, label in enumerate(self.video_labels):
                label.grid(row = 0, column = i)

    def create_empty_image(self):# TODO fix resolution
        img  = Image.new("RGB", (640, 480), "white")
        return ImageTk.PhotoImage(image = img)



if __name__ == '__main__':
    provider = Provider([0, 1, 2])
    provider.initialize_cameras()
    provider.start_capturing()

    gui = GUI(provider.images)
    gui.start()


    provider.stop_capturing()
    gui.root.quit()
