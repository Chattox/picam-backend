import io
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()
    
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
        print("hello wooooorld")
        

    def livestream(self):
        print("hello world")
        while True:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')