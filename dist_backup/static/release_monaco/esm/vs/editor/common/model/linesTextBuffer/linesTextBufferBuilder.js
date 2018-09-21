/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as strings from '../../../../base/common/strings.js';
import { TextSource } from './textSource.js';
import { LinesTextBuffer } from './linesTextBuffer.js';
var TextBufferFactory = /** @class */ (function () {
    function TextBufferFactory(rawTextSource) {
        this.rawTextSource = rawTextSource;
    }
    TextBufferFactory.prototype.create = function (defaultEOL) {
        var textSource = TextSource.fromRawTextSource(this.rawTextSource, defaultEOL);
        return new LinesTextBuffer(textSource);
    };
    TextBufferFactory.prototype.getFirstLineText = function (lengthLimit) {
        return this.rawTextSource.lines[0].substr(0, lengthLimit);
    };
    return TextBufferFactory;
}());
export { TextBufferFactory };
var ModelLineBasedBuilder = /** @class */ (function () {
    function ModelLineBasedBuilder() {
        this.BOM = '';
        this.lines = [];
        this.currLineIndex = 0;
    }
    ModelLineBasedBuilder.prototype.acceptLines = function (lines) {
        if (this.currLineIndex === 0) {
            // Remove the BOM (if present)
            if (strings.startsWithUTF8BOM(lines[0])) {
                this.BOM = strings.UTF8_BOM_CHARACTER;
                lines[0] = lines[0].substr(1);
            }
        }
        for (var i = 0, len = lines.length; i < len; i++) {
            this.lines[this.currLineIndex++] = lines[i];
        }
    };
    ModelLineBasedBuilder.prototype.finish = function (carriageReturnCnt, containsRTL, isBasicASCII) {
        return new TextBufferFactory({
            BOM: this.BOM,
            lines: this.lines,
            containsRTL: containsRTL,
            totalCRCount: carriageReturnCnt,
            isBasicASCII: isBasicASCII,
        });
    };
    return ModelLineBasedBuilder;
}());
var LinesTextBufferBuilder = /** @class */ (function () {
    function LinesTextBufferBuilder() {
        this.leftoverPrevChunk = '';
        this.leftoverEndsInCR = false;
        this.totalCRCount = 0;
        this.lineBasedBuilder = new ModelLineBasedBuilder();
        this.containsRTL = false;
        this.isBasicASCII = true;
    }
    LinesTextBufferBuilder.prototype._updateCRCount = function (chunk) {
        // Count how many \r are present in chunk to determine the majority EOL sequence
        var chunkCarriageReturnCnt = 0;
        var lastCarriageReturnIndex = -1;
        while ((lastCarriageReturnIndex = chunk.indexOf('\r', lastCarriageReturnIndex + 1)) !== -1) {
            chunkCarriageReturnCnt++;
        }
        this.totalCRCount += chunkCarriageReturnCnt;
    };
    LinesTextBufferBuilder.prototype.acceptChunk = function (chunk) {
        if (chunk.length === 0) {
            return;
        }
        this._updateCRCount(chunk);
        if (!this.containsRTL) {
            this.containsRTL = strings.containsRTL(chunk);
        }
        if (this.isBasicASCII) {
            this.isBasicASCII = strings.isBasicASCII(chunk);
        }
        // Avoid dealing with a chunk that ends in \r (push the \r to the next chunk)
        if (this.leftoverEndsInCR) {
            chunk = '\r' + chunk;
        }
        if (chunk.charCodeAt(chunk.length - 1) === 13 /* CarriageReturn */) {
            this.leftoverEndsInCR = true;
            chunk = chunk.substr(0, chunk.length - 1);
        }
        else {
            this.leftoverEndsInCR = false;
        }
        var lines = chunk.split(/\r\n|\r|\n/);
        if (lines.length === 1) {
            // no \r or \n encountered
            this.leftoverPrevChunk += lines[0];
            return;
        }
        lines[0] = this.leftoverPrevChunk + lines[0];
        this.lineBasedBuilder.acceptLines(lines.slice(0, lines.length - 1));
        this.leftoverPrevChunk = lines[lines.length - 1];
    };
    LinesTextBufferBuilder.prototype.finish = function () {
        var finalLines = [this.leftoverPrevChunk];
        if (this.leftoverEndsInCR) {
            finalLines.push('');
        }
        this.lineBasedBuilder.acceptLines(finalLines);
        return this.lineBasedBuilder.finish(this.totalCRCount, this.containsRTL, this.isBasicASCII);
    };
    return LinesTextBufferBuilder;
}());
export { LinesTextBufferBuilder };
