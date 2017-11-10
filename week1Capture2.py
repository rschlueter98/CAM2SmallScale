# The program takes an EarthCam source media file to capture frames every 10 minutes for 1 week

import os
import cv2
import time
import datetime
# Path to save the frames
RESULTS_PATH = "/homes/rschluet/SaraCode"

def checkCamera():
    source = "http://video3.earthcam.com/fecnetwork/4054.flv/playlist.m3u8"
    duration = 611000 #300 #611000 (1 week)
    interval = 600 #60 # 600 (10 minute break)
    folderName = source.split("/")[4]
    #folderName = source.split("/")[2] #for IP Cameras
    cam_directory = os.path.join(RESULTS_PATH, str(folderName))

    try:
        os.makedirs(cam_directory)
    except OSError as e:
        if e.errno != 17:
            raise
        pass

    try:
        c = 1
        start = time.time()
        while ((time.time() - start)) < duration:
            vc = cv2.VideoCapture("http://video3.earthcam.com/fecnetwork/4054.flv/playlist.m3u8")
            if not vc.isOpened():
                print("VC did not open")
                return
            capture_time = time.time()
            # Get the image
            rval, frame = vc.read()
            # Save the image.
            file_name = '{}/{}.jpg'.format(cam_directory,datetime.datetime.fromtimestamp(
                        capture_time).strftime('%Y-%m-%d_%H-%M-%S-%f'))
            print(str(file_name))
            cv2.imwrite(str(file_name), frame)
            c = c + 1
            vc.release()
            time.sleep(interval)

        print ("Frames captured over a week: " + str(c-1))
    except Exception as e:
        print e
    vc.release()

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    checkCamera()
    endTime = datetime.datetime.now()
    print("Program took: ")
    print(endTime-startTime)

