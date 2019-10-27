from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
import json
from django.views.decorators.csrf import csrf_protect
from .forms import *
import os
import shutil
from os import listdir
from os.path import isfile, join
from .linedetector import *
import cv2
import numpy as np

lines = {}
squares = {}
lineID = 0
background_path = None

def index(request):
    chicken = 'Banana'
    template = loader.get_template('planner/index.html')
    context = {
        'lines': lines.items(),
        'squares': squares.items(),
        'lineID': int(lineID),
        'background_path': background_path
    }
    return HttpResponse(template.render(context, request))

@csrf_protect
def save(request):
    global lines, squares, lineID
    json_data = json.loads(request.body)
    lines = json.loads(json_data["lines"])
    squares = json.loads(json_data["squares"])
    lineID = int(json_data["lineID"])
    return JsonResponse(json_data)

def floorplan_image_view(request):
    global background_path
    if request.method == 'POST':
        mypath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'planner', 'images', 'background')
        shutil.rmtree(mypath)
        form = FloorPlanForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            background_path = os.path.join('planner', 'images', 'background', ([f for f in listdir(mypath) if isfile(join(mypath, f))])[0])
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', background_path)
            clean_image(full_path, full_path)
            return redirect('index')
    else:
        form = FloorPlanForm()
    return render(request, 'image_upload.html', {'form' : form})


def success(request):
    return HttpResponse('successfuly uploaded')



# Line Detection Software
def clean_image(before, after):
    # Read the image
    img = cv2.imread(before, 0)

    # Thresholding the image
    (thresh, img_bin) = cv2.threshold(img, 128, 255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    # Invert the image
    img_bin = 255-img_bin
    cv2.imwrite("planner/images/background/Image_bin.png",img_bin)

    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//80

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    cv2.imwrite("planner/images/background/verticle_lines.png",verticle_lines_img)
    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    cv2.imwrite("planner/images/background/horizontal_lines.png",horizontal_lines_img)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    cv2.imwrite(after,img_final_bin)
