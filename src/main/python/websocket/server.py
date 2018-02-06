import sys
import json
import base64
import logging
import time

from twisted.internet import reactor
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from camera.camera import *


class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, cam, frame2base64):
        WebSocketServerFactory.__init__(self, url)

        self.clients = []
        self.tickcount = 0
        self.tick()
        self.cam = cam

        self.frame2base64 = frame2base64

    def tick(self):
        self.tickcount += 1

        msg = json.dumps({
            "event": "tick",
            "data": {
                "msg": "tick {} from server".format(self.tickcount),
                "counter": self.tickcount
            }
        })

        self.broadcast(msg)
        reactor.callLater(10, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

        if len(self.clients) > 0:
            self.cam.start()

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

        if len(self.clients) <= 0:
            self.cam.stop()

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))

    def send_image(self, client):
        logging.debug("send image ..")

        #frame = self.cam.read()
        frame = self.cam.read_directly()
        if frame is None:
            logging.error("Frame was invalid...")
            return

        b64_image = self.frame2base64(frame)

        # logging.info("Base64-Image: {}",b64_image)
        # 'data:image/png;base64,' +

        event = {
            "event": "frame",
            "data": {
                "raw": b64_image,
                'timestamp': time.time()
            }
        }
        client.sendMessage(
            json.dumps(event).encode('utf8')
        )


class BroadcastPreparedServerFactory(BroadcastServerFactory):
    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))

        prepared_msg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(prepared_msg)
            print("prepared message sent to {}".format(c.peer))
