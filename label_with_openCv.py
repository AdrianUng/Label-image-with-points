"""
Created on Wed Aug 22 15:39:58 2018

Adapted code from source: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

@author: adrian ungureanu
"""
import cv2
import numpy as np
import pandas as pd
import os
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path


# save dictionary created after each folder is analyzed to a csv
def save_csv(dictionary, save_path):
    df = pd.DataFrame(dictionary)
    df.to_csv(save_path)


# get keys from label_names that are not in stored_xy keys (skipped labels) and input nan value
def compare_labels(label_names, stored_labels):
    unlabelled_values = list(set(label_names) - set(stored_labels.keys()))
    for i in unlabelled_values:
        stored_labels[i] = np.nan
    return dict(sorted(stored_labels.items()))


# TODO: check rgb arrays from cvtColor


class ImageLandmarks:
    def __init__(self, source_folder, label_names, output_folder=None, image_type=None, toplevel=False,
                 thickness=10, image_size=400):

        # default thickness
        self.thickness = thickness
        # default image resize
        self.image_size = image_size
        # determine image type
        if image_type is not None:
            self.image_type = image_type
        elif image_type is None:
            self.image_type = ".png"

        # determine if the input file is a folder or single file
        if os.path.isdir(source_folder):
            self.source_folder = source_folder
            self.image_list = [os.path.join(source_folder, i) for i in os.listdir(source_folder) if
                               i.lower().endswith(self.image_type)]
        elif os.path.isfile(source_folder):
            self.source_folder = os.path.dirname(source_folder)
            self.image_list = [source_folder]

        self.n_points = len(label_names)

        # where to store the labels
        if output_folder is not None:
            self.output_folder = output_folder
        if output_folder is None:
            self.output_folder = source_folder
        if toplevel is False:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel()

        self.label_names = label_names

        self.image_points_dict = {}
        self.stored_xy = {}

        # canvas and image instance to be assigned in methods
        self.canvas_w = image_size
        self.canvas_h = image_size
        # self.canvas = tk.Canvas(self.window, width=400, height=400)
        self.image = None
        self.photo = self.resize_image()

        self.image_frame = tk.Frame(self.window, width=self.canvas_w, height=self.canvas_h)
        self.landmark_frame = tk.Frame(self.window)
        self.button_frame = tk.Frame(self.window)
        # Create a canvas that can fit the given image using adjusted dimensions
        self.canvas = tk.Canvas(self.image_frame, width=self.canvas_w, height=self.canvas_h)
        self.canvas.pack(expand=1)

        # Add PhotoImage to the Canvas
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # bind click and crop function to mouse click
        self.canvas.bind('<Button>', self.click_and_crop)

        button_next = tk.Button(master=self.button_frame, text="Next", command=self.next_button)

        button_quit = tk.Button(master=self.button_frame, text="Quit", command=self.window.destroy)

        self.radio_dict = {}
        self.radio_test_dict = {}
        self.radio_int = tk.IntVar()
        self.radio_int.set(0)
        for i in range(len(self.label_names)):
            radio = tk.Radiobutton(self.landmark_frame, text=self.label_names[i], value=i, variable=self.radio_int)
            radio.configure(fg="black")
            radio.pack()

            self.radio_dict[self.label_names[i]] = radio, radio
            self.radio_test_dict[radio] = self.label_names[i]
        print(self.radio_dict)

        button_next.pack(side=tk.RIGHT)
        button_quit.pack(side=tk.LEFT)
        # toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=0)

        self.image_frame.pack(side=tk.LEFT)
        self.landmark_frame.pack(side=tk.RIGHT)
        self.button_frame.pack(side=tk.BOTTOM)
        self.window.mainloop()

    def click_and_crop(self, event):
        # click again after placing last point to continue to next image
        if len(self.stored_xy.keys()) == len(self.label_names):
            self.next_button()
        else:
            try:
                self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="blue", width=20,
                                        outline="")
                self.stored_xy[self.label_names[self.radio_int.get()]] = event.x, event.y
                self.radio_int.set(self.radio_int.get() + 1)
                print(self.stored_xy)
            #     exception for if it was last point and no label is selected, assumes labelling is complete
            except IndexError:
                self.next_button()

    def resize_image(self):
        image_path = self.image_list[len(self.image_points_dict)]
        self.image = cv2.cvtColor(cv2.imread(str(Path(image_path))), cv2.COLOR_BGR2RGB)
        r = self.image_size / self.image.shape[1]
        dim = (self.image_size, int(self.image.shape[0] * r))
        self.canvas_w = dim[0]
        self.canvas_h = dim[1]
        # resized cv2 image
        resized = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        # PIL image
        photo = ImageTk.PhotoImage(image=Image.fromarray(resized))

        return photo

    def next_button(self):
        # check if all images have been analyzed, if not:
        if len(self.image_points_dict) < len(self.image_list):
            # get keys from label_names that are not in stored_xy keys (skipped labels) and input nan value
            # store to larger dict with image name as key, stored_xy dictionary as values
            self.image_points_dict[self.image_list[len(self.image_points_dict)]] = compare_labels(self.label_names, self.stored_xy)
            print(self.image_points_dict)
            # resize next image
            self.photo = self.resize_image()
            # clear stored_xy points from last image
            self.stored_xy.clear()
            # clear canvas
            self.canvas.delete("all")
            # configure canvas to new dimensions
            self.canvas.configure(height=self.canvas_h, width=self.canvas_w)
            # set image to top left corner
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            # reset radio int selection variable
            self.radio_int.set(0)
        else:
            save_csv(self.image_points_dict, self.output_folder+"/saved_points")
            print("Done")
            self.window.quit()


# if __name__ == "__main__":
#     ImageLandmarks(source_folder="/Users/brandonhastings/Desktop/modified_images/image/original/VIS/20210624/modified",
#                    label_names=["left eye", "right eye", "neck"])
