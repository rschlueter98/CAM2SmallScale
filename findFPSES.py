import cv2
import time






def downloadImages(inputFile):
    for line in inputFile:
        count=0
        try:
            stream = cv2.VideoCapture(line)
            ti = time.time()
            while((time.time()-ti)<120):
                frame = stream.read()[1]
                if((time.time()-ti>75)):
                    count=count+1

            temp = line.split("/")[4]
            temp = temp.split(".")[0]
            FPS = count/45

            print(str(temp) + "\t" + str(FPS))
            outputFile.write(str(temp) + "\t" + str(FPS))
        except:
            print(str(temp) + "\t" + "failed")
            outputFile.write(str(temp) + "\t" + "failed")
            outputFile.close()
            exit()


if __name__ == '__main__':
    inputFile = open("m3u8sDownloadingAll.txt", 'r')
    outputFile = open("wholeSetFPSES.txt", 'w')
    downloadImages(inputFile)

    inputFile.close()
    outputFile.close()
    # Load yolo model and start analysis
    #  loadAnalysis()
