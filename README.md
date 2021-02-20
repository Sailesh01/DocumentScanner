# Document Scanner
It is simple GUI based application which can extract document from a given picture if present. The user have to upload the image and then there are two options to extract the document:
- Select ROI ---> the user have to select the four corners of the document in the image and then the application will extract that region of interest.
- Auto Detect ---> the application can automatically detect the document in the image using OpenCV's contour feature.

# Libraries used:
- OpenCV ---> to select the ROI either manually or automatically using contour feature, and to apply warp perspective to display the output image.
- PyQt5 ---> to develop an inractive GUI.

# Demo Video:
![doc_scan](https://user-images.githubusercontent.com/43297280/108591301-32d16280-7390-11eb-9dde-a07d3fef5239.gif)
