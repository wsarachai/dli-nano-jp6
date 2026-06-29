import atexit
import cv2
import numpy as np
import threading
import traitlets

from .camera import Camera


class USBCamera(Camera):

    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=640)
    capture_height = traitlets.Integer(default_value=480)
    capture_device = traitlets.Integer(default_value=0)

    def __init__(self, *args, **kwargs):
        super(USBCamera, self).__init__(*args, **kwargs)
        try:
            self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
            re, image = self.cap.read()
            if not re:
                raise RuntimeError('Could not read image from camera.')
        except Exception:
            raise RuntimeError(
                'Could not initialize camera. '
                'Ensure the USB camera is connected and passed with '
                '--device /dev/videoN to the container.')

        atexit.register(self.cap.release)

    def _gst_str(self):
        return (
            'v4l2src device=/dev/video{device} ! '
            'video/x-raw, width=(int){cw}, height=(int){ch}, '
            'framerate=(fraction){fps}/1 ! '
            'videoconvert ! '
            'video/x-raw, format=(string)BGR ! '
            'appsink drop=1 max-buffers=1 sync=false'
        ).format(
            device=self.capture_device,
            cw=self.capture_width,
            ch=self.capture_height,
            fps=self.capture_fps,
        )

    def _read(self):
        re, image = self.cap.read()
        if re:
            return cv2.resize(image, (int(self.width), int(self.height)))
        else:
            raise RuntimeError('Could not read image from camera')
