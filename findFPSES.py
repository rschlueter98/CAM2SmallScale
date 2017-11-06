import cv2
import time






def downloadImages(inputFile):
    for line in inputFile:
        count=0
        stream = cv2.VideoCapture(line)
        print("New Stream")
        ti = time.time()
        while((time.time()-ti)<10):
            frame = stream.read()[1]
            print("Frame Downloaded")
            if((time.time()-ti>5)):
                count=count+1

        temp = line.split("/")[4]
        temp = temp.split(".")[0]
        FPS = count/5

        print(str(temp) + "\t" + str(FPS))
        outputFile.write(str(temp) + "\t" + str(FPS))

if __name__ == '__main__':
  inputFile = open("m3u8s.txt", 'r')
  outputFile = open("wholeSetFPSES.txt", 'w')
  downloadImages(inputFile)

  # Load yolo model and start analysis
  # loadAnalysis()
