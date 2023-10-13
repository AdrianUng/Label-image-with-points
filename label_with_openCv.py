"""
Created on Wed Aug 22 15:39:58 2018

Adapted code from source: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

@author: adrian ungureanu

Updated on Fri Oct 13 13:55:22 2023
@author: Brandon Hastings
"""
import cv2
import rawpy
import numpy as np
import pandas as pd
import os
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path


# save dictionary created after each folder is analyzed to a csv
def save_csv(dictionary, save_path):
    df = pd.DataFrame(dictionary).T
    df.index.name = "image path"
    df.to_csv(Path(os.path.join(save_path, "labeled_points.csv")))


def compare_labels(label_names, stored_labels):
    # also remove oval_id from dictionary values, leaving only tuple of coordinate points
    for i in stored_labels.keys():
        stored_labels[i] = stored_labels[i][0]
    # get keys from label_names that are not in stored_xy keys (skipped labels) and input nan value
    unlabelled_values = list(set(label_names) - set(stored_labels.keys()))
    for i in unlabelled_values:
        stored_labels[i] = np.nan
    return dict(sorted(stored_labels.items()))


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

        # determine if window wil belong to a higher level tk window
        if toplevel is False:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel()

        # get label names list
        self.label_names = label_names

        # dictionary that holds the label name: [x, y] points for each image. Is cleared with a new image
        self.stored_xy = {}

        # dictionary that holds the image name: stored_xy dictionary for each folder. Is cleared after each folder
        # is completed and saved to a csv or xml file
        self.image_points_dict = {}

        # image size to be set in canvas
        self.canvas_w = image_size
        self.canvas_h = image_size

        # set image as none to be assigned a loaded in instance in methods
        self.image = None
        # the photo assigned to the canvas
        self.photo = self.resize_image()

        # tk window is created out of multiple frames:
        # image frame is made to the size of the resized image
        self.image_frame = tk.Frame(self.window, width=self.canvas_w, height=self.canvas_h)
        # landmark frame will hold radio buttons for each landmark to be labeled
        self.landmark_frame = tk.Frame(self.window)
        # button frame holding "next" and "quit" buttons
        self.button_frame = tk.Frame(self.window)
        # Create a canvas that can fit the given image using adjusted dimensions inside image_frame
        self.canvas = tk.Canvas(self.image_frame, width=self.canvas_w, height=self.canvas_h)
        self.canvas.pack(expand=1)

        # Add PhotoImage to the Canvas
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # bind click and crop function to mouse click
        self.canvas.bind('<Button>', self.click_and_crop)

        # create next button
        button_next = tk.Button(master=self.button_frame, text="Next", command=self.next_button)

        # create quit button
        button_quit = tk.Button(master=self.button_frame, text="Quit", command=self.window.destroy)

        # create radio buttons and set to first button by default
        self.radio_int = tk.IntVar()
        self.radio_int.set(0)
        for i in range(len(self.label_names)):
            radio = tk.Radiobutton(self.landmark_frame, text=self.label_names[i], value=i, variable=self.radio_int)
            radio.configure(fg="black")
            radio.pack()

        # pack buttons to frame
        button_next.pack(side=tk.RIGHT)
        button_quit.pack(side=tk.LEFT)
        # TODO: add toolbar for zooming

        # pack and create the tk window
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
                # check if point has been labeled before (for relabeling purposes). If so, delete and relabel
                if self.label_names[self.radio_int.get()] in self.stored_xy.keys():
                    self.canvas.delete(self.stored_xy[self.label_names[self.radio_int.get()]][1])
                oval_id = self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="blue",
                                                  width=20, outline="")
                self.stored_xy[self.label_names[self.radio_int.get()]] = [(event.x, event.y), oval_id]
                self.radio_int.set(self.radio_int.get() + 1)
            #     exception for if it was last point and no label is selected, assumes labeling is complete
            except IndexError:
                self.next_button()

    '''function to load in image, resize it to given dimensions, and convert to a PIL image type'''

    def resize_image(self):
        # get image path from image list based on how many images have been processed
        image_path = self.image_list[len(self.image_points_dict)]
        # assign self.image to loaded in image path using openCV
        try:
            self.image = cv2.cvtColor(cv2.imread(str(Path(image_path))), cv2.COLOR_BGR2RGB)
        # error handling for a raw image
        except cv2.error:
            raw = rawpy.imread(str(Path(image_path)))
            img = raw.postprocess()
            self.image = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
        # image resolution
        r = self.image_size / self.image.shape[1]
        # image dimensions
        dim = (self.image_size, int(self.image.shape[0] * r))
        # set canvas dimensions based on image dimensions
        self.canvas_w = dim[0]
        self.canvas_h = dim[1]
        # resize cv2 image
        resized = cv2.resize(self.image, dim, interpolation=cv2.INTER_AREA)
        # convert to PIL image so it can be held in tk canvas
        photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
        return photo

    '''next button to save x, y points from last image to dictionary and load next image
    If it's the last image in the folder, saves labels to a csv or xml'''

    def next_button(self):
        # get keys from label_names that are not in stored_xy keys (skipped labels) and input nan value
        # store to larger dict with image name as key, stored_xy dictionary as values
        self.image_points_dict[self.image_list[len(self.image_points_dict)]] = compare_labels(self.label_names,
                                                                                              self.stored_xy)
        # check if all images have been analyzed
        if len(self.image_points_dict) == len(self.image_list):
            save_csv(self.image_points_dict, self.output_folder)
            print("Done")
            self.window.quit()
        else:
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
