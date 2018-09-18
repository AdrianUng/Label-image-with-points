
"""
Created on Wed Aug 22 15:39:58 2018

Adapted code from source: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

@author: adrian ungureanu
"""
import cv2,glob,numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt

def camera_coord_export_as_XML_v3(file_name,finger_joints_xy,output_folder):
    ''' finger_joints_xy needs to be an np.array of shape 2xn, where n = Nr of points '''
    new_root = ET.Element("leap_coordinates")

    img_name=ET.SubElement(new_root,"img_name")
    img_name.text=file_name

    nr_points=np.size(finger_joints_xy,1)
    finger_joints=ET.SubElement(new_root,"finger_joints", ptCount=str(nr_points))

    for i in range(0,nr_points):
        point_nr="joint%d" % (i+1)        
        ET.SubElement(finger_joints,point_nr, x=str(finger_joints_xy[0,i]), y=str(finger_joints_xy[1,i]))
    tree = ET.ElementTree(new_root)
    tree.write(output_folder+file_name+'.xml')# wrap it in an ElementTree instance, and save as XML
    print('XMLs created')
    return None

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global  point_count,width,length# cropping,refPt,

    if event == cv2.EVENT_LBUTTONDOWN:
        if point_count==6:
            pass
        else:
            cv2.rectangle(image,(x-3,y-3),
                          (x+3,y+3),(0, 255, 0))
            cv2.imshow(window_title, image)
            point_count+=1
            
            stored_xy.append([x,y])
            
def overlap_image_labels(image,stored_xy):
    overlapped_im=image
    for point in stored_xy:
        overlapped_im[point[1]-3:point[1]+3,point[0]-3:point[0]+3,0]=0
        overlapped_im[point[1]-3:point[1]+3,point[0]-3:point[0]+3,1]=255
        overlapped_im[point[1]-3:point[1]+3,point[0]-3:point[0]+3,2]=0
    return overlapped_im
'''
#############################################################################
#####################   Press [q] to reset the labels   #####################
#############################################################################
#####################   Press [s] to export the labels  #####################
#############################################################################
#####################   Press [p] to print the labels   #####################
#############################################################################
'''
stored_xy=[]
point_count=0

folder_source = 'images\\' # location of images to be labeled
output_folder = 'images\\' # where to store the labels 

global_image_list=glob.glob(folder_source+'*.png') # Generating the list of images to be labeled
# change the '.jpg' extension if other image types are used...

image_name=''

fig = plt.figure()
plt.ion()
for (image_nr,image_path) in enumerate(global_image_list):
     window_title='image'
                 
     if image_nr<0: # In case the previous labeling session was suddenly stopped. It basically overlooks all previous images
         pass
     else:
         image_original = cv2.imread(image_path,cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR) # read the image having the orientation it was saved with, otherwise its rotation is reset
         length_orig,width_orig,dim=np.shape(image_original) # image width, length and dimensions
         
         image = cv2.resize(image_original,(256*4,160*4)) # resizin the image to something that can fit easily on the screen
         
         length,width,dim=np.shape(image)
         clone = image.copy() # the initial image is stored, just in case
         cv2.namedWindow(window_title)
         cv2.setMouseCallback(window_title, click_and_crop)
         
         
    # keep looping until the 's' key is pressed
         while True:
    # display the image and wait for a keypress
             cv2.imshow(window_title, image)
             key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, reset the labels
             if key == ord("q"):
                 image = clone.copy()
                 stored_xy=[]
                 point_count=0
    # if the 's' key is pressed, break from the loop
             elif key == ord("s"):
                 overlapped_image=overlap_image_labels(image,stored_xy)
                 
                 stored_xy=np.array(stored_xy,dtype=np.float)
                 stored_xy[:,0]=stored_xy[:,0]/width
                 stored_xy[:,1]=stored_xy[:,1]/length
                 
                 stored_xy=np.transpose(stored_xy)
                 
                 splits=str.split(image_path,'.')
                 splits_2=str.split(splits[0],'\\')
                 
                 fig_name=output_folder+splits_2[1]+'_overlapped.jpg'
                 
                 image_name=splits_2[1]
                 cv2.imwrite(fig_name,overlapped_image)
                 
                 plt.imshow(cv2.cvtColor(overlapped_image,cv2.COLOR_BGR2RGB))
                 plt.title('image:[%s]:' % image_name)
                 plt.tight_layout()
                 plt.show()
                 
                 xml_name=splits_2[1]+'_coord'
                 camera_coord_export_as_XML_v3(xml_name,stored_xy,output_folder)
                 
                 stored_xy=[]
                 point_count=0
                 print ('Created XML for image Nr%d' % image_nr)
                 break
    # if the 'p' key is pressed,  print the stored points...
             elif key == ord("p"): #let's POP the last element in the list!!!
                 print('points before:')
                 print(stored_xy)
                 stored_xy.pop()
                 point_count-=1
                 image = overlap_image_labels(clone.copy(),stored_xy)
                 
                 print('points after:')
                 print(stored_xy)
                 
                 
plt.ioff()
cv2.destroyAllWindows()