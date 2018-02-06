###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
import signal
import sys
import json
import base64
import logging
import time

import imutils
from twisted.internet import reactor
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from websocket.server import *
from websocket.client import *
from camera.camera import *

ip = "192.168.0.120"
cam_url = "rtsp://{ip}:554/user=admin&password=&channel=0&stream=0.sdp?real_stream--rtp-caching=100" \
    .format(ip=ip)

cam_url = 0


def frame2image(frame):
    """
    Converts a frame read by cv2.VideoCapture.read() into a base64-image

    :param frame: Video-Frame
    :return: base64 utf8 string
    """

    # Resize
    # image_scaled = cv2.resize(frame, None, fx=300, fy=200)
    image_scaled = imutils.resize(frame, width=400)

    retval, buffer = cv2.imencode('.png', image_scaled)

    bytes = bytearray(buffer)

    b64_image = base64.b64encode(bytes)
    b64_image = b64_image.decode('utf8')

    frame = None
    return 'data:image/png;base64,' + b64_image


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def signal_handler_function(signum, frame):
    logging.info('Caught signal %d' % signum)
    raise ServiceExit


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    observer = log.PythonLoggingObserver()
    observer.start()

    log.startLogging(sys.stdout)

    cam = Camera(cam_url)

    try:
        #camThread = cam.init()

        WSServerFactory = BroadcastServerFactory
        # ServerFactory = BroadcastPreparedServerFactory

        factory = WSServerFactory(u"ws://127.0.0.1:9000", cam, frame2image)
        factory.protocol = WSClient
        listenWS(factory)

        signal.signal(signal.SIGTERM, signal_handler_function)
        reactor.run()

    except ServiceExit:
        logging.debug("Stopping threads and services...")

    finally:
        #reactor.stop()

        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        cam.shutdown.set()

        # Wait for the threads to close...
        #camThread.join()


    # Release camera and close windows
    cam.release()
    cv2.destroyAllWindows()
    
    logging.info("Exiting main program...")
