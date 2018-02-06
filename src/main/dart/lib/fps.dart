/*
 * Copyright (c) 2018, Michael Mitterer (office@mikemitterer.at),
 * IT-Consulting and Development Limited.
 * 
 * All Rights Reserved.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

library opencv.fps;

class FPS {
    DateTime _start = new DateTime.now();
    int _numFrames = 0;

    void start() {
        _start = new DateTime.now();
        _numFrames = 0;
    }

    void update() => _numFrames++;

    Duration get elapsed => (new DateTime.now()).difference(_start);

    int get fps => _numFrames;

    void reset() => _numFrames = 0;
}
