import atexit
import cv2
import numpy as np
import threading
import traitlets

from .camera import Camera


class CSICamera(Camera):
    """
    CSI camera via nvarguscamerasrc (JetPack 6.x / L4T R36+).

    The sensor-mode selects the capture resolution before ISP scaling:
      0 → 3280×2464 @ 21 fps
      1 → 3280×1848 @ 28 fps
      2 → 1920×1080 @ 30 fps
      3 → 1640×1232 @ 30 fps
      4 → 1280×720  @ 60 fps  ← default (best balance of speed and FOV)
    """

    capture_device = traitlets.Integer(default_value=0)
    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=1280)
    capture_height = traitlets.Integer(default_value=720)
    sensor_mode = traitlets.Integer(default_value=4)
    # wbmode: 0=off 1=auto 2=incandescent 3=fluorescent 5=daylight 6=cloudy
    wb_mode = traitlets.Integer(default_value=1)

    def __init__(self, *args, **kwargs):
        super(CSICamera, self).__init__(*args, **kwargs)
        try:
            self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
            re, image = self.cap.read()
            if not re:
                raise RuntimeError('Could not read image from camera.')
        except Exception:
            raise RuntimeError(
                'Could not initialize camera. '
                'Ensure nvargus-daemon is running on the host and '
                '/tmp/argus_socket is mounted into the container.')

        atexit.register(self.cap.release)

    def _gst_str(self):
        # JetPack 6.x pipeline: sensor-mode controls capture resolution;
        # nvvidconv scales and converts to BGRx for OpenCV.
        return (
            'nvarguscamerasrc sensor-id={sensor_id} sensor-mode={mode} wbmode={wb} ! '
            'video/x-raw(memory:NVMM), format=(string)NV12, '
            'framerate=(fraction){fps}/1 ! '
            'nvvidconv flip-method=0 ! '
            'video/x-raw, width=(int){w}, height=(int){h}, '
            'format=(string)BGRx ! '
            'videoconvert ! '
            'video/x-raw, format=(string)BGR ! '
            'appsink drop=1 max-buffers=1 sync=false'
        ).format(
            sensor_id=self.capture_device,
            mode=self.sensor_mode,
            wb=self.wb_mode,
            fps=self.capture_fps,
            w=self.width,
            h=self.height,
        )

    def _read(self):
        re, image = self.cap.read()
        if re:
            return self._correct_wb(image)
        else:
            raise RuntimeError('Could not read image from camera')

    @staticmethod
    def _correct_wb(image):
        # NoIR camera IR correction: IR light bleeds into R and B channels
        # producing a purple cast. Reduce R and B, boost G to compensate.
        img = image.astype(np.float32)
        img[:, :, 0] *= 0.55  # B
        img[:, :, 1] *= 1.15  # G
        img[:, :, 2] *= 0.70  # R
        return np.clip(img, 0, 255).astype(np.uint8)
