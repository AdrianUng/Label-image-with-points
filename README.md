![](https://github.com/AdrianUng/place_labels/blob/master/repo_snap2.png)
<br/><br/>
This package is meant to address the need for an image point labeling toolbox that works with tkinter
## Packages used:
- OpenCV version 4.8.0.76
- Numpy version 1.25.2
- Pandas version 2.1.1
- Pillow version 10.0.0
- Matplotlib version 3.7.2
- rawpy version 0.18.1

## General description:

Script used to label an image with a finite number of user defined landmarks. The output is a CSV file containing the (x,y) coordinates of the points and the file path of the labeled image.

If a landmark is not placed properly, simply select the name of the landmark and relabel it.

If a landmark is not visible, simply skip it.

When the user is happy with how the points are placed, click the "Next" button or simply click the image again to move to the next point. Once all images are labeled a CSV file is automatically saved to the output folder (if not specified, this is the same folder that the images were stored in.


## Output of ImageLandmarks class:
- CSV file containing the (x,y) coordinates named 'labeled_points.csv'

## Future improvements:
- Delete a landmark.
- Specific point colors assigned for each landmark name.

Please notify me if you find this code useful in any way and end up using it in one of your projects! :)
