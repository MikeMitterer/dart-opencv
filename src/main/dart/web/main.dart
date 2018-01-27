// Copyright (c) 2018, Mike Mitterer. All rights reserved. Use of this source code
// is governed by a BSD-style license that can be found in the LICENSE file.

// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the COPYING file.

// This is a simple example of using Websockets.
// See: http://www.html5rocks.com/en/tutorials/websockets/basics/
//      https://github.com/sethladd/Dart-Web-Sockets
//
// This has been tested under Chrome and Firefox.

import 'dart:html' as dom;
import 'dart:async';
import 'dart:convert';

logMsg(final String msg) {
    final dom.PreElement output = dom.querySelector('#log') as dom.PreElement;
    var text = msg;
    if (!output.text.isEmpty) {
        text = "${output.text}\n${text}";
    }
    output.text = text;
    output.scrollTop = output.scrollHeight;
}

dom.WebSocket initWebSocket([int retrySeconds = 10]) {
    var reconnectScheduled = false;

    logMsg("Connecting to websocket");

    String wsuri = "ws://" + dom.window.location.hostname + ":9000";
    if (dom.window.location.protocol.startsWith("file:")) {
        wsuri = "ws://localhost:9000";
    }

    final ws = new dom.WebSocket(wsuri);

    void scheduleReconnect() {
        if (!reconnectScheduled) {
            new Timer(new Duration(milliseconds: 1000 * retrySeconds), () => initWebSocket(retrySeconds * 2));
        }
        reconnectScheduled = true;
    }

    ws.onOpen.listen((e) {
        logMsg('Connected');
        ws.send(JSON.encode({
            "event" : "msg",
            "data": {
                "msg" : 'Hello from Dart!'
            }
        }));

    });

    ws.onClose.listen((e) {
        logMsg('Websocket closed, retrying in $retrySeconds seconds');
        scheduleReconnect();
    });

    ws.onError.listen((e) {
        logMsg("Error connecting to ws");
        scheduleReconnect();
    });

    ws.onMessage.listen((final dom.MessageEvent e) {
        final Map data = JSON.decode(e.data);
        
        switch(data["event"]) {
            case "msg":
                logMsg('Message: ${data["data"]["msg"]}');
                break;
            case "tick":
                logMsg('Tick: ${data["data"]["msg"]}');
                break;
            default:
                logMsg('Unknown event: ${e.data}');
        }
    });

    return ws;
}

void main() {
    final dom.WebSocket ws = initWebSocket();
    final button = dom.querySelector("#broadcast") as dom.ButtonElement;

    button.onClick.listen((_) {
        if(ws.readyState == dom.WebSocket.OPEN) {
            final String message = (dom.querySelector("#message") as dom.InputElement).value;
            if(message.isNotEmpty) {
                ws.send(JSON.encode({
                    "event" : "msg",
                    "data": {
                        "msg" : message
                    }
                }));
            }
        }
    });
}