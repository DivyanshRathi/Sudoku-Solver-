# -*- coding: utf-8 -*-
"""SudokuDetector.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ufzNY-Sn7L37dE_AETQ6kNySLuaIx-ge
"""

import cv2 as cv
import numpy as np
from google.colab.patches import cv2_imshow
from tensorflow.keras.models import load_model, model_from_json

def initializePredictionModel():
  json_file = open('model.json', 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  model = model_from_json(loaded_model_json)
  model.load_weights("model_trained.h5")

  return model

model = initializePredictionModel()
heightImage = 450
widthImage = 450
imageDimensions = (32, 32, 3)
pathImage = "img16.jpg"

def preProcess(img):
  imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
  # imgHist = cv.equalizeHist(imgGray)
  imgBlur = cv.GaussianBlur(imgGray,(5,5),1)
  imgThreshold = cv.adaptiveThreshold(imgBlur,255,1,1,11,2)
  return imgThreshold

img = cv.imread(pathImage)
img = cv.resize(img,(widthImage,heightImage))
imgBlank = np.zeros((heightImage,widthImage,3),np.uint8)
imgThreshold = preProcess(img)
cv2_imshow(imgThreshold)

imgContours = img.copy()
imgBigContour = img.copy()
contours, hierarchy = cv.findContours(imgThreshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cv.drawContours(imgContours, contours, -1 , (0,255,0),3)
cv2_imshow(imgContours)

def biggest(contours):
  biggest = contours[0]
  max_area = 0
  for c in contours:
    area = cv.contourArea(c)
    if area > max_area:
      biggest = c
      max_area = area
  return biggest, max_area
# print(len(contours))
biggest, maxArea = biggest(contours)
print(maxArea)

def reorder(contour):
  max_bottom_right = 0
  min_top_left = 1e100
  min_bottom_left = 1e400
  max_top_right = 0

  bottom_right = []
  bottom_left = []
  top_left = []
  top_right = []
  for point in contour:
      if(point[0][1] + point[0][0] > max_bottom_right):
          max_bottom_right = point[0][1] + point[0][0]
          bottom_right = [point[0][0], point[0][1]]

      if(point[0][1] + point[0][0] < min_top_left):
          min_top_left = point[0][1] + point[0][0]
          top_left = [point[0][0], point[0][1]]

      if(point[0][0] - point[0][1] > max_top_right):
          max_top_right = point[0][0] - point[0][1]
          top_right = [point[0][0], point[0][1]]

      if(point[0][0] - point[0][1] < min_bottom_left):
          min_bottom_left = point[0][0] - point[0][1]
          bottom_left = [point[0][0], point[0][1]]

  coordinates = [[top_left], [top_right], [bottom_left], [bottom_right]]
  coordinates = np.array(coordinates, dtype="float32")
  # coordinaes = coordinates.reshape(4,1,2)
  print(coordinates.shape)
  
  return coordinates

# print(biggest)
print(biggest.shape)
# cv2_imshow(imgBigContour)

if biggest.size != 0:
  cv.drawContours(imgBigContour, [biggest], -1, (0,0,250), 20)
  biggest = reorder(biggest)
  pts1 = np.float32(biggest)
  pts2 = np.float32([[0,0],[widthImage,0],[0,heightImage],[widthImage,heightImage]])
  matrix = cv.getPerspectiveTransform(pts1,pts2)
  imgWarpColored = cv.warpPerspective(img,matrix, (widthImage,heightImage))
  imgDetectedDigits = imgBlank.copy()
  imgWarpGray = cv.cvtColor(imgWarpColored, cv.COLOR_BGR2GRAY)
  cv2_imshow(imgBigContour)
  # cv2_imshow(imgWarpColored)
  cv2_imshow(imgWarpGray)

def splitBoxes(img):
  rows = np.vsplit(img, 9)
  boxes = []
  for r in rows:
    cols = np.hsplit(r, 9)
    for box in cols:
      boxes.append(box)
  return boxes

def getPrediction(boxes, model):
  result = []
  for image in boxes:
    img = np.asarray(image)
    img = img[4:img.shape[0] - 4, 4:img.shape[1] - 4]
    img = cv.resize(img, (imageDimensions[0], imageDimensions[1]))
    img = img/255
    img = img.reshape(1, imageDimensions[0], imageDimensions[1], 1)

    predictions = model.predict(img)

    classIndex = np.argmax(predictions, axis = -1)
    probabilityValue = np.amax(predictions)
    # print(classIndex, probabilityValue)
    if probabilityValue > 0.35:
      result.append(classIndex[0])
      ans = classIndex[0]
    else:
      result.append(0)
      ans = 0
    print(ans, probabilityValue)
  return result 

def displayNumbers(img, numbers, color = (0,255,0)):
  secW = int(img.shape[1]/9)
  secH = int(img.shape[0]/9)
  for x in range(0,9):
    for y in range(0,9):
      if(numbers[(y*9) + x] != 0):
        cv.putText(img, str(numbers[(y*9) + x]), 
                   (x*secW + int(secW/2)-10, int((y + 0.8)*secH)), 
                   cv.FONT_HERSHEY_COMPLEX_SMALL, 1, color, 1)
  return img
        
imgSolvedDigits = imgBlank.copy()
# cv2_imshow(imgSolvedDigits)
boxes = splitBoxes(imgWarpGray)
# cv2_imshow(boxes[2])
# print(boxes[2].shape)
numbers = getPrediction(boxes, model)
imgDetectedDigits = displayNumbers(imgSolvedDigits, numbers, color = (255, 0, 255))
cv2_imshow(imgDetectedDigits)
cv2_imshow(img)
numbers = np.asarray(numbers)
# posArray = np.where(numbers > 0, 0, 1)

cv2_imshow(boxes[78])