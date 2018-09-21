/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { toDisposable, combinedDisposable, empty as EmptyDisposable } from './lifecycle.js';
import { TPromise } from './winjs.base.js';
import { once as onceFn } from './functional.js';
import { onUnexpectedError } from './errors.js';
import { LinkedList } from './linkedList.js';
var Event;
(function (Event) {
    var _disposable = { dispose: function () { } };
    Event.None = function () { return _disposable; };
})(Event || (Event = {}));
export default Event;
/**
 * The Emitter can be used to expose an Event to the public
 * to fire it from the insides.
 * Sample:
    class Document {

        private _onDidChange = new Emitter<(value:string)=>any>();

        public onDidChange = this._onDidChange.event;

        // getter-style
        // get onDidChange(): Event<(value:string)=>any> {
        // 	return this._onDidChange.event;
        // }

        private _doIt() {
            //...
            this._onDidChange.fire(value);
        }
    }
 */
var Emitter = /** @class */ (function () {
    function Emitter(_options) {
        this._options = _options;
    }
    Object.defineProperty(Emitter.prototype, "event", {
        /**
         * For the public to allow to subscribe
         * to events from this Emitter
         */
        get: function () {
            var _this = this;
            if (!this._event) {
                this._event = function (listener, thisArgs, disposables) {
                    if (!_this._listeners) {
                        _this._listeners = new LinkedList();
                    }
                    var firstListener = _this._listeners.isEmpty();
                    if (firstListener && _this._options && _this._options.onFirstListenerAdd) {
                        _this._options.onFirstListenerAdd(_this);
                    }
                    var remove = _this._listeners.push(!thisArgs ? listener : [listener, thisArgs]);
                    if (firstListener && _this._options && _this._options.onFirstListenerDidAdd) {
                        _this._options.onFirstListenerDidAdd(_this);
                    }
                    if (_this._options && _this._options.onListenerDidAdd) {
                        _this._options.onListenerDidAdd(_this, listener, thisArgs);
                    }
                    var result;
                    result = {
                        dispose: function () {
                            result.dispose = Emitter._noop;
                            if (!_this._disposed) {
                                remove();
                                if (_this._options && _this._options.onLastListenerRemove && _this._listeners.isEmpty()) {
                                    _this._options.onLastListenerRemove(_this);
                                }
                            }
                        }
                    };
                    if (Array.isArray(disposables)) {
                        disposables.push(result);
                    }
                    return result;
                };
            }
            return this._event;
        },
        enumerable: true,
        configurable: true
    });
    /**
     * To be kept private to fire an event to
     * subscribers
     */
    Emitter.prototype.fire = function (event) {
        if (this._listeners) {
            // put all [listener,event]-pairs into delivery queue
            // then emit all event. an inner/nested event might be
            // the driver of this
            if (!this._deliveryQueue) {
                this._deliveryQueue = [];
            }
            for (var iter = this._listeners.iterator(), e = iter.next(); !e.done; e = iter.next()) {
                this._deliveryQueue.push([e.value, event]);
            }
            while (this._deliveryQueue.length > 0) {
                var _a = this._deliveryQueue.shift(), listener = _a[0], event_1 = _a[1];
                try {
                    if (typeof listener === 'function') {
                        listener.call(undefined, event_1);
                    }
                    else {
                        listener[0].call(listener[1], event_1);
                    }
                }
                catch (e) {
                    onUnexpectedError(e);
                }
            }
        }
    };
    Emitter.prototype.dispose = function () {
        if (this._listeners) {
            this._listeners = undefined;
        }
        if (this._deliveryQueue) {
            this._deliveryQueue.length = 0;
        }
        this._disposed = true;
    };
    Emitter._noop = function () { };
    return Emitter;
}());
export { Emitter };
var EventMultiplexer = /** @class */ (function () {
    function EventMultiplexer() {
        var _this = this;
        this.hasListeners = false;
        this.events = [];
        this.emitter = new Emitter({
            onFirstListenerAdd: function () { return _this.onFirstListenerAdd(); },
            onLastListenerRemove: function () { return _this.onLastListenerRemove(); }
        });
    }
    Object.defineProperty(EventMultiplexer.prototype, "event", {
        get: function () {
            return this.emitter.event;
        },
        enumerable: true,
        configurable: true
    });
    EventMultiplexer.prototype.add = function (event) {
        var _this = this;
        var e = { event: event, listener: null };
        this.events.push(e);
        if (this.hasListeners) {
            this.hook(e);
        }
        var dispose = function () {
            if (_this.hasListeners) {
                _this.unhook(e);
            }
            var idx = _this.events.indexOf(e);
            _this.events.splice(idx, 1);
        };
        return toDisposable(onceFn(dispose));
    };
    EventMultiplexer.prototype.onFirstListenerAdd = function () {
        var _this = this;
        this.hasListeners = true;
        this.events.forEach(function (e) { return _this.hook(e); });
    };
    EventMultiplexer.prototype.onLastListenerRemove = function () {
        var _this = this;
        this.hasListeners = false;
        this.events.forEach(function (e) { return _this.unhook(e); });
    };
    EventMultiplexer.prototype.hook = function (e) {
        var _this = this;
        e.listener = e.event(function (r) { return _this.emitter.fire(r); });
    };
    EventMultiplexer.prototype.unhook = function (e) {
        e.listener.dispose();
        e.listener = null;
    };
    EventMultiplexer.prototype.dispose = function () {
        this.emitter.dispose();
    };
    return EventMultiplexer;
}());
export { EventMultiplexer };
export function fromCallback(fn) {
    var listener;
    var emitter = new Emitter({
        onFirstListenerAdd: function () { return listener = fn(function (e) { return emitter.fire(e); }); },
        onLastListenerRemove: function () { return listener.dispose(); }
    });
    return emitter.event;
}
export function fromPromise(promise) {
    var emitter = new Emitter();
    var shouldEmit = false;
    promise
        .then(null, function () { return null; })
        .then(function () {
        if (!shouldEmit) {
            setTimeout(function () { return emitter.fire(); }, 0);
        }
        else {
            emitter.fire();
        }
    });
    shouldEmit = true;
    return emitter.event;
}
export function toPromise(event) {
    return new TPromise(function (complete) {
        var sub = event(function (e) {
            sub.dispose();
            complete(e);
        });
    });
}
export function once(event) {
    return function (listener, thisArgs, disposables) {
        if (thisArgs === void 0) { thisArgs = null; }
        var result = event(function (e) {
            result.dispose();
            return listener.call(thisArgs, e);
        }, null, disposables);
        return result;
    };
}
export function anyEvent() {
    var events = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        events[_i] = arguments[_i];
    }
    return function (listener, thisArgs, disposables) {
        if (thisArgs === void 0) { thisArgs = null; }
        return combinedDisposable(events.map(function (event) { return event(function (e) { return listener.call(thisArgs, e); }, null, disposables); }));
    };
}
export function debounceEvent(event, merger, delay, leading) {
    if (delay === void 0) { delay = 100; }
    if (leading === void 0) { leading = false; }
    var subscription;
    var output = undefined;
    var handle = undefined;
    var numDebouncedCalls = 0;
    var emitter = new Emitter({
        onFirstListenerAdd: function () {
            subscription = event(function (cur) {
                numDebouncedCalls++;
                output = merger(output, cur);
                if (leading && !handle) {
                    emitter.fire(output);
                }
                clearTimeout(handle);
                handle = setTimeout(function () {
                    var _output = output;
                    output = undefined;
                    handle = undefined;
                    if (!leading || numDebouncedCalls > 1) {
                        emitter.fire(_output);
                    }
                    numDebouncedCalls = 0;
                }, delay);
            });
        },
        onLastListenerRemove: function () {
            subscription.dispose();
        }
    });
    return emitter.event;
}
/**
 * The EventDelayer is useful in situations in which you want
 * to delay firing your events during some code.
 * You can wrap that code and be sure that the event will not
 * be fired during that wrap.
 *
 * ```
 * const emitter: Emitter;
 * const delayer = new EventDelayer();
 * const delayedEvent = delayer.wrapEvent(emitter.event);
 *
 * delayedEvent(console.log);
 *
 * delayer.bufferEvents(() => {
 *   emitter.fire(); // event will not be fired yet
 * });
 *
 * // event will only be fired at this point
 * ```
 */
var EventBufferer = /** @class */ (function () {
    function EventBufferer() {
        this.buffers = [];
    }
    EventBufferer.prototype.wrapEvent = function (event) {
        var _this = this;
        return function (listener, thisArgs, disposables) {
            return event(function (i) {
                var buffer = _this.buffers[_this.buffers.length - 1];
                if (buffer) {
                    buffer.push(function () { return listener.call(thisArgs, i); });
                }
                else {
                    listener.call(thisArgs, i);
                }
            }, void 0, disposables);
        };
    };
    EventBufferer.prototype.bufferEvents = function (fn) {
        var buffer = [];
        this.buffers.push(buffer);
        fn();
        this.buffers.pop();
        buffer.forEach(function (flush) { return flush(); });
    };
    return EventBufferer;
}());
export { EventBufferer };
export function mapEvent(event, map) {
    return function (listener, thisArgs, disposables) {
        if (thisArgs === void 0) { thisArgs = null; }
        return event(function (i) { return listener.call(thisArgs, map(i)); }, null, disposables);
    };
}
export function forEach(event, each) {
    return function (listener, thisArgs, disposables) {
        if (thisArgs === void 0) { thisArgs = null; }
        return event(function (i) { each(i); listener.call(thisArgs, i); }, null, disposables);
    };
}
export function filterEvent(event, filter) {
    return function (listener, thisArgs, disposables) {
        if (thisArgs === void 0) { thisArgs = null; }
        return event(function (e) { return filter(e) && listener.call(thisArgs, e); }, null, disposables);
    };
}
var ChainableEvent = /** @class */ (function () {
    function ChainableEvent(_event) {
        this._event = _event;
    }
    Object.defineProperty(ChainableEvent.prototype, "event", {
        get: function () { return this._event; },
        enumerable: true,
        configurable: true
    });
    ChainableEvent.prototype.map = function (fn) {
        return new ChainableEvent(mapEvent(this._event, fn));
    };
    ChainableEvent.prototype.forEach = function (fn) {
        return new ChainableEvent(forEach(this._event, fn));
    };
    ChainableEvent.prototype.filter = function (fn) {
        return new ChainableEvent(filterEvent(this._event, fn));
    };
    ChainableEvent.prototype.on = function (listener, thisArgs, disposables) {
        return this._event(listener, thisArgs, disposables);
    };
    return ChainableEvent;
}());
export function chain(event) {
    return new ChainableEvent(event);
}
export function stopwatch(event) {
    var start = new Date().getTime();
    return mapEvent(once(event), function (_) { return new Date().getTime() - start; });
}
/**
 * Buffers the provided event until a first listener comes
 * along, at which point fire all the events at once and
 * pipe the event from then on.
 *
 * ```typescript
 * const emitter = new Emitter<number>();
 * const event = emitter.event;
 * const bufferedEvent = buffer(event);
 *
 * emitter.fire(1);
 * emitter.fire(2);
 * emitter.fire(3);
 * // nothing...
 *
 * const listener = bufferedEvent(num => console.log(num));
 * // 1, 2, 3
 *
 * emitter.fire(4);
 * // 4
 * ```
 */
export function buffer(event, nextTick, buffer) {
    if (nextTick === void 0) { nextTick = false; }
    if (buffer === void 0) { buffer = []; }
    buffer = buffer.slice();
    var listener = event(function (e) {
        if (buffer) {
            buffer.push(e);
        }
        else {
            emitter.fire(e);
        }
    });
    var flush = function () {
        buffer.forEach(function (e) { return emitter.fire(e); });
        buffer = null;
    };
    var emitter = new Emitter({
        onFirstListenerAdd: function () {
            if (!listener) {
                listener = event(function (e) { return emitter.fire(e); });
            }
        },
        onFirstListenerDidAdd: function () {
            if (buffer) {
                if (nextTick) {
                    setTimeout(flush);
                }
                else {
                    flush();
                }
            }
        },
        onLastListenerRemove: function () {
            listener.dispose();
            listener = null;
        }
    });
    return emitter.event;
}
/**
 * Similar to `buffer` but it buffers indefinitely and repeats
 * the buffered events to every new listener.
 */
export function echo(event, nextTick, buffer) {
    if (nextTick === void 0) { nextTick = false; }
    if (buffer === void 0) { buffer = []; }
    buffer = buffer.slice();
    event(function (e) {
        buffer.push(e);
        emitter.fire(e);
    });
    var flush = function (listener, thisArgs) { return buffer.forEach(function (e) { return listener.call(thisArgs, e); }); };
    var emitter = new Emitter({
        onListenerDidAdd: function (emitter, listener, thisArgs) {
            if (nextTick) {
                setTimeout(function () { return flush(listener, thisArgs); });
            }
            else {
                flush(listener, thisArgs);
            }
        }
    });
    return emitter.event;
}
var Relay = /** @class */ (function () {
    function Relay() {
        this.emitter = new Emitter();
        this.event = this.emitter.event;
        this.disposable = EmptyDisposable;
    }
    Object.defineProperty(Relay.prototype, "input", {
        set: function (event) {
            this.disposable.dispose();
            this.disposable = event(this.emitter.fire, this.emitter);
        },
        enumerable: true,
        configurable: true
    });
    Relay.prototype.dispose = function () {
        this.disposable.dispose();
        this.emitter.dispose();
    };
    return Relay;
}());
export { Relay };
export function fromNodeEventEmitter(emitter, eventName, map) {
    if (map === void 0) { map = function (id) { return id; }; }
    var fn = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        return result.fire(map.apply(void 0, args));
    };
    var onFirstListenerAdd = function () { return emitter.on(eventName, fn); };
    var onLastListenerRemove = function () { return emitter.removeListener(eventName, fn); };
    var result = new Emitter({ onFirstListenerAdd: onFirstListenerAdd, onLastListenerRemove: onLastListenerRemove });
    return result.event;
}
