# place_labels
This script is based on a previous post from PyImage Search: https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

General description:
Simple script to label an image with a finite number of landmarks. The output is an XML script containing the (x,y) coordinates of the points.
The points are successively stored in a python list, until the maximum number is reached (in this case 6).
If a landmark was not placed properly, the list containing the points can be popped (until it is empty).

