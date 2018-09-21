/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
import * as errors from './errors.js';
import { Promise, TPromise } from './winjs.base.js';
import { CancellationTokenSource } from './cancellation.js';
import { Disposable } from './lifecycle.js';
import { Emitter } from './event.js';
export function isPromiseLike(obj) {
    return obj && typeof obj.then === 'function';
}
export function toPromiseLike(arg) {
    if (isPromiseLike(arg)) {
        return arg;
    }
    else {
        return TPromise.as(arg);
    }
}
export function asWinJsPromise(callback) {
    var source = new CancellationTokenSource();
    return new TPromise(function (resolve, reject, progress) {
        var item = callback(source.token);
        if (item instanceof TPromise) {
            item.then(resolve, reject, progress);
        }
        else if (isPromiseLike(item)) {
            item.then(resolve, reject);
        }
        else {
            resolve(item);
        }
    }, function () {
        source.cancel();
    });
}
/**
 * Hook a cancellation token to a WinJS Promise
 */
export function wireCancellationToken(token, promise, resolveAsUndefinedWhenCancelled) {
    var subscription = token.onCancellationRequested(function () { return promise.cancel(); });
    if (resolveAsUndefinedWhenCancelled) {
        promise = promise.then(undefined, function (err) {
            if (!errors.isPromiseCanceledError(err)) {
                return TPromise.wrapError(err);
            }
            return undefined;
        });
    }
    return always(promise, function () { return subscription.dispose(); });
}
/**
 * A helper to prevent accumulation of sequential async tasks.
 *
 * Imagine a mail man with the sole task of delivering letters. As soon as
 * a letter submitted for delivery, he drives to the destination, delivers it
 * and returns to his base. Imagine that during the trip, N more letters were submitted.
 * When the mail man returns, he picks those N letters and delivers them all in a
 * single trip. Even though N+1 submissions occurred, only 2 deliveries were made.
 *
 * The throttler implements this via the queue() method, by providing it a task
 * factory. Following the example:
 *
 * 		const throttler = new Throttler();
 * 		const letters = [];
 *
 * 		function deliver() {
 * 			const lettersToDeliver = letters;
 * 			letters = [];
 * 			return makeTheTrip(lettersToDeliver);
 * 		}
 *
 * 		function onLetterReceived(l) {
 * 			letters.push(l);
 * 			throttler.queue(deliver);
 * 		}
 */
var Throttler = /** @class */ (function () {
    function Throttler() {
        this.activePromise = null;
        this.queuedPromise = null;
        this.queuedPromiseFactory = null;
    }
    Throttler.prototype.queue = function (promiseFactory) {
        var _this = this;
        if (this.activePromise) {
            this.queuedPromiseFactory = promiseFactory;
            if (!this.queuedPromise) {
                var onComplete_1 = function () {
                    _this.queuedPromise = null;
                    var result = _this.queue(_this.queuedPromiseFactory);
                    _this.queuedPromiseFactory = null;
                    return result;
                };
                this.queuedPromise = new TPromise(function (c, e, p) {
                    _this.activePromise.then(onComplete_1, onComplete_1, p).done(c);
                }, function () {
                    _this.activePromise.cancel();
                });
            }
            return new TPromise(function (c, e, p) {
                _this.queuedPromise.then(c, e, p);
            }, function () {
                // no-op
            });
        }
        this.activePromise = promiseFactory();
        return new TPromise(function (c, e, p) {
            _this.activePromise.done(function (result) {
                _this.activePromise = null;
                c(result);
            }, function (err) {
                _this.activePromise = null;
                e(err);
            }, p);
        }, function () {
            _this.activePromise.cancel();
        });
    };
    return Throttler;
}());
export { Throttler };
// TODO@Joao: can the previous throttler be replaced with this?
var SimpleThrottler = /** @class */ (function () {
    function SimpleThrottler() {
        this.current = TPromise.wrap(null);
    }
    SimpleThrottler.prototype.queue = function (promiseTask) {
        return this.current = this.current.then(function () { return promiseTask(); });
    };
    return SimpleThrottler;
}());
export { SimpleThrottler };
/**
 * A helper to delay execution of a task that is being requested often.
 *
 * Following the throttler, now imagine the mail man wants to optimize the number of
 * trips proactively. The trip itself can be long, so the he decides not to make the trip
 * as soon as a letter is submitted. Instead he waits a while, in case more
 * letters are submitted. After said waiting period, if no letters were submitted, he
 * decides to make the trip. Imagine that N more letters were submitted after the first
 * one, all within a short period of time between each other. Even though N+1
 * submissions occurred, only 1 delivery was made.
 *
 * The delayer offers this behavior via the trigger() method, into which both the task
 * to be executed and the waiting period (delay) must be passed in as arguments. Following
 * the example:
 *
 * 		const delayer = new Delayer(WAITING_PERIOD);
 * 		const letters = [];
 *
 * 		function letterReceived(l) {
 * 			letters.push(l);
 * 			delayer.trigger(() => { return makeTheTrip(); });
 * 		}
 */
var Delayer = /** @class */ (function () {
    function Delayer(defaultDelay) {
        this.defaultDelay = defaultDelay;
        this.timeout = null;
        this.completionPromise = null;
        this.onSuccess = null;
        this.task = null;
    }
    Delayer.prototype.trigger = function (task, delay) {
        var _this = this;
        if (delay === void 0) { delay = this.defaultDelay; }
        this.task = task;
        this.cancelTimeout();
        if (!this.completionPromise) {
            this.completionPromise = new TPromise(function (c) {
                _this.onSuccess = c;
            }, function () {
                // no-op
            }).then(function () {
                _this.completionPromise = null;
                _this.onSuccess = null;
                var task = _this.task;
                _this.task = null;
                return task();
            });
        }
        this.timeout = setTimeout(function () {
            _this.timeout = null;
            _this.onSuccess(null);
        }, delay);
        return this.completionPromise;
    };
    Delayer.prototype.isTriggered = function () {
        return this.timeout !== null;
    };
    Delayer.prototype.cancel = function () {
        this.cancelTimeout();
        if (this.completionPromise) {
            this.completionPromise.cancel();
            this.completionPromise = null;
        }
    };
    Delayer.prototype.cancelTimeout = function () {
        if (this.timeout !== null) {
            clearTimeout(this.timeout);
            this.timeout = null;
        }
    };
    return Delayer;
}());
export { Delayer };
/**
 * A helper to delay execution of a task that is being requested often, while
 * preventing accumulation of consecutive executions, while the task runs.
 *
 * Simply combine the two mail man strategies from the Throttler and Delayer
 * helpers, for an analogy.
 */
var ThrottledDelayer = /** @class */ (function (_super) {
    __extends(ThrottledDelayer, _super);
    function ThrottledDelayer(defaultDelay) {
        var _this = _super.call(this, defaultDelay) || this;
        _this.throttler = new Throttler();
        return _this;
    }
    ThrottledDelayer.prototype.trigger = function (promiseFactory, delay) {
        var _this = this;
        return _super.prototype.trigger.call(this, function () { return _this.throttler.queue(promiseFactory); }, delay);
    };
    return ThrottledDelayer;
}(Delayer));
export { ThrottledDelayer };
/**
 * A barrier that is initially closed and then becomes opened permanently.
 */
var Barrier = /** @class */ (function () {
    function Barrier() {
        var _this = this;
        this._isOpen = false;
        this._promise = new TPromise(function (c, e, p) {
            _this._completePromise = c;
        }, function () {
            console.warn('You should really not try to cancel this ready promise!');
        });
    }
    Barrier.prototype.isOpen = function () {
        return this._isOpen;
    };
    Barrier.prototype.open = function () {
        this._isOpen = true;
        this._completePromise(true);
    };
    Barrier.prototype.wait = function () {
        return this._promise;
    };
    return Barrier;
}());
export { Barrier };
var ShallowCancelThenPromise = /** @class */ (function (_super) {
    __extends(ShallowCancelThenPromise, _super);
    function ShallowCancelThenPromise(outer) {
        var _this = this;
        var completeCallback, errorCallback, progressCallback;
        _this = _super.call(this, function (c, e, p) {
            completeCallback = c;
            errorCallback = e;
            progressCallback = p;
        }, function () {
            // cancel this promise but not the
            // outer promise
            errorCallback(errors.canceled());
        }) || this;
        outer.then(completeCallback, errorCallback, progressCallback);
        return _this;
    }
    return ShallowCancelThenPromise;
}(TPromise));
export { ShallowCancelThenPromise };
/**
 * Replacement for `WinJS.Promise.timeout`.
 */
export function timeout(n) {
    return new Promise(function (resolve) { return setTimeout(resolve, n); });
}
/**
 * Returns a new promise that joins the provided promise. Upon completion of
 * the provided promise the provided function will always be called. This
 * method is comparable to a try-finally code block.
 * @param promise a promise
 * @param f a function that will be call in the success and error case.
 */
export function always(promise, f) {
    return new TPromise(function (c, e, p) {
        promise.done(function (result) {
            try {
                f(result);
            }
            catch (e1) {
                errors.onUnexpectedError(e1);
            }
            c(result);
        }, function (err) {
            try {
                f(err);
            }
            catch (e1) {
                errors.onUnexpectedError(e1);
            }
            e(err);
        }, function (progress) {
            p(progress);
        });
    }, function () {
        promise.cancel();
    });
}
/**
 * Runs the provided list of promise factories in sequential order. The returned
 * promise will complete to an array of results from each promise.
 */
export function sequence(promiseFactories) {
    var results = [];
    // reverse since we start with last element using pop()
    promiseFactories = promiseFactories.reverse();
    function next() {
        if (promiseFactories.length) {
            return promiseFactories.pop()();
        }
        return null;
    }
    function thenHandler(result) {
        if (result !== undefined && result !== null) {
            results.push(result);
        }
        var n = next();
        if (n) {
            return n.then(thenHandler);
        }
        return TPromise.as(results);
    }
    return TPromise.as(null).then(thenHandler);
}
export function first(promiseFactories, shouldStop) {
    if (shouldStop === void 0) { shouldStop = function (t) { return !!t; }; }
    promiseFactories = promiseFactories.reverse().slice();
    var loop = function () {
        if (promiseFactories.length === 0) {
            return TPromise.as(null);
        }
        var factory = promiseFactories.pop();
        var promise = factory();
        return promise.then(function (result) {
            if (shouldStop(result)) {
                return TPromise.as(result);
            }
            return loop();
        });
    };
    return loop();
}
/**
 * A helper to queue N promises and run them all with a max degree of parallelism. The helper
 * ensures that at any time no more than M promises are running at the same time.
 */
var Limiter = /** @class */ (function () {
    function Limiter(maxDegreeOfParalellism) {
        this.maxDegreeOfParalellism = maxDegreeOfParalellism;
        this.outstandingPromises = [];
        this.runningPromises = 0;
        this._onFinished = new Emitter();
    }
    Object.defineProperty(Limiter.prototype, "onFinished", {
        get: function () {
            return this._onFinished.event;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Limiter.prototype, "size", {
        get: function () {
            return this.runningPromises + this.outstandingPromises.length;
        },
        enumerable: true,
        configurable: true
    });
    Limiter.prototype.queue = function (promiseFactory) {
        var _this = this;
        return new TPromise(function (c, e, p) {
            _this.outstandingPromises.push({
                factory: promiseFactory,
                c: c,
                e: e,
                p: p
            });
            _this.consume();
        });
    };
    Limiter.prototype.consume = function () {
        var _this = this;
        while (this.outstandingPromises.length && this.runningPromises < this.maxDegreeOfParalellism) {
            var iLimitedTask = this.outstandingPromises.shift();
            this.runningPromises++;
            var promise = iLimitedTask.factory();
            promise.done(iLimitedTask.c, iLimitedTask.e, iLimitedTask.p);
            promise.done(function () { return _this.consumed(); }, function () { return _this.consumed(); });
        }
    };
    Limiter.prototype.consumed = function () {
        this.runningPromises--;
        if (this.outstandingPromises.length > 0) {
            this.consume();
        }
        else {
            this._onFinished.fire();
        }
    };
    Limiter.prototype.dispose = function () {
        this._onFinished.dispose();
    };
    return Limiter;
}());
export { Limiter };
/**
 * A queue is handles one promise at a time and guarantees that at any time only one promise is executing.
 */
var Queue = /** @class */ (function (_super) {
    __extends(Queue, _super);
    function Queue() {
        return _super.call(this, 1) || this;
    }
    return Queue;
}(Limiter));
export { Queue };
/**
 * A helper to organize queues per resource. The ResourceQueue makes sure to manage queues per resource
 * by disposing them once the queue is empty.
 */
var ResourceQueue = /** @class */ (function () {
    function ResourceQueue() {
        this.queues = Object.create(null);
    }
    ResourceQueue.prototype.queueFor = function (resource) {
        var _this = this;
        var key = resource.toString();
        if (!this.queues[key]) {
            var queue_1 = new Queue();
            queue_1.onFinished(function () {
                queue_1.dispose();
                delete _this.queues[key];
            });
            this.queues[key] = queue_1;
        }
        return this.queues[key];
    };
    return ResourceQueue;
}());
export { ResourceQueue };
export function setDisposableTimeout(handler, timeout) {
    var args = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        args[_i - 2] = arguments[_i];
    }
    var handle = setTimeout.apply(void 0, [handler, timeout].concat(args));
    return { dispose: function () { clearTimeout(handle); } };
}
var TimeoutTimer = /** @class */ (function (_super) {
    __extends(TimeoutTimer, _super);
    function TimeoutTimer() {
        var _this = _super.call(this) || this;
        _this._token = -1;
        return _this;
    }
    TimeoutTimer.prototype.dispose = function () {
        this.cancel();
        _super.prototype.dispose.call(this);
    };
    TimeoutTimer.prototype.cancel = function () {
        if (this._token !== -1) {
            clearTimeout(this._token);
            this._token = -1;
        }
    };
    TimeoutTimer.prototype.cancelAndSet = function (runner, timeout) {
        var _this = this;
        this.cancel();
        this._token = setTimeout(function () {
            _this._token = -1;
            runner();
        }, timeout);
    };
    TimeoutTimer.prototype.setIfNotSet = function (runner, timeout) {
        var _this = this;
        if (this._token !== -1) {
            // timer is already set
            return;
        }
        this._token = setTimeout(function () {
            _this._token = -1;
            runner();
        }, timeout);
    };
    return TimeoutTimer;
}(Disposable));
export { TimeoutTimer };
var IntervalTimer = /** @class */ (function (_super) {
    __extends(IntervalTimer, _super);
    function IntervalTimer() {
        var _this = _super.call(this) || this;
        _this._token = -1;
        return _this;
    }
    IntervalTimer.prototype.dispose = function () {
        this.cancel();
        _super.prototype.dispose.call(this);
    };
    IntervalTimer.prototype.cancel = function () {
        if (this._token !== -1) {
            clearInterval(this._token);
            this._token = -1;
        }
    };
    IntervalTimer.prototype.cancelAndSet = function (runner, interval) {
        this.cancel();
        this._token = setInterval(function () {
            runner();
        }, interval);
    };
    return IntervalTimer;
}(Disposable));
export { IntervalTimer };
var RunOnceScheduler = /** @class */ (function () {
    function RunOnceScheduler(runner, timeout) {
        this.timeoutToken = -1;
        this.runner = runner;
        this.timeout = timeout;
        this.timeoutHandler = this.onTimeout.bind(this);
    }
    /**
     * Dispose RunOnceScheduler
     */
    RunOnceScheduler.prototype.dispose = function () {
        this.cancel();
        this.runner = null;
    };
    /**
     * Cancel current scheduled runner (if any).
     */
    RunOnceScheduler.prototype.cancel = function () {
        if (this.isScheduled()) {
            clearTimeout(this.timeoutToken);
            this.timeoutToken = -1;
        }
    };
    /**
     * Cancel previous runner (if any) & schedule a new runner.
     */
    RunOnceScheduler.prototype.schedule = function (delay) {
        if (delay === void 0) { delay = this.timeout; }
        this.cancel();
        this.timeoutToken = setTimeout(this.timeoutHandler, delay);
    };
    /**
     * Returns true if scheduled.
     */
    RunOnceScheduler.prototype.isScheduled = function () {
        return this.timeoutToken !== -1;
    };
    RunOnceScheduler.prototype.onTimeout = function () {
        this.timeoutToken = -1;
        if (this.runner) {
            this.runner();
        }
    };
    return RunOnceScheduler;
}());
export { RunOnceScheduler };
export function nfcall(fn) {
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        args[_i - 1] = arguments[_i];
    }
    return new TPromise(function (c, e) { return fn.apply(void 0, args.concat([function (err, result) { return err ? e(err) : c(result); }])); }, function () { return null; });
}
export function ninvoke(thisArg, fn) {
    var args = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        args[_i - 2] = arguments[_i];
    }
    return new TPromise(function (c, e) { return fn.call.apply(fn, [thisArg].concat(args, [function (err, result) { return err ? e(err) : c(result); }])); }, function () { return null; });
}
/**
 * An emitter that will ignore any events that occur during a specific code
 * execution triggered via throttle() until the promise has finished (either
 * successfully or with an error). Only after the promise has finished, the
 * last event that was fired during the operation will get emitted.
 *
 */
var ThrottledEmitter = /** @class */ (function (_super) {
    __extends(ThrottledEmitter, _super);
    function ThrottledEmitter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ThrottledEmitter.prototype.throttle = function (promise) {
        var _this = this;
        this.suspended = true;
        return always(promise, function () { return _this.resume(); });
    };
    ThrottledEmitter.prototype.fire = function (event) {
        if (this.suspended) {
            this.lastEvent = event;
            this.hasLastEvent = true;
            return;
        }
        return _super.prototype.fire.call(this, event);
    };
    ThrottledEmitter.prototype.resume = function () {
        this.suspended = false;
        if (this.hasLastEvent) {
            this.fire(this.lastEvent);
        }
        this.hasLastEvent = false;
        this.lastEvent = void 0;
    };
    return ThrottledEmitter;
}(Emitter));
export { ThrottledEmitter };
