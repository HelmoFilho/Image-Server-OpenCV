# Image serving server using Flask and OpenCV

![GitHub last commit](https://img.shields.io/github/last-commit/HelmoFilho/Image-Server-OpenCV)

This api focuses on showing how to serve and save images using the [OpenCV][opencv-docs] library for python for WEB applications. In this api the [Flask][flask-docs] micro-framework was used but the behavior can easily be replicated for other frameworks.

## What is this project about?

As already explained, in this project the use of [OpenCV][opencv-docs] was chosen as the method of serving the images on the WEB. This choice was due to the ease of image manipulation and the high usability rate of the library in other computer vision projects.

Is good to remenber that there is another python image manipulation library known as [PIL][pil-docs] and is much easier to serve and save images using this library, but the performance of the library may be a problem in the long run as it is often lower compared to OpenCV.

Another point is the use o the [Waitress][waitress-docs] library. It is a really good python wsgi and it was used because this project was made on windows and other options like gunicorn are not available (wsl, vm or docker can be used to remedy these problems)

## The api

The API consists of 3 main uses:

 * Listing the folder structure
 * Saving an image in the structure
 * Deleting a directory/image in the structure
 * Serving an image from the structure

All of these uses need to be set the in a directory where the path (absolute or relative to the main.py of the project) is set in the ".env" of the project.
if no folder if given, None of the endpoints will work.

## Usage

1. THe first thing to do is set the values in the ".env" file:

 * The SERVER variable only changes the way the api behaves if it has the value "production". In this case it will use the [Waitress][waitress-docs] to start the application.
    
    * The value "development" is used by default only for the sake of understanding.

 * PORT should be set to a port value that is NOT ALREADY BEING USED BY ANOTHER APPLICATION

 * The CHECK_FOLDER is where the api will look when executing any of the actions explained in the "THE API" section

 * Next are [Waitress][waitress-docs] configuration. THese values are only used when the SERVER is in "production" and should be setted by necessity. More about what these variable can be learned on the [Serve module][waitress-serve-docs] section in the docs.

2. Next the endpoint of "structure"

 * In the structure sections is possible to:
  * Save the image in a folder using a path. If the path to the file does not exists, the api will create it and then save the file there
  * Delete an image/directory. If a path to a file is given, only the file is deleted, if is a directory, all the files in the directory (directory included) are deleted and if nothing is given all files in the predetermined folder (not including the folder) will be deleted
  * List all file and directories in the predetermined folder in a tree structure.

3. Finally, the "serving" endpoint

 * There are four ways to serve an image on the WEB
 
  1. Normal: The path to the image is given in the url and the dimensions of the image will be the original ones
  2. Width and height: It is added the "width" or "height" url params to the "normal" way. If one of the two is given but not the other, the lenght that was not given will be set to be proportional to the length of the given one.
  3. Square: Here the image is proportionaly set to the same length on all 4 sides, and if necessary, white (or transparent depending on the image format) space is added to fit the rest of the image.
  4. circle: Here the image is set to have all length as 2\*Radius and then the middle of the image is cropped using a [OpenCV][opencv-docs] circle.

[flask-docs]: https://flask.palletsprojects.com
[opencv-docs]: https://docs.opencv.org/4.x/
[pil-docs]: https://pillow.readthedocs.io/en/stable/
[waitress-docs]: https://docs.pylonsproject.org/projects/waitress/en/stable/index.html
[waitress-serve-docs]: https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html