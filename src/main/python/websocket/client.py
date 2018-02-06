import sys
import json
import base64
import logging
import time

from twisted.internet import reactor
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from camera.camera import *


class WSClient(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            log.msg(payload.decode('utf8'))
            json_event = json.loads(payload.decode('utf8'))

            event_type = json_event["event"]
            if event_type == "msg":
                self.factory.broadcast(
                    json.dumps({
                        "event": "msg",
                        "data": {
                            "msg": "{} from {}".format(
                                json_event["data"]["msg"],
                                self.peer)
                        }
                    })
                )

            elif event_type == "pull-image":
                self.factory.broadcast(
                    json.dumps({
                        "event": "msg",
                        "data": {
                            "msg": "Yup - images is coming!"
                        }
                    })
                )
                self.factory.send_image(self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)
