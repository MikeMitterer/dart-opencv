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

import 'package:opencv/fps.dart';

void logMsg(final String msg) {
    final dom.PreElement output = dom.querySelector('#log') as dom.PreElement;
    var text = msg;
    if (!output.text.isEmpty) {
        text = "${output.text}\n${text}";
    }
    output.text = text;
    output.scrollTop = output.scrollHeight;
}

dom.WebSocket initWebSocket(final FPS fps, bool isPauseState(), [final int retrySeconds = 10]) {
    var reconnectScheduled = false;

    logMsg("Connecting to websocket");

    String wsuri = "ws://" + dom.window.location.hostname + ":9000";
    if (dom.window.location.protocol.startsWith("file:")) {
        wsuri = "ws://localhost:9000";
    }

    final ws = new dom.WebSocket(wsuri);

    void scheduleReconnect() {
        if (!reconnectScheduled) {
            new Timer(new Duration(milliseconds: 1000 * retrySeconds),
                    () => initWebSocket(fps, isPauseState, retrySeconds * 2));
        }
        reconnectScheduled = true;
    }

    ws.onOpen.listen((e) {
        logMsg('Connected');
        ws.send(JSON.encode({
            "event": "msg",
            "data": {"msg": 'Hello from Dart!'}
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

        switch (data["event"]) {
            case "msg":
                logMsg('Message: ${data["data"]["msg"]}');
                break;
            case "tick":
                logMsg('Tick: ${data["data"]["msg"]}');
                break;
            case "frame":
                final canvasElement = dom.querySelector("#video") as dom.CanvasElement;
                final contextElement = canvasElement.getContext("2d") as dom
                    .CanvasRenderingContext2D;
                final image = new dom.ImageElement(width: 422, height: 316);
                final base64 = data["data"]["raw"] as String;

                logMsg("Image: ${base64.substring(0, 35)}...${base64.substring(base64.length - 15)}");

                // Trigger next frame
                if (!isPauseState()) {
                    ws.send(JSON.encode({"event": "pull-image"}));
                }

                image.src = "";
                image.onLoad.listen((_) {
                    //context.drawImage(image, canvas.width, canvas.height);
                    contextElement.drawImageScaled(image, 0, 0, 422, 316);
                    logMsg("Image should have changed...");
                });
                image.src = data["data"]["raw"] as String;

                fps.update();
                break;
            default:
                logMsg('Unknown event: ${data["event"]}');
        }
    });

    return ws;
}

void main() {
    bool pauseState = true;
    final FPS fps = new FPS();
    final dom.WebSocket ws = initWebSocket(fps, () => pauseState);
    final btnBroadcast = dom.querySelector("#broadcast") as dom.ButtonElement;
    final btnPlay = dom.querySelector("#play") as dom.ButtonElement;
    final btnPause = dom.querySelector("#pause") as dom.ButtonElement;
    final fpsElement = dom.querySelector("#fps") as dom.SpanElement;

    btnBroadcast.onClick.listen((_) {
        if (ws.readyState == dom.WebSocket.OPEN) {
            final String message = (dom.querySelector("#message") as dom.InputElement).value;
            if (message.isNotEmpty) {
                ws.send(JSON.encode({
                    "event": "msg",
                    "data": {"msg": message}
                }));
            }
        }
    });

    btnPlay.onClick.listen((_) {
        if (ws.readyState == dom.WebSocket.OPEN) {
            pauseState = false;
            ws.send(JSON.encode({"event": "pull-image"}));
        }
        fps.start();
    });

    btnPause.onClick.listen((_) {
        if (ws.readyState == dom.WebSocket.OPEN) {
            pauseState = true;
        }
    });

    new Timer.periodic(new Duration(seconds: 1), (_) {
        fpsElement.text = fps.fps.toString();
        fps.reset();
    });

}
