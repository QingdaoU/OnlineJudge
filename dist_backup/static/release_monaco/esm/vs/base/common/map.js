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
import URI from './uri.js';
export function values(forEachable) {
    var result = [];
    forEachable.forEach(function (value) { return result.push(value); });
    return result;
}
export function keys(map) {
    var result = [];
    map.forEach(function (value, key) { return result.push(key); });
    return result;
}
export function getOrSet(map, key, value) {
    var result = map.get(key);
    if (result === void 0) {
        result = value;
        map.set(key, result);
    }
    return result;
}
var StringIterator = /** @class */ (function () {
    function StringIterator() {
        this._value = '';
        this._pos = 0;
    }
    StringIterator.prototype.reset = function (key) {
        this._value = key;
        this._pos = 0;
        return this;
    };
    StringIterator.prototype.next = function () {
        this._pos += 1;
        return this;
    };
    StringIterator.prototype.join = function (parts) {
        return parts.join('');
    };
    StringIterator.prototype.hasNext = function () {
        return this._pos < this._value.length - 1;
    };
    StringIterator.prototype.cmp = function (a) {
        var aCode = a.charCodeAt(0);
        var thisCode = this._value.charCodeAt(this._pos);
        return aCode - thisCode;
    };
    StringIterator.prototype.value = function () {
        return this._value[this._pos];
    };
    return StringIterator;
}());
export { StringIterator };
var PathIterator = /** @class */ (function () {
    function PathIterator() {
    }
    PathIterator.prototype.reset = function (key) {
        this._value = key.replace(/\\$|\/$/, '');
        this._from = 0;
        this._to = 0;
        return this.next();
    };
    PathIterator.prototype.hasNext = function () {
        return this._to < this._value.length;
    };
    PathIterator.prototype.join = function (parts) {
        return parts.join('/');
    };
    PathIterator.prototype.next = function () {
        // this._data = key.split(/[\\/]/).filter(s => !!s);
        this._from = this._to;
        var justSeps = true;
        for (; this._to < this._value.length; this._to++) {
            var ch = this._value.charCodeAt(this._to);
            if (ch === PathIterator._fwd || ch === PathIterator._bwd) {
                if (justSeps) {
                    this._from++;
                }
                else {
                    break;
                }
            }
            else {
                justSeps = false;
            }
        }
        return this;
    };
    PathIterator.prototype.cmp = function (a) {
        var aPos = 0;
        var aLen = a.length;
        var thisPos = this._from;
        while (aPos < aLen && thisPos < this._to) {
            var cmp = a.charCodeAt(aPos) - this._value.charCodeAt(thisPos);
            if (cmp !== 0) {
                return cmp;
            }
            aPos += 1;
            thisPos += 1;
        }
        if (aLen === this._to - this._from) {
            return 0;
        }
        else if (aPos < aLen) {
            return -1;
        }
        else {
            return 1;
        }
    };
    PathIterator.prototype.value = function () {
        return this._value.substring(this._from, this._to);
    };
    PathIterator._fwd = '/'.charCodeAt(0);
    PathIterator._bwd = '\\'.charCodeAt(0);
    return PathIterator;
}());
export { PathIterator };
var TernarySearchTreeNode = /** @class */ (function () {
    function TernarySearchTreeNode() {
    }
    TernarySearchTreeNode.prototype.isEmpty = function () {
        return !this.left && !this.mid && !this.right && !this.element;
    };
    return TernarySearchTreeNode;
}());
var TernarySearchTree = /** @class */ (function () {
    function TernarySearchTree(segments) {
        this._iter = segments;
    }
    TernarySearchTree.forPaths = function () {
        return new TernarySearchTree(new PathIterator());
    };
    TernarySearchTree.forStrings = function () {
        return new TernarySearchTree(new StringIterator());
    };
    TernarySearchTree.prototype.clear = function () {
        this._root = undefined;
    };
    TernarySearchTree.prototype.set = function (key, element) {
        var iter = this._iter.reset(key);
        var node;
        if (!this._root) {
            this._root = new TernarySearchTreeNode();
            this._root.str = iter.value();
        }
        node = this._root;
        while (true) {
            var val = iter.cmp(node.str);
            if (val > 0) {
                // left
                if (!node.left) {
                    node.left = new TernarySearchTreeNode();
                    node.left.str = iter.value();
                }
                node = node.left;
            }
            else if (val < 0) {
                // right
                if (!node.right) {
                    node.right = new TernarySearchTreeNode();
                    node.right.str = iter.value();
                }
                node = node.right;
            }
            else if (iter.hasNext()) {
                // mid
                iter.next();
                if (!node.mid) {
                    node.mid = new TernarySearchTreeNode();
                    node.mid.str = iter.value();
                }
                node = node.mid;
            }
            else {
                break;
            }
        }
        var oldElement = node.element;
        node.element = element;
        return oldElement;
    };
    TernarySearchTree.prototype.get = function (key) {
        var iter = this._iter.reset(key);
        var node = this._root;
        while (node) {
            var val = iter.cmp(node.str);
            if (val > 0) {
                // left
                node = node.left;
            }
            else if (val < 0) {
                // right
                node = node.right;
            }
            else if (iter.hasNext()) {
                // mid
                iter.next();
                node = node.mid;
            }
            else {
                break;
            }
        }
        return node ? node.element : undefined;
    };
    TernarySearchTree.prototype.delete = function (key) {
        var iter = this._iter.reset(key);
        var stack = [];
        var node = this._root;
        // find and unset node
        while (node) {
            var val = iter.cmp(node.str);
            if (val > 0) {
                // left
                stack.push([1, node]);
                node = node.left;
            }
            else if (val < 0) {
                // right
                stack.push([-1, node]);
                node = node.right;
            }
            else if (iter.hasNext()) {
                // mid
                iter.next();
                stack.push([0, node]);
                node = node.mid;
            }
            else {
                // remove element
                node.element = undefined;
                // clean up empty nodes
                while (stack.length > 0 && node.isEmpty()) {
                    var _a = stack.pop(), dir = _a[0], parent_1 = _a[1];
                    switch (dir) {
                        case 1:
                            parent_1.left = undefined;
                            break;
                        case 0:
                            parent_1.mid = undefined;
                            break;
                        case -1:
                            parent_1.right = undefined;
                            break;
                    }
                    node = parent_1;
                }
                break;
            }
        }
    };
    TernarySearchTree.prototype.findSubstr = function (key) {
        var iter = this._iter.reset(key);
        var node = this._root;
        var candidate;
        while (node) {
            var val = iter.cmp(node.str);
            if (val > 0) {
                // left
                node = node.left;
            }
            else if (val < 0) {
                // right
                node = node.right;
            }
            else if (iter.hasNext()) {
                // mid
                iter.next();
                candidate = node.element || candidate;
                node = node.mid;
            }
            else {
                break;
            }
        }
        return node && node.element || candidate;
    };
    TernarySearchTree.prototype.findSuperstr = function (key) {
        var iter = this._iter.reset(key);
        var node = this._root;
        while (node) {
            var val = iter.cmp(node.str);
            if (val > 0) {
                // left
                node = node.left;
            }
            else if (val < 0) {
                // right
                node = node.right;
            }
            else if (iter.hasNext()) {
                // mid
                iter.next();
                node = node.mid;
            }
            else {
                // collect
                if (!node.mid) {
                    return undefined;
                }
                var ret = new TernarySearchTree(this._iter);
                ret._root = node.mid;
                return ret;
            }
        }
        return undefined;
    };
    TernarySearchTree.prototype.forEach = function (callback) {
        this._forEach(this._root, [], callback);
    };
    TernarySearchTree.prototype._forEach = function (node, parts, callback) {
        if (node) {
            // left
            this._forEach(node.left, parts, callback);
            // node
            parts.push(node.str);
            if (node.element) {
                callback(node.element, this._iter.join(parts));
            }
            // mid
            this._forEach(node.mid, parts, callback);
            parts.pop();
            // right
            this._forEach(node.right, parts, callback);
        }
    };
    return TernarySearchTree;
}());
export { TernarySearchTree };
var ResourceMap = /** @class */ (function () {
    function ResourceMap(ignoreCase) {
        this.ignoreCase = ignoreCase;
        this.map = new Map();
    }
    ResourceMap.prototype.set = function (resource, value) {
        this.map.set(this.toKey(resource), value);
    };
    ResourceMap.prototype.get = function (resource) {
        return this.map.get(this.toKey(resource));
    };
    ResourceMap.prototype.has = function (resource) {
        return this.map.has(this.toKey(resource));
    };
    Object.defineProperty(ResourceMap.prototype, "size", {
        get: function () {
            return this.map.size;
        },
        enumerable: true,
        configurable: true
    });
    ResourceMap.prototype.clear = function () {
        this.map.clear();
    };
    ResourceMap.prototype.delete = function (resource) {
        return this.map.delete(this.toKey(resource));
    };
    ResourceMap.prototype.forEach = function (clb) {
        this.map.forEach(clb);
    };
    ResourceMap.prototype.values = function () {
        return values(this.map);
    };
    ResourceMap.prototype.toKey = function (resource) {
        var key = resource.toString();
        if (this.ignoreCase) {
            key = key.toLowerCase();
        }
        return key;
    };
    return ResourceMap;
}());
export { ResourceMap };
var StrictResourceMap = /** @class */ (function (_super) {
    __extends(StrictResourceMap, _super);
    function StrictResourceMap() {
        return _super.call(this) || this;
    }
    StrictResourceMap.prototype.keys = function () {
        return keys(this.map).map(function (key) { return URI.parse(key); });
    };
    return StrictResourceMap;
}(ResourceMap));
export { StrictResourceMap };
export var Touch;
(function (Touch) {
    Touch[Touch["None"] = 0] = "None";
    Touch[Touch["AsOld"] = 1] = "AsOld";
    Touch[Touch["AsNew"] = 2] = "AsNew";
})(Touch || (Touch = {}));
var LinkedMap = /** @class */ (function () {
    function LinkedMap() {
        this._map = new Map();
        this._head = undefined;
        this._tail = undefined;
        this._size = 0;
    }
    LinkedMap.prototype.clear = function () {
        this._map.clear();
        this._head = undefined;
        this._tail = undefined;
        this._size = 0;
    };
    LinkedMap.prototype.isEmpty = function () {
        return !this._head && !this._tail;
    };
    Object.defineProperty(LinkedMap.prototype, "size", {
        get: function () {
            return this._size;
        },
        enumerable: true,
        configurable: true
    });
    LinkedMap.prototype.has = function (key) {
        return this._map.has(key);
    };
    LinkedMap.prototype.get = function (key, touch) {
        if (touch === void 0) { touch = Touch.None; }
        var item = this._map.get(key);
        if (!item) {
            return undefined;
        }
        if (touch !== Touch.None) {
            this.touch(item, touch);
        }
        return item.value;
    };
    LinkedMap.prototype.set = function (key, value, touch) {
        if (touch === void 0) { touch = Touch.None; }
        var item = this._map.get(key);
        if (item) {
            item.value = value;
            if (touch !== Touch.None) {
                this.touch(item, touch);
            }
        }
        else {
            item = { key: key, value: value, next: undefined, previous: undefined };
            switch (touch) {
                case Touch.None:
                    this.addItemLast(item);
                    break;
                case Touch.AsOld:
                    this.addItemFirst(item);
                    break;
                case Touch.AsNew:
                    this.addItemLast(item);
                    break;
                default:
                    this.addItemLast(item);
                    break;
            }
            this._map.set(key, item);
            this._size++;
        }
    };
    LinkedMap.prototype.delete = function (key) {
        return !!this.remove(key);
    };
    LinkedMap.prototype.remove = function (key) {
        var item = this._map.get(key);
        if (!item) {
            return undefined;
        }
        this._map.delete(key);
        this.removeItem(item);
        this._size--;
        return item.value;
    };
    LinkedMap.prototype.shift = function () {
        if (!this._head && !this._tail) {
            return undefined;
        }
        if (!this._head || !this._tail) {
            throw new Error('Invalid list');
        }
        var item = this._head;
        this._map.delete(item.key);
        this.removeItem(item);
        this._size--;
        return item.value;
    };
    LinkedMap.prototype.forEach = function (callbackfn, thisArg) {
        var current = this._head;
        while (current) {
            if (thisArg) {
                callbackfn.bind(thisArg)(current.value, current.key, this);
            }
            else {
                callbackfn(current.value, current.key, this);
            }
            current = current.next;
        }
    };
    LinkedMap.prototype.values = function () {
        var result = [];
        var current = this._head;
        while (current) {
            result.push(current.value);
            current = current.next;
        }
        return result;
    };
    LinkedMap.prototype.keys = function () {
        var result = [];
        var current = this._head;
        while (current) {
            result.push(current.key);
            current = current.next;
        }
        return result;
    };
    /* VS Code / Monaco editor runs on es5 which has no Symbol.iterator
    public keys(): IterableIterator<K> {
        let current = this._head;
        let iterator: IterableIterator<K> = {
            [Symbol.iterator]() {
                return iterator;
            },
            next():IteratorResult<K> {
                if (current) {
                    let result = { value: current.key, done: false };
                    current = current.next;
                    return result;
                } else {
                    return { value: undefined, done: true };
                }
            }
        };
        return iterator;
    }

    public values(): IterableIterator<V> {
        let current = this._head;
        let iterator: IterableIterator<V> = {
            [Symbol.iterator]() {
                return iterator;
            },
            next():IteratorResult<V> {
                if (current) {
                    let result = { value: current.value, done: false };
                    current = current.next;
                    return result;
                } else {
                    return { value: undefined, done: true };
                }
            }
        };
        return iterator;
    }
    */
    LinkedMap.prototype.trimOld = function (newSize) {
        if (newSize >= this.size) {
            return;
        }
        if (newSize === 0) {
            this.clear();
            return;
        }
        var current = this._head;
        var currentSize = this.size;
        while (current && currentSize > newSize) {
            this._map.delete(current.key);
            current = current.next;
            currentSize--;
        }
        this._head = current;
        this._size = currentSize;
        current.previous = void 0;
    };
    LinkedMap.prototype.addItemFirst = function (item) {
        // First time Insert
        if (!this._head && !this._tail) {
            this._tail = item;
        }
        else if (!this._head) {
            throw new Error('Invalid list');
        }
        else {
            item.next = this._head;
            this._head.previous = item;
        }
        this._head = item;
    };
    LinkedMap.prototype.addItemLast = function (item) {
        // First time Insert
        if (!this._head && !this._tail) {
            this._head = item;
        }
        else if (!this._tail) {
            throw new Error('Invalid list');
        }
        else {
            item.previous = this._tail;
            this._tail.next = item;
        }
        this._tail = item;
    };
    LinkedMap.prototype.removeItem = function (item) {
        if (item === this._head && item === this._tail) {
            this._head = void 0;
            this._tail = void 0;
        }
        else if (item === this._head) {
            this._head = item.next;
        }
        else if (item === this._tail) {
            this._tail = item.previous;
        }
        else {
            var next = item.next;
            var previous = item.previous;
            if (!next || !previous) {
                throw new Error('Invalid list');
            }
            next.previous = previous;
            previous.next = next;
        }
    };
    LinkedMap.prototype.touch = function (item, touch) {
        if (!this._head || !this._tail) {
            throw new Error('Invalid list');
        }
        if ((touch !== Touch.AsOld && touch !== Touch.AsNew)) {
            return;
        }
        if (touch === Touch.AsOld) {
            if (item === this._head) {
                return;
            }
            var next = item.next;
            var previous = item.previous;
            // Unlink the item
            if (item === this._tail) {
                // previous must be defined since item was not head but is tail
                // So there are more than on item in the map
                previous.next = void 0;
                this._tail = previous;
            }
            else {
                // Both next and previous are not undefined since item was neither head nor tail.
                next.previous = previous;
                previous.next = next;
            }
            // Insert the node at head
            item.previous = void 0;
            item.next = this._head;
            this._head.previous = item;
            this._head = item;
        }
        else if (touch === Touch.AsNew) {
            if (item === this._tail) {
                return;
            }
            var next = item.next;
            var previous = item.previous;
            // Unlink the item.
            if (item === this._head) {
                // next must be defined since item was not tail but is head
                // So there are more than on item in the map
                next.previous = void 0;
                this._head = next;
            }
            else {
                // Both next and previous are not undefined since item was neither head nor tail.
                next.previous = previous;
                previous.next = next;
            }
            item.next = void 0;
            item.previous = this._tail;
            this._tail.next = item;
            this._tail = item;
        }
    };
    return LinkedMap;
}());
export { LinkedMap };
var LRUCache = /** @class */ (function (_super) {
    __extends(LRUCache, _super);
    function LRUCache(limit, ratio) {
        if (ratio === void 0) { ratio = 1; }
        var _this = _super.call(this) || this;
        _this._limit = limit;
        _this._ratio = Math.min(Math.max(0, ratio), 1);
        return _this;
    }
    Object.defineProperty(LRUCache.prototype, "limit", {
        get: function () {
            return this._limit;
        },
        set: function (limit) {
            this._limit = limit;
            this.checkTrim();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(LRUCache.prototype, "ratio", {
        get: function () {
            return this._ratio;
        },
        set: function (ratio) {
            this._ratio = Math.min(Math.max(0, ratio), 1);
            this.checkTrim();
        },
        enumerable: true,
        configurable: true
    });
    LRUCache.prototype.get = function (key) {
        return _super.prototype.get.call(this, key, Touch.AsNew);
    };
    LRUCache.prototype.peek = function (key) {
        return _super.prototype.get.call(this, key, Touch.None);
    };
    LRUCache.prototype.set = function (key, value) {
        _super.prototype.set.call(this, key, value, Touch.AsNew);
        this.checkTrim();
    };
    LRUCache.prototype.checkTrim = function () {
        if (this.size > this._limit) {
            this.trimOld(Math.round(this._limit * this._ratio));
        }
    };
    return LRUCache;
}(LinkedMap));
export { LRUCache };
