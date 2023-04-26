import io
import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera
from picam.ObjectDetector import ObjectDetector
import time

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()
    
    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class Picam:
    def __init__(self):
        self.camera = Picamera2()
        self.obj_detector = ObjectDetector(self.camera)
        self.video_config = self.camera.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"})
        self.video_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
        self.camera.configure(self.video_config)
        self.output = StreamingOutput()
        self.camera.start_recording(JpegEncoder(), FileOutput(self.output))  
        self.thread_abort = False # This will come in handy later

    def livestream(self):
        while not self.thread_abort:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.016)

    def obj_detect(self):
        while not self.thread_abort:
            img, object_info = self.obj_detector.getObjects(0.6, 0.2)
            print(object_info)
            time.sleep(1)

    def start_obj_det(self):
        obj_det_thread = threading.Thread(target=self.obj_detect)
        obj_det_thread.start()
