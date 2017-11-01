#######################################################################################################################
#Header
#This was made by Ryan Schlueter rschlueter98@gmail.com, (314) 603-4504, BSEE '18 on Sep. 18th 2017
#I'm not a coder, so don't hate if this doesn't follow PEP-8 or whatever other standards
#
#This program downloads images from a list of m3u8 streams. It doesn't save them or run yolo or anything
#Run it with: python image_downloader.py <input_filename> <type> <inputValue>
#input_filename is the filename of m3u8 streams you want to download from
#type is either "num" or "time" based of if you want to download for x minutes, or download x images
#inputValue is the above mentioned x. Like 5000 images, or 60 minutes
#
#No output files, FPS is display at the end
#######################################################################################################################


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

#Change these number of cores based of whatever system you are running it on
#I normally used 5*<however_many_threads_your_cpu_has> for loading cores. This is entirely network bound
#Downloading cores are normally 1-1.5x the number of cores you have
#Yolo cores are normally only as many the number of cores you have
#If you're compiling with Intel's Zeon Phi instruction set, mess around with these numbers. Their compilation is weird
cores_load_max = 200
cores_download_max = 200
cores_yolo_max = 80

#Active core counters for various functions
cores_load_current = []
cores_download_current = []
cores_yolo_current = []

#List and queue for loaded streads and downloaded image data
loadedStreams = []
streamNames = []
imageData = []

# Controls the number of feeds to be opened with how many threads. Currently reads in from an input text file of
# m3u8 feeds links. Can be altered to read in from ip cameras as well
def loadStreams(streams_file):
  streamsDatabase = open(streams_file)
  for line in streamsDatabase:
    if not line.startswith("#"):
      opened = False
      while (not opened):
        if(len(cores_load_current) < cores_load_max):
          t = threading.Thread(target=loadStream, args=(line,))
          t.start()
          cores_load_current.append(t)
          time.sleep(0.01)
          opened = True
        else:
          time.sleep(0.01)


# Function to load one individual stream. Called from the loadStreams
def loadStream(url):
  try:
    cap = cv2.VideoCapture(url)
    if (cap.isOpened()):
      print ("Stream " + str(len(loadedStreams)) + " loaded")
      loadedStreams.append(cap)
      temp = url.split("/")[4]
      temp = temp.split(".")[0]
      streamNames.append(temp)
  except:
      print (str(url) + " failed to load")
  cores_load_current.pop()


# Controls number of threads being used for downloading images. Also chooses num or time based off input args
def downloadImages(type, input, saveImage):
  print ("Downloading images")
  if (type =="num"):
    for x in range((len(loadedStreams))):
      opened = False
      while (not opened):
        if (len(cores_download_current) < cores_download_max):
          t = threading.Thread(target=numDownloadImage, args=(loadedStreams[x], streamNames[x], input, saveImage,))
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
          t = threading.Thread(target=timeDownloadImage, args=(loadedStreams[x], streamNames[x],  input, saveImage,))
          t.start()
          cores_download_current.append(t)
          opened = True
        else:
          time.sleep(0.01)


# Downloads images for a set time
def timeDownloadImage(stream, streamName, timeToDownload, saveImage):
  global downloadCounter
  path = "/export/purdue/ryanTesting/saveTesting"
  timeToDownload = timeToDownload * 60
  breaker = False
  startTime = time.time()
  while ((time.time()-startTime)<timeToDownload):
    if(breaker):
      break
    try:
      frame = stream.read()[1]
      if (saveImage):
        filename = ("z_" + str(streamName) + str(downloadCounter) + ".jpg")
        fullpath = (str(path) + "/" + filename)
        cv2.imwrite(str(fullpath), frame)
      else:
        imageData.append(frame)
      downloadCounter = downloadCounter + 1
    except:
      print ("Bad Frame")
      pass
  print ("Stream finished downloading")
  cores_download_current.pop()


# Downloads a set number of images
def numDownloadImage(stream, streamName, numToDownload, saveImage):
  global downloadCounter
  path = "/homes/rschluet/batchDownloadForYolo"
  breaker = False
  for x in range(numToDownload):
    if(breaker):
      break
    try:
      frame = stream.read()[1]
      if(saveImage):
        filename = ("z_" + str(streamName) + "_" + str(downloadCounter) + ".jpg")
        fullpath = (str(path) + "/" + filename)
        cv2.imwrite(str(fullpath), frame)
      else:
        imageData.append(frame)
      downloadCounter  = downloadCounter + 1
    except Exception as e:
      print e
      print ("Bad Frame")
      pass
  print ("Stream finished downloading")
  cores_download_current.pop()



if __name__ == '__main__':
  # Input validation, makes sure numer of images was entered
  if (len(sys.argv) <= 4):
    print ("Re-Run program with the following input:")
    print ("\npython image_download.py <input_filename> <type> <amount> <save type>\n")
    print ("Check the header/docs for more info")
    exit()
  if ((sys.argv[2] != "num") and (sys.argv[2] != "time")):
    print("Re-run with proper input args")

  global downloadCounter
  downloadCounter = 0
  fpses = []
  times = []

  # Initial loading of streams
  ti = time.time()
  print ("Loading Streams")
  loadStreams(sys.argv[1])
  # Sleep while streams are still being opened
  while(len(cores_load_current) > 0):
    time.sleep(0.05)
  print ("All streams opened. Downloading now")


  # Initial downloading of images
  print ("Downloading images")
  ti2 = time.time()
  downloadImages(sys.argv[2],int(sys.argv[3]), sys.argv[4])
  while (len(cores_download_current) > 0):
    # print (str(len(imageData)) + " images downloaded")
    print ("Downloaded " + str(downloadCounter) + " in " + str(time.time() - ti2) + " seconds.")
    print (str(downloadCounter / (time.time() - ti2)) + " FPS")
    fpses.append(str(downloadCounter / (time.time() - ti2)))
    times.append(time.time() - ti2)
    print ("waiting on downloading threads to shut down. " + str(len(cores_download_current)) + " remaining")
    time.sleep(0.5)
  endTime = time.time()
  print ("\n\n")
  print ("FPSes")
  print (fpses)
  print ("\n\n")
  print ("Times")
  print (times)
  print ("\n\n")
  print ("Downloaded " + str(downloadCounter) + " in " + str(endTime - ti2) + " seconds.")
  print (str(downloadCounter/(endTime-ti2)) + " FPS")


