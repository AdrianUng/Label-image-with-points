This script is based on a previous post from PyImage Search. You can access the original tutorial here: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

## Packages used:
- OpenCV version 3.4.0
- Numpy version 1.14.0
- Matplotlib version 1.4.3
- xml

## General description:

Script used to label an image with a finite number of landmarks. The output is an XML script containing the (x,y) coordinates of the points.

The points are successively added in a python list, until the maximum number is reached (in this case 6).
If a landmark was not placed properly, the list containing the points can be popped (until it is empty) by pressing the 'p' key.

When the user is happy with how the points are placed, the list containing them is fed to a function which normalizes their values (float from 0 to 1) and writes an XML file. Furthermore, a small image is saved in the 'destination folder' to allow the easy inspection of the landmarks later on. 

Green squares of side=6 pixels are displayed centered on the landmark's (x,y) values.

In order to aid the consistent placing of landmarks in a context where this task is very difficult, both cv2.imshow() and plt.imshow() are being used, allowing the user to easily inspect the landmarks from the previous image (as displayed in 'git_screen1.png')

![alt text](https://github.com/AdrianUng/place_labels/blob/master/git_screen1.png)

In order to completely clear the list of landmarks 'q' is pressed.

## Output of script:
- XML file containing the (x,y) coordinates named 'imageName_coord.xml'
- JPG file of smaller size displaying both the final orientation of the image, as well as the placed landmarks, named 'imageName_overlapped.jpg'

## Future improvements:

[ ] rotate the image by pressing 'r' and allow the placing of landmarks at the **(x,y)** coordinates regardless of the image's orientation

[ ] change the landmark placing order in order to facilitate the more accurately alignment of the points **#3** to **#6**





Please notify me if you find this code useful in any way and end up using it in one of your projects! :)
