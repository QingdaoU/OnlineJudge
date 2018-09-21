/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as strings from '../../../../base/common/strings.js';
import { DefaultEndOfLine } from '../../model.js';
import { BufferPiece, createLineStarts } from './bufferPiece.js';
import { ChunksTextBuffer } from './chunksTextBuffer.js';
var TextBufferFactory = /** @class */ (function () {
    function TextBufferFactory(_pieces, _averageChunkSize, _BOM, _cr, _lf, _crlf, _containsRTL, _isBasicASCII) {
        this._pieces = _pieces;
        this._averageChunkSize = _averageChunkSize;
        this._BOM = _BOM;
        this._cr = _cr;
        this._lf = _lf;
        this._crlf = _crlf;
        this._containsRTL = _containsRTL;
        this._isBasicASCII = _isBasicASCII;
    }
    /**
     * if text source is empty or with precisely one line, returns null. No end of line is detected.
     * if text source contains more lines ending with '\r\n', returns '\r\n'.
     * Otherwise returns '\n'. More lines end with '\n'.
     */
    TextBufferFactory.prototype._getEOL = function (defaultEOL) {
        var totalEOLCount = this._cr + this._lf + this._crlf;
        var totalCRCount = this._cr + this._crlf;
        if (totalEOLCount === 0) {
            // This is an empty file or a file with precisely one line
            return (defaultEOL === DefaultEndOfLine.LF ? '\n' : '\r\n');
        }
        if (totalCRCount > totalEOLCount / 2) {
            // More than half of the file contains \r\n ending lines
            return '\r\n';
        }
        // At least one line more ends in \n
        return '\n';
    };
    TextBufferFactory.prototype.create = function (defaultEOL) {
        var eol = this._getEOL(defaultEOL);
        var pieces = this._pieces;
        if ((eol === '\r\n' && (this._cr > 0 || this._lf > 0))
            || (eol === '\n' && (this._cr > 0 || this._crlf > 0))) {
            // Normalize pieces
            for (var i = 0, len = pieces.length; i < len; i++) {
                pieces[i] = BufferPiece.normalizeEOL(pieces[i], eol);
            }
        }
        return new ChunksTextBuffer(pieces, this._averageChunkSize, this._BOM, eol, this._containsRTL, this._isBasicASCII);
    };
    TextBufferFactory.prototype.getFirstLineText = function (lengthLimit) {
        var firstPiece = this._pieces[0];
        if (firstPiece.newLineCount() === 0) {
            return firstPiece.substr(0, lengthLimit);
        }
        var firstEOLOffset = firstPiece.lineStartFor(0);
        return firstPiece.substr(0, Math.min(lengthLimit, firstEOLOffset));
    };
    return TextBufferFactory;
}());
export { TextBufferFactory };
var ChunksTextBufferBuilder = /** @class */ (function () {
    function ChunksTextBufferBuilder() {
        this._rawPieces = [];
        this._hasPreviousChar = false;
        this._previousChar = 0;
        this._averageChunkSize = 0;
        this._tmpLineStarts = [];
        this.BOM = '';
        this.cr = 0;
        this.lf = 0;
        this.crlf = 0;
        this.containsRTL = false;
        this.isBasicASCII = true;
    }
    ChunksTextBufferBuilder.prototype.acceptChunk = function (chunk) {
        if (chunk.length === 0) {
            return;
        }
        if (this._rawPieces.length === 0) {
            if (strings.startsWithUTF8BOM(chunk)) {
                this.BOM = strings.UTF8_BOM_CHARACTER;
                chunk = chunk.substr(1);
            }
        }
        this._averageChunkSize = (this._averageChunkSize * this._rawPieces.length + chunk.length) / (this._rawPieces.length + 1);
        var lastChar = chunk.charCodeAt(chunk.length - 1);
        if (lastChar === 13 /* CarriageReturn */ || (lastChar >= 0xd800 && lastChar <= 0xdbff)) {
            // last character is \r or a high surrogate => keep it back
            this._acceptChunk1(chunk.substr(0, chunk.length - 1), false);
            this._hasPreviousChar = true;
            this._previousChar = lastChar;
        }
        else {
            this._acceptChunk1(chunk, false);
            this._hasPreviousChar = false;
            this._previousChar = lastChar;
        }
    };
    ChunksTextBufferBuilder.prototype._acceptChunk1 = function (chunk, allowEmptyStrings) {
        if (!allowEmptyStrings && chunk.length === 0) {
            // Nothing to do
            return;
        }
        if (this._hasPreviousChar) {
            this._acceptChunk2(chunk + String.fromCharCode(this._previousChar));
        }
        else {
            this._acceptChunk2(chunk);
        }
    };
    ChunksTextBufferBuilder.prototype._acceptChunk2 = function (chunk) {
        var lineStarts = createLineStarts(this._tmpLineStarts, chunk);
        this._rawPieces.push(new BufferPiece(chunk, lineStarts.lineStarts));
        this.cr += lineStarts.cr;
        this.lf += lineStarts.lf;
        this.crlf += lineStarts.crlf;
        if (this.isBasicASCII) {
            this.isBasicASCII = lineStarts.isBasicASCII;
        }
        if (!this.isBasicASCII && !this.containsRTL) {
            // No need to check if is basic ASCII
            this.containsRTL = strings.containsRTL(chunk);
        }
    };
    ChunksTextBufferBuilder.prototype.finish = function () {
        this._finish();
        return new TextBufferFactory(this._rawPieces, this._averageChunkSize, this.BOM, this.cr, this.lf, this.crlf, this.containsRTL, this.isBasicASCII);
    };
    ChunksTextBufferBuilder.prototype._finish = function () {
        if (this._rawPieces.length === 0) {
            // no chunks => forcefully go through accept chunk
            this._acceptChunk1('', true);
            return;
        }
        if (this._hasPreviousChar) {
            this._hasPreviousChar = false;
            // recreate last chunk
            var lastPiece = this._rawPieces[this._rawPieces.length - 1];
            var tmp = new BufferPiece(String.fromCharCode(this._previousChar));
            var newLastPiece = BufferPiece.join(lastPiece, tmp);
            this._rawPieces[this._rawPieces.length - 1] = newLastPiece;
            if (this._previousChar === 13 /* CarriageReturn */) {
                this.cr++;
            }
        }
    };
    return ChunksTextBufferBuilder;
}());
export { ChunksTextBufferBuilder };
