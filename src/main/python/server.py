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

import sys
import json

from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS


class WSClient(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            log.msg(payload.decode('utf8'))
            event = json.loads(payload.decode('utf8'))

            msg = json.dumps({
                "event": "msg",
                "data": {
                    "msg": "{} from {}".format(
                        event["data"]["msg"],
                        self.peer)
                }
            })

            self.factory.broadcast(msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        self.tick()

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

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))


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


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    WSServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    factory = WSServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = WSClient
    listenWS(factory)

    reactor.run()
