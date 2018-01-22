import tkinter as tk

import cv2
import time
from PIL import Image, ImageTk

from Provider import Provider


class GUI(object):
    def __init__(self, number_of_cameras, image_streams):
        self.root = tk.Tk()
        self.streams = image_streams
        pass

    def start_streaming(self):
        if len(self.streams[0]) == 0:
            return
        image = self.process_image(self.streams[0][0])

        self.panel = tk.Label(self.root, image=image)
        self.panel.image = image
        self.panel.pack()

    def update_image(self):
        while 1:
            self.start_streaming()

    def stop_streaming(self):
        pass

    def process_image(self, image):
        #print(image)
        if isinstance(image, tuple):
            image = image[1]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        return ImageTk.PhotoImage(image)

if __name__ == '__main__':
    provider = Provider([0])
    provider.initialize_cameras()
    provider.start_capturing()

    gui = GUI(1, provider.images)
    gui.start_streaming()
    gui.root.mainloop()
    gui.update_image()

    time.sleep(10)
    provider.stop_capturing()

