/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
var LeafOffsetLenEdit = /** @class */ (function () {
    function LeafOffsetLenEdit(start, length, text) {
        this.start = start;
        this.length = length;
        this.text = text;
    }
    return LeafOffsetLenEdit;
}());
export { LeafOffsetLenEdit };
var BufferPiece = /** @class */ (function () {
    function BufferPiece(str, lineStarts) {
        if (lineStarts === void 0) { lineStarts = null; }
        this._str = str;
        if (lineStarts === null) {
            this._lineStarts = createLineStartsFast(str);
        }
        else {
            this._lineStarts = lineStarts;
        }
    }
    Object.defineProperty(BufferPiece.prototype, "text", {
        get: function () { return this._str; },
        enumerable: true,
        configurable: true
    });
    BufferPiece.prototype.length = function () {
        return this._str.length;
    };
    BufferPiece.prototype.newLineCount = function () {
        return this._lineStarts.length;
    };
    BufferPiece.prototype.lineStartFor = function (relativeLineIndex) {
        return this._lineStarts[relativeLineIndex];
    };
    BufferPiece.prototype.charCodeAt = function (index) {
        return this._str.charCodeAt(index);
    };
    BufferPiece.prototype.substr = function (from, length) {
        return this._str.substr(from, length);
    };
    BufferPiece.prototype.findLineStartBeforeOffset = function (offset) {
        if (this._lineStarts.length === 0 || offset < this._lineStarts[0]) {
            return -1;
        }
        var low = 0, high = this._lineStarts.length - 1;
        while (low < high) {
            var mid = low + Math.ceil((high - low) / 2);
            var lineStart = this._lineStarts[mid];
            if (offset === lineStart) {
                return mid;
            }
            else if (offset < lineStart) {
                high = mid - 1;
            }
            else {
                low = mid;
            }
        }
        return low;
    };
    BufferPiece.prototype.findLineFirstNonWhitespaceIndex = function (searchStartOffset) {
        for (var i = searchStartOffset, len = this._str.length; i < len; i++) {
            var chCode = this._str.charCodeAt(i);
            if (chCode === 13 /* CarriageReturn */ || chCode === 10 /* LineFeed */) {
                // Reached EOL
                return -2;
            }
            if (chCode !== 32 /* Space */ && chCode !== 9 /* Tab */) {
                return i;
            }
        }
        return -1;
    };
    BufferPiece.prototype.findLineLastNonWhitespaceIndex = function (searchStartOffset) {
        for (var i = searchStartOffset - 1; i >= 0; i--) {
            var chCode = this._str.charCodeAt(i);
            if (chCode === 13 /* CarriageReturn */ || chCode === 10 /* LineFeed */) {
                // Reached EOL
                return -2;
            }
            if (chCode !== 32 /* Space */ && chCode !== 9 /* Tab */) {
                return i;
            }
        }
        return -1;
    };
    BufferPiece.normalizeEOL = function (target, eol) {
        return new BufferPiece(target._str.replace(/\r\n|\r|\n/g, eol));
    };
    BufferPiece.deleteLastChar = function (target) {
        var targetCharsLength = target.length();
        var targetLineStartsLength = target.newLineCount();
        var targetLineStarts = target._lineStarts;
        var newLineStartsLength;
        if (targetLineStartsLength > 0 && targetLineStarts[targetLineStartsLength - 1] === targetCharsLength) {
            newLineStartsLength = targetLineStartsLength - 1;
        }
        else {
            newLineStartsLength = targetLineStartsLength;
        }
        var newLineStarts = new Uint32Array(newLineStartsLength);
        newLineStarts.set(targetLineStarts);
        return new BufferPiece(target._str.substr(0, targetCharsLength - 1), newLineStarts);
    };
    BufferPiece.insertFirstChar = function (target, character) {
        var targetLineStartsLength = target.newLineCount();
        var targetLineStarts = target._lineStarts;
        var insertLineStart = ((character === 13 /* CarriageReturn */ && (targetLineStartsLength === 0 || targetLineStarts[0] !== 1 || target.charCodeAt(0) !== 10 /* LineFeed */)) || (character === 10 /* LineFeed */));
        var newLineStartsLength = (insertLineStart ? targetLineStartsLength + 1 : targetLineStartsLength);
        var newLineStarts = new Uint32Array(newLineStartsLength);
        if (insertLineStart) {
            newLineStarts[0] = 1;
            for (var i = 0; i < targetLineStartsLength; i++) {
                newLineStarts[i + 1] = targetLineStarts[i] + 1;
            }
        }
        else {
            for (var i = 0; i < targetLineStartsLength; i++) {
                newLineStarts[i] = targetLineStarts[i] + 1;
            }
        }
        return new BufferPiece(String.fromCharCode(character) + target._str, newLineStarts);
    };
    BufferPiece.join = function (first, second) {
        var firstCharsLength = first._str.length;
        var firstLineStartsLength = first._lineStarts.length;
        var secondLineStartsLength = second._lineStarts.length;
        var firstLineStarts = first._lineStarts;
        var secondLineStarts = second._lineStarts;
        var newLineStartsLength = firstLineStartsLength + secondLineStartsLength;
        var newLineStarts = new Uint32Array(newLineStartsLength);
        newLineStarts.set(firstLineStarts, 0);
        for (var i = 0; i < secondLineStartsLength; i++) {
            newLineStarts[i + firstLineStartsLength] = secondLineStarts[i] + firstCharsLength;
        }
        return new BufferPiece(first._str + second._str, newLineStarts);
    };
    BufferPiece.replaceOffsetLen = function (target, edits, idealLeafLength, maxLeafLength, result) {
        var editsSize = edits.length;
        var originalCharsLength = target.length();
        if (editsSize === 1 && edits[0].text.length === 0 && edits[0].start === 0 && edits[0].length === originalCharsLength) {
            // special case => deleting everything
            return;
        }
        var pieces = new Array(2 * editsSize + 1);
        var originalFromIndex = 0;
        var piecesTextLength = 0;
        for (var i = 0; i < editsSize; i++) {
            var edit = edits[i];
            var originalText = target._str.substr(originalFromIndex, edit.start - originalFromIndex);
            pieces[2 * i] = originalText;
            piecesTextLength += originalText.length;
            originalFromIndex = edit.start + edit.length;
            pieces[2 * i + 1] = edit.text;
            piecesTextLength += edit.text.length;
        }
        // maintain the chars that survive to the right of the last edit
        var text = target._str.substr(originalFromIndex, originalCharsLength - originalFromIndex);
        pieces[2 * editsSize] = text;
        piecesTextLength += text.length;
        var targetDataLength = piecesTextLength > maxLeafLength ? idealLeafLength : piecesTextLength;
        var targetDataOffset = 0;
        var data = '';
        for (var pieceIndex = 0, pieceCount = pieces.length; pieceIndex < pieceCount; pieceIndex++) {
            var pieceText = pieces[pieceIndex];
            var pieceLength = pieceText.length;
            if (pieceLength === 0) {
                continue;
            }
            var pieceOffset = 0;
            while (pieceOffset < pieceLength) {
                if (targetDataOffset >= targetDataLength) {
                    result.push(new BufferPiece(data));
                    targetDataLength = piecesTextLength > maxLeafLength ? idealLeafLength : piecesTextLength;
                    targetDataOffset = 0;
                    data = '';
                }
                var writingCnt = min(pieceLength - pieceOffset, targetDataLength - targetDataOffset);
                data += pieceText.substr(pieceOffset, writingCnt);
                pieceOffset += writingCnt;
                targetDataOffset += writingCnt;
                piecesTextLength -= writingCnt;
                // check that the buffer piece does not end in a \r or high surrogate
                if (targetDataOffset === targetDataLength && piecesTextLength > 0) {
                    var lastChar = data.charCodeAt(targetDataLength - 1);
                    if (lastChar === 13 /* CarriageReturn */ || (0xD800 <= lastChar && lastChar <= 0xDBFF)) {
                        // move lastChar over to next buffer piece
                        targetDataLength -= 1;
                        pieceOffset -= 1;
                        targetDataOffset -= 1;
                        piecesTextLength += 1;
                        data = data.substr(0, data.length - 1);
                    }
                }
            }
        }
        result.push(new BufferPiece(data));
    };
    return BufferPiece;
}());
export { BufferPiece };
function min(a, b) {
    return (a < b ? a : b);
}
export function createUint32Array(arr) {
    var r = new Uint32Array(arr.length);
    r.set(arr, 0);
    return r;
}
var LineStarts = /** @class */ (function () {
    function LineStarts(lineStarts, cr, lf, crlf, isBasicASCII) {
        this.lineStarts = lineStarts;
        this.cr = cr;
        this.lf = lf;
        this.crlf = crlf;
        this.isBasicASCII = isBasicASCII;
    }
    return LineStarts;
}());
export { LineStarts };
export function createLineStartsFast(str) {
    var r = [], rLength = 0;
    for (var i = 0, len = str.length; i < len; i++) {
        var chr = str.charCodeAt(i);
        if (chr === 13 /* CarriageReturn */) {
            if (i + 1 < len && str.charCodeAt(i + 1) === 10 /* LineFeed */) {
                // \r\n... case
                r[rLength++] = i + 2;
                i++; // skip \n
            }
            else {
                // \r... case
                r[rLength++] = i + 1;
            }
        }
        else if (chr === 10 /* LineFeed */) {
            r[rLength++] = i + 1;
        }
    }
    return createUint32Array(r);
}
export function createLineStarts(r, str) {
    r.length = 0;
    var rLength = 0;
    var cr = 0, lf = 0, crlf = 0;
    var isBasicASCII = true;
    for (var i = 0, len = str.length; i < len; i++) {
        var chr = str.charCodeAt(i);
        if (chr === 13 /* CarriageReturn */) {
            if (i + 1 < len && str.charCodeAt(i + 1) === 10 /* LineFeed */) {
                // \r\n... case
                crlf++;
                r[rLength++] = i + 2;
                i++; // skip \n
            }
            else {
                cr++;
                // \r... case
                r[rLength++] = i + 1;
            }
        }
        else if (chr === 10 /* LineFeed */) {
            lf++;
            r[rLength++] = i + 1;
        }
        else {
            if (isBasicASCII) {
                if (chr !== 9 /* Tab */ && (chr < 32 || chr > 126)) {
                    isBasicASCII = false;
                }
            }
        }
    }
    var result = new LineStarts(createUint32Array(r), cr, lf, crlf, isBasicASCII);
    r.length = 0;
    return result;
}
