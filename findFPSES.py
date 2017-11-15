import cv2
import time






def downloadImages(inputFile, outputFile):
    for line in inputFile:
        count=0
        max=0
        average=0
        try:
            stream = cv2.VideoCapture(line)
            earthcamID = line.split("/")[4]
            earthcamID = earthcamID.split(".")[0]
            # print(("Checking: " + earthcamID))
            ti = time.time()
            while((time.time()-ti)<120):
                frame = stream.read()[1]
                if((time.time()-ti>60)):
                    count=count+1
                    average=count/(time.time()-(ti+60))
                    if (average>max):
                        max=average
                        maxTime = time.time()-(ti+60)
                    # print(str(count) + ": " + str(count/(time.time()-(ti+60))))

            stream.release()
            output = str(earthcamID) + "\tAverage:\t" + str(average) + "\tMax:\t" + str(max) + "\tat\t" + str(maxTime)
            print(output)
            outputFile.write(output + "\n")
        except Exception as  e:
            print(e)
            stream.release()
            print(str(earthcamID) + "\t" + "failed")
            outputFile.write(str(earthcamID) + "\t" + "failed" + "\n")
            # outputFile.close()
            # exit()
    outputFile.close()


if __name__ == '__main__':
    inputFile = open("m3u8sDownloadingAll.txt", 'r')
    outputFile = open("wholeSetFPSES.txt", 'w')
    downloadImages(inputFile, outputFile)

    inputFile.close()
    outputFile.close()
    # Load yolo model and start analysis
    #  loadAnalysis()
