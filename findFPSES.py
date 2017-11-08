import cv2
import time






def downloadImages(inputFile, outputFile):
    for line in inputFile:
        count=0
        try:
            stream = cv2.VideoCapture(line)
            earthcamID = line.split("/")[4]
            earthcamID = earthcamID.split(".")[0]

            ti = time.time()
            while((time.time()-ti)<120):
                frame = stream.read()[1]
                if((time.time()-ti>60)):
                    count=count+1
                    print(count + ": " + (count/(time.time()-(ti+60))))


            FPS = count/60

            print(str(earthcamID) + "\t" + str(FPS))
            outputFile.write(str(earthcamID) + "\t" + str(FPS))
        except e:
            print(e)
            print(str(earthcamID) + "\t" + "failed")
            outputFile.write(str(earthcamID) + "\t" + "failed")
            outputFile.close()
            exit()


if __name__ == '__main__':
    inputFile = open("m3u8sDownloadingAll.txt", 'r')
    outputFile = open("wholeSetFPSES.txt", 'w')
    downloadImages(inputFile, outputFile)

    inputFile.close()
    outputFile.close()
    # Load yolo model and start analysis
    #  loadAnalysis()
