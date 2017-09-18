#run with python image_downloader.py <num>or<time> and <amount of time in hours>or<number of image> per stream

import threading
import time
import cv2
import numpy as np
import caffe
import sys
GPU_ID = 0  # Switch between 0 and 1 depending on the GPU you want to use.
# caffe.set_mode_gpu()
# caffe.set_device(GPU_ID)
caffe.set_mode_cpu()


cores_load_max = 8*5#6
cores_download_max = 8#2
cores_yolo_max = 8#5

cores_load_current = []
cores_download_current = []
cores_yolo_current = []

loadedStreams = []
imageData = []

global saveThreadCounter
saveThreadCounter = 0
global imagesProcessed
imagesProcessed = 0
global StartTime
StartTime = 0

# Controls the number of feeds to be opened with how many threads. Currently reads in from an input text file of
# m3u8 feeds links. Can be altered to read in from ip cameras as well
def loadStreams():
  streamsDatabase = open("m3u8s2.txt")
  for line in streamsDatabase:
    t = threading.Thread(target=loadStream, args=(line,))
    t.start()
    cores_load_current.append(t)


# Function to load one individual stream. Called from the loadStreams function, which controls threading for loading
# image feeds.
def loadStream(url):
  try:
    cap = cv2.VideoCapture(url)
    if (cap.isOpened()):
      print ("Stream " + str(len(loadedStreams)) + " loaded")
      loadedStreams.append(cap)
  except:
      print (str(url) + " failed to load")
  cores_load_current.pop()


# Downloads images by running through the list of streams loaded previously and calling new threads (up to the maximum
# number specified) to download 100 images at a time from each of the streams, then free up the thread. Once a thread
# is freed, it will load the next item in the list of loadedStreams and begin downloading images from that feed
def downloadImages(type, input):
  print ("Downloading images")
  if (type =="num"):
    for x in range((len(loadedStreams))):
      opened = False
      while (not opened):
        if (len(cores_download_current) < cores_download_max):
          t = threading.Thread(target=numDownloadImage, args=(loadedStreams[x], input,))
          t.start()
          cores_download_current.append(t)
          opened = True
        else:
          time.sleep(0.01)
  if (type == "time"):
    for x in range((len(loadedStreams))):
      opened = False
      while (not opened):
        if (len(cores_download_current) < cores_download_max):
          t = threading.Thread(target=timeDownloadImage, args=(loadedStreams[x], input,))
          t.start()
          cores_download_current.append(t)
          opened = True
        else:
          time.sleep(0.01)


# Downloads images for a set time
def timeDownloadImage(stream, timeToDownload):
  global downloadCounter

  breaker = False
  while ((time.time()-ti2)<timeToDownload):
    if(breaker):
      break
    try:
      frame = stream.read()[1]
      downloadCounter  = downloadCounter + 1
    except:
      print ("Bad Frame")
      pass
  print ("Stream finished downloading")
  cores_download_current.pop()


# Downloads a set number of images
def numDownloadImage(stream, numToDownload):
  global downloadCounter
  print numToDownload
  print type(numToDownload)
  breaker = False
  for x in range(numToDownload):
    if(breaker):
      break
    try:
      frame = stream.read()[1]
      downloadCounter  = downloadCounter + 1
    except:
      print ("Bad Frame")
      pass
  print ("Stream finished downloading")
  cores_download_current.pop()


if __name__ == '__main__':
  # Input validation, makes sure numer of images was entered

  if (len(sys.argv) <= 2):
    print ("Re-Run program with the following input:")
    print ("python image_download.py <num>or<time> <amount of time in hours>or<number of image>")
    exit()
  if ((sys.argv[1] != "num") and (sys.argv[1] != "time")):
    print("Re-run with proper input args")

  global downloadCounter
  downloadCounter = 0


  # Initial loading of streams
  ti = time.time()
  print ("Loading Streams")
  loadStreams()
  # Sleep while streams are still being opened
  while(len(cores_load_current) > 0):
    time.sleep(0.05)
  print ("All streams opened. Downloading now")


  # Initial downloading of images
  print ("Downloading images")
  global ti2
  ti2 = time.time()
  downloadImages(sys.argv[1],sys.argv[2])
  while (len(cores_download_current) > 0):
    # print (str(len(imageData)) + " images downloaded")
    print ("Downloaded " + str(downloadCounter) + " in " + str(time.time() - ti2) + " seconds.")
    print (str(downloadCounter / (time.time() - ti2)) + " FPS")

    print ("waiting on downloading threads to shut down. " + str(len(cores_download_current)) + " remaining")
    time.sleep(0.5)
  print ("Downloaded " + str(downloadCounter) + " in " + str(time.time()-ti2) + " seconds.")
  print (str(downloadCounter/(time.time()-ti2)) + " FPS")

