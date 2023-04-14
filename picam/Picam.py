import io
import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera

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
        self.video_config = self.camera.create_video_configuration(main={"size": (1280, 720)})
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
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def obj_detect(self):
        while not self.thread_abort:
            print('Hello, world')
            arr = self.camera.capture_array()
            print(arr)
            time.sleep(3)

    def start_obj_det(self):
        obj_det_thread = threading.Thread(target=self.obj_detect)
        obj_det_thread.start()
