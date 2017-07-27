import cv2
import threading
import sys
import time
import os

cores_load_max = 8#6
cores_download_max = 8#2
cores_save_max = 8#3
cores_yolo_max = 8#5

cores_load_current = []
cores_download_current = []
cores_save_current = []
cores_yolo_current = []


loadedStreams = []
imageData = []
savedImagesPaths = []
global saveThreadCounter

# Controls the number of feeds to be opened with how many threads. Currently reads in from an input text file of
# m3u8 feeds links. Can be altered to read in from ip cameras as well
def loadStreams():
  streamsDatabase = open("m3u8s3.txt")
  for line in streamsDatabase:
    t = threading.Thread(target=loadStream, args=(line,))
    t.start()
    cores_load_current.append(t)


# Function to load one individual stream. Called from the loadStreams function, which controls threading for loading
# image feeds.
def loadStream(url):
  cap = cv2.VideoCapture(url)
  if (cap.isOpened()):
    loadedStreams.append(cap)
  cores_load_current.pop()


# Downloads images by running through the list of streams loaded previously and calling new threads (up to teh maximum
# number specified) to download 100 images at a time from each of the streams, then free up the thread. Once a thread
# is freed, it will load the next item in the list of loadedStreams and begin downloading images from that feed
def downloadImages():
  print ("Downloading images")
  for x in range(len(loadedStreams)):
    opened = False
    while (not opened):
      if (len(cores_download_current) < cores_download_max):
        t = threading.Thread(target=downloadImage, args=(loadedStreams[x],))
        t.start()
        cores_download_current.append(t)
        opened = True
      else:
        time.sleep(0.01)


# Downloads 100 images from a specified stream. This function is called from the downloadImages function, which
# controlls threading, and decides which stream the threads should download from
def downloadImage(stream):
   for x in range(300):
     imageData.append(stream.read()[1])
   cores_download_current.pop()


# Converts and saves images from the queue of downloaded images (imageData[]). Calls on saveImage to save images from
# the list of raw downloaded data
def saveImages():
  for threadNo in range(cores_save_max):
    t = threading.Thread(target=saveImage, args=(imageData, threadNo,))
    print ("opening saving ")
    t.start()
    cores_save_current.append(t)
  while len(cores_save_current)>0:
    time.sleep(0.1)
  if (len(imageData)!=0):
    global saveThreadCounter
    saveThreadCounter += 1
    saveImages()

# Saves 100 images at a time, then returns the thread
def saveImage(imageData, threadNo):
  time.sleep(0.5)
  path="/home/ryan/Documents/Summer_Research/mMaster/imageOutput"
  for fileNumber in range(100):
    try:
      frame = imageData.pop()
      filename = ("z_" + "iterationNumber" + str(saveThreadCounter) + "threadNumber" + str(threadNo) + "iamgeNumber" + str(fileNumber) + ".jpg")
      fullpath = os.path.join(path, filename)
      a = cv2.imwrite(str(fullpath), frame)
      savedImagesPaths.append(fullpath)
    except Exception as e:
      print e
      print ("out of images")
      break
  cores_save_current.pop()


# def loadAnalysis():
#
#
#
# def analyze():
#
#
#
if __name__ == '__main__':
  saveThreadCounter = 0
  loadStreams()
  while(len(cores_load_current) > 0):
    time.sleep(0.05)
  print ("Number of streams opened: " + str(len(loadedStreams)))
  ti = time.time()
  downloadImages()
  while (len(cores_download_current) > 0):
    time.sleep(0.05)
  print ("Number of images downloaded: " + str(len(imageData)))
  saveImages()
  while (len(cores_save_current) > 0):
    time.sleep(0.05)
  print ("Number of images saved: " + str(len(savedImagesPaths)))
  print (time.time()-ti)

  # while True:
  #   if (cores_save_current==0 and cores_load_current==0):
  #     downloadImages()
  #     saveImages()
  # loadStreams()
  # while(True):
  #   downloadImage()
  # load streams
  # wait til finished
  # start downloading, wait 15(5) seconds then start saving
  # wait 15(5) seconds, then start analyzing