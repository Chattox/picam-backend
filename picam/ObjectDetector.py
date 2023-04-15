import os
import cv2 as cv
from picamera2 import Picamera2
import libcamera

class ObjectDetector:
    def __init__(self, stream):
        self.stream = stream
        self.directory = os.path.dirname(__file__)
        self.class_names = []
        self.class_file = os.path.join(self.directory, "obj_ident_data/coco.names")
        print(self.class_file)
        with open(self.class_file, "rt") as f:
            self.class_names = f.read().rstrip("\n").split("\n")
        self.config_path = os.path.join(self.directory, "obj_ident_data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")
        self.weights_path = os.path.join(self.directory, "obj_ident_data/frozen_inference_graph.pb")
        self.net = cv.dnn_DetectionModel(self.weights_path, self.config_path)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

    def getObjects(self, thres, nms, draw=True, objects=[]):
        img = self.stream.capture_array()
        class_ids, confs, bbox = self.net.detect(img, confThreshold=thres, nmsThreshold=nms)

        if len(objects) == 0:
            objects = self.class_names
        
        object_info = []
        
        if len(class_ids) != 0:
            for class_id, confidence, box in zip(class_ids.flatten(), confs.flatten(), bbox):
                class_name = self.class_names[class_id - 1]
                if class_name in objects:
                    object_info.append([box, class_name])
                    if (draw):
                        cv.rectangle(img, box, color=(0, 255, 0), thickness=2)
                        cv.putText(img, self.class_names[class_id - 1].upper(), (box[0] + 10, box[1] + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                        cv.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                        
        return img, object_info
