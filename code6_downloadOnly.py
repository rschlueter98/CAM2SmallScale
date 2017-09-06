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
  streamsDatabase = open("m3u8s3.txt")
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
def downloadImages(numToDownload):
  print ("Downloading images")
  for x in range(len(loadedStreams)):
    opened = False
    while (not opened):
      if (len(cores_download_current) < cores_download_max):
        t = threading.Thread(target=downloadImage, args=(loadedStreams[x], numToDownload,))
        t.start()
        cores_download_current.append(t)
        opened = True
      else:
        time.sleep(0.01)
  print ("Images downloaded")


# Downloads 100 images from a specified stream. This function is called from the downloadImages function, which
# controlls threading, and decides which stream the threads should download from
def downloadImage(stream, numToDownload):
  print ("downloading stream: " + str(stream))
  global downloadCounter

  breaker = False
  for x in range(numToDownload):
    if(breaker):
      break
    try:
      if ((time.time()-ti)>20):
        print ("DOWNLOADING TIMEOUT")
        breaker = True
        break
      frame = stream.read()[1]
      downloadCounter  = downloadCounter + 1
    except:
      print ("Bad Frame")
      pass
  print ("Finished Downloading")
  cores_download_current.pop()


if __name__ == '__main__':
  # Input validation, makes sure numer of images was entered

  if (len(sys.argv) <= 1):
    print ("Re-Run program with the following input:")
    print ("Python code6_downloadOnly XXXXX")
    print ("Where XXXXX is the number of images per stream to download")
  imagesPerStream = int(sys.argv[1])
  print imagesPerStream
  print type(imagesPerStream)

  print ("This program downloads " + str(imagesPerStream) + " frames worth of image data, does not resize, does not save, does not process")

  global downloadCounter
  downloadCounter = 0


  # Initial loading of streams
  ti = time.time()
  print ("Loading Streams")
  loadStreams()
  # Sleep while streams are still being opened
  while(len(cores_load_current) > 0):
    time.sleep(0.05)
  print ("Number of streams opened: " + str(len(loadedStreams)) + " in " + str(time.time()-ti) + " seconds.")


  # Initial downloading of images
  print ("Downloading images")
  ti2 = time.time()
  downloadImages(imagesPerStream)
  while (len(cores_download_current) > 0):
    print (str(len(imageData)) + " images downloaded")
    print ("waiting on downloading threads to shut down. " + str(len(cores_download_current)) + " remaining")
    time.sleep(0.5)
  print ("Downloaded " + str(downloadCounter) + " in " + time.time()-ti2 + " seconds.")
  print (str(downloadCounter/(time.time()-ti2)) + " FPS")

