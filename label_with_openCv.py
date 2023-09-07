"""
Created on Wed Aug 22 15:39:58 2018

Adapted code from source: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

@author: adrian ungureanu
"""
import sys
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import os
from pathlib import Path


def camera_coord_export_as_XML_v3(file_name, finger_joints_xy, output_folder):
    ''' finger_joints_xy needs to be an np.array of shape 2xn, where n = Nr of points '''
    new_root = ET.Element("leap_coordinates")

    img_name = ET.SubElement(new_root, "img_name")
    img_name.text = file_name

    nr_points = np.size(finger_joints_xy, 1)
    finger_joints = ET.SubElement(new_root, "finger_joints", ptCount=str(nr_points))

    for i in range(0, nr_points):
        point_nr = "joint%d" % (i + 1)
        ET.SubElement(finger_joints, point_nr, x=str(finger_joints_xy[0, i]), y=str(finger_joints_xy[1, i]))
    tree = ET.ElementTree(new_root)
    tree.write(output_folder + file_name + '.xml')  # wrap it in an ElementTree instance, and save as XML
    print('XMLs created')
    return None


# def click_and_crop(event, x, y, flags, param):
#     # grab references to the global variables
#     global point_count, width, length  # cropping,refPt,
#
#     if event == cv2.EVENT_LBUTTONDOWN:
#         if point_count >= n_labels:
#             pass
#         else:
#             cv2.rectangle(image, (x - 3, y - 3),
#                           (x + 3, y + 3), (0, 255, 0))
#             cv2.imshow(window_title, image)
#             point_count += 1
#
#             stored_xy.append([x, y])


def overlap_image_labels(image, stored_xy):
    overlapped_im = image
    for point in stored_xy:
        overlapped_im[point[1] - 10:point[1] + 10, point[0] - 10:point[0] + 10, 0] = 255
        overlapped_im[point[1] - 10:point[1] + 10, point[0] - 10:point[0] + 10, 1] = 0
        overlapped_im[point[1] - 10:point[1] + 10, point[0] - 10:point[0] + 10, 2] = 255
    return overlapped_im


    # @staticmethod
    # def pop_up(fig, subroot):
    #     canvas = FigureCanvasTkAgg(fig, master=subroot)
    #     canvas.draw()
    #
    #     toolbar = NavigationToolbar2Tk(canvas, subroot, pack_toolbar=False)
    #     toolbar.update()
    #
    #     canvas.mpl_connect(
    #         "key_press_event", lambda event: print(f"you pressed {event.key}"))
    #     canvas.mpl_connect("key_press_event", key_press_handler)
    #
    #     button_quit = tk.Button(master=subroot, text="Quit", command=subroot.destroy)
    #     return [button_quit, toolbar, canvas]
    #
    # '''toolbar functions for selecting image'''
    #
    # @staticmethod
    # def image_selection(subroot, n_cluster, command, canvas, start=1, end=1):
    #     options = list(range(start, n_cluster + end))
    #     # convert to strings
    #     options = [str(x) for x in options]
    #     #
    #     variable = tk.StringVar(subroot)
    #     variable.set(options[0])
    #     selector = tk.OptionMenu(subroot, variable, *options, command=command)
    #     canvas[0].pack(side=tk.BOTTOM)
    #     selector.pack(side=tk.BOTTOM)
    #     canvas[1].pack(side=tk.BOTTOM, fill=tk.X)
    #     canvas[2].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

'''
#############################################################################
#####################   Press [q] to reset the labels   #####################
#############################################################################
#####################   Press [s] to export the labels  #####################
#############################################################################
#####################   Press [p] to print the labels   #####################
#############################################################################
'''

# TODO: potentially add method to display image within tkinter canvas. label_names=None (dict), tk.toplevel=None


class ImageLandmarks:
    def __init__(self, source_folder, n_points, output_folder=None, label_names=None, image_type=None, toplevel=False,
                 save_xml=False, thickness=10):
        # default thickness
        self.thickness = thickness
        # determine image type
        if image_type is None:
            self.image_type = ".png"
        elif image_type is not None:
            self.image_type = image_type

        if os.path.isdir(source_folder):
            self.source_folder = source_folder
            self.image_list = [os.path.join(source_folder, i) for i in os.listdir(source_folder) if i.endswith(image_type)]
        elif os.path.isfile(source_folder):
            self.source_folder = os.path.dirname(source_folder)
            self.image_list = [source_folder]

        self.n_points = int(n_points)
        # where to store the labels
        if output_folder is None:
            self.output_folder = source_folder
        elif output_folder is not None:
            self.output_folder = output_folder

        self.save_xml = save_xml

        self.window_title = 'image'

        self.stored_xy = []
        self.point_count = 0

        self.image = None

    def click_and_crop(self, event, x, y, flags, param):
        # grab references to the global variables
        global width, length  # cropping,refPt,

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.point_count >= self.n_points:
                pass
            else:
                # cv2.rectangle(self.image, (x - 10, y - 10),
                #               (x + 10, y + 10), (0, 0, 255), thickness=self.thickness)
                cv2.circle(self.image, (x, y), color=(0, 0, 255), radius=self.thickness, thickness=-1)
                # cv2.imshow(self.window_title, self.image)
                self.point_count += 1

                self.stored_xy.append([x, y])


    def main(self):
        # Generating the list of images to be labeled
        # global_image_list = [i for i in os.listdir(self.source_folder) if i.endswith(self.image_type)]
        # print(global_image_list)

        image_points_dict = {}

        # fig = plt.figure()
        plt.ion()

        for (image_nr, image_path) in enumerate(self.image_list):

            self.stored_xy = []

            # window_title = 'image'
            print(image_path)
            image_name = os.path.basename(image_path)
            window_title = image_name
            print(image_name)

            if image_nr < 0:  # In case the previous labeling session was suddenly stopped. It basically overlooks all previous images
                pass
            else:
                print(str(Path(image_path)))
                print(str(Path(os.path.join(self.source_folder, image_name))))
                image_original = cv2.imread(str(Path(image_path)))  # read the image having the orientation it was saved with, otherwise its rotation is reset
                length_orig, width_orig, dim = np.shape(image_original)  # image width, length and dimensions

                self.image = image_original

                # self.image = cv2.resize(image_original,
                #                    (width_orig, length_orig))  # resizin the image to something that can fit easily on the screen

                length, width, dim = np.shape(self.image)
                clone = self.image.copy()  # the initial image is stored, just in case
                cv2.namedWindow(window_title)
                cv2.setMouseCallback(window_title, self.click_and_crop)

                # keep looping until the 's' key is pressed
                while True:
                    # display the image and wait for a keypress
                    cv2.imshow(window_title, self.image)
                    key = cv2.waitKey(1) & 0xFF
                    # if the 'q' key is pressed, reset the labels
                    if key == ord("q"):
                        self.image = clone.copy()
                        self.stored_xy.clear()
                        self.point_count = 0
                    # if the 's' key is pressed, break from the loop
                    elif key == ord("s"):
                        overlapped_image = overlap_image_labels(self.image, self.stored_xy)

                        stored_xy_array = np.array(self.stored_xy.copy(), dtype=float)
                        stored_xy_array[:, 0] = stored_xy_array[:, 0] / width
                        stored_xy_array[:, 1] = stored_xy_array[:, 1] / length

                        stored_xy_array = np.transpose(stored_xy_array)

                        fig_name = os.path.join(self.output_folder, image_name+'_overlapped.png')

                        image_name = image_name
                        # cv2.imwrite(fig_name, overlapped_image)

                        # plt.imshow(cv2.cvtColor(overlapped_image, cv2.COLOR_BGR2RGB))
                        # plt.title('image:[%s]:' % image_name)
                        # plt.tight_layout()
                        # plt.show()

                        if self.save_xml is True:
                            xml_name = image_name + '_coord'
                            camera_coord_export_as_XML_v3(xml_name, stored_xy_array, self.output_folder)

                            self.stored_xy.clear()
                            self.point_count = 0
                            print('Created XML for image Nr%d' % image_nr)
                            # break
                        else:
                            print(self.stored_xy)
                            image_points_dict[image_name] = self.stored_xy.copy()
                            self.stored_xy.clear()
                            self.point_count = 0
                            # return self.stored_xy
                        break
                    # if the 'p' key is pressed,  print the stored points...
                    elif key == ord("p"):  # let's POP the last element in the list!!!
                        if len(self.stored_xy) < 1:
                            print("No points labelled yet.")
                        else:
                            print('points before:')
                            print(self.stored_xy)
                            self.stored_xy.pop()
                            self.point_count -= 1
                            self.image = overlap_image_labels(clone.copy(), self.stored_xy)

                            print('points after:')
                            print(self.stored_xy)

            # self.stored_xy.clear()

            plt.ioff()
            cv2.destroyAllWindows()
        print(image_points_dict)
        return image_points_dict


if __name__ == "__main__":
    ImageLandmarks(sys.argv[1], sys.argv[2]).main()
