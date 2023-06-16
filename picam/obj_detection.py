import cv2
from picamera2 import Picamera2
import libcamera

classNames = []
classFile = "/home/pi/Documents/Coding/picam-backend/picam/obj_ident_data/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Documents/Coding/picam-backend/picam/obj_ident_data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Documents/Coding/picam-backend/picam/obj_ident_data/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(
        img, confThreshold=thres, nmsThreshold=nms)

    if len(objects) == 0:
        objects = classNames
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if (draw):
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0, 255, 0), 2)
                    cv2.putText(img,str(round(confidence*100, 2)),(box[0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0, 255, 0), 2)
    
    return img, objectInfo

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    config["transform"] = libcamera.Transform(hflip=1, vflip=1)
    picam2.configure(config)
    picam2.start()

    while True:
        img = picam2.capture_array()
        result, objectInfo = getObjects(img, 0.6, 0.2)
        cv2.imshow("Output", img)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('objdetect.png', img)
