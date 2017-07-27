import cv2


url = ["http://video3.earthcam.com/fecnetwork/10072.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10147.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10294.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10347.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10551.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10610.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10669.flv/playlist.m3u8",
        "http://video3.earthcam.com/fecnetwork/10729.flv/playlist.m3u8"]

cap = [0]*8
for x in range(8):
  try:
    cap[x]=cv2.VideoCapture(url[x])
    if cap[x].isOpened():
      print ("Stream: " + str(x) + " opened")
  except:
    print ("Stream: " + str(x) + " failed")

for x in range(8):
  for y in range(10):
    try:
      frame = cap[x].read()[1]
      print ("Image: " + str(x) + str(y) + " succeeded: " + str(len(frame)) + " x " + str(len(frame[0])))
    except:
      print ("Image: " + str(x) + str(y) + " failed")
      pass
