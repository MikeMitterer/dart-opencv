import threading

import cv2
from threading import Thread, Lock
import logging
import time


# Our sketch generating function
def sketch(image):
    # Resize
    image_scaled = cv2.resize(image, None, fx=0.33, fy=0.33)

    # Convert image to grayscale
    img_gray = cv2.cvtColor(image_scaled, cv2.COLOR_BGR2GRAY)

    # Clean up image using Guassian Blur
    img_gray_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # Extract edges
    canny_edges = cv2.Canny(img_gray_blur, 10, 70)

    # Do an invert binarize the image
    ret, mask = cv2.threshold(canny_edges, 70, 255, cv2.THRESH_BINARY_INV)
    return mask


class Camera(object):

    def __init__(self, camid=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.cam = cv2.VideoCapture(camid)

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

        # self.cam.set(cv2.CAP_PROP_FPS, fps)
        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])

        self.frame = None
        (self.retval, self.tempFrame) = self.cam.read()
        if self.retval:
            self.frame = self.tempFrame

        self.lock = Lock()

        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown = threading.Event()

        self.locked = False

    def init(self):
        """Start the thread to read frames from the video stream"""

        thread = Thread(target=self.update, args=())
        thread.start()

        return thread

    def start(self):

        try:
            self.lock.acquire()
            self.stopped = False

        finally:
            self.lock.release()

    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.shutdown.is_set():

            # if the thread indicator variable is set, stop the thread
            if not self.stopped:
                try:
                    self.lock.acquire()
                    logging.debug('Acquired a lock')

                    # otherwise, read the next frame from the stream
                    # (self.grabbed, self.frame) = self.cam.read()
                    (self.retval, self.tempFrame) = self.cam.read()
                    # self.cam.release()

                    if self.retval:
                        self.frame = self.tempFrame

                    # cv2.imshow('Our Live Sketcher', sketch(self.frame))
                    # cv2.waitKey(1)

                finally:
                    logging.debug('Released a lock')
                    self.lock.release()

                    time.sleep(0.1)
            else:
                time.sleep(0.5)

        # ~24Frames p. sec
        # time.sleep(0.5)

    def read(self):
        """Return the frame most recently read"""

        try:
            self.lock.acquire()
            return self.frame

        finally:
            self.lock.release()

    def read_directly(self):
        # self.frame = None

        self.lock.acquire()
        while self.locked:
            time.sleep(0.1)

        self.locked = True

        (self.retval, self.tempFrame) = self.cam.read()
        #time.sleep(0.1)
        # self.cam.release()

        if self.tempFrame is not None:
            self.frame = self.tempFrame

            # cv2.imshow('Our Live Sketcher', sketch(self.frame))
            # cv2.waitKey(1)

        else:
            logging.error("CAM-read failed!")
            self.cam.release()

        self.lock.release()
        self.locked = False

        return self.frame

    def stop(self):
        """indicate that the thread should be stopped"""

        try:
            self.lock.acquire()
            self.stopped = True

        finally:
            self.lock.release()

    def release(self):
        self.cam.release()
