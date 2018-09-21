/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { EndOfLinePreference, ApplyEditsResult } from '../../model.js';
import { BufferPiece, LeafOffsetLenEdit } from './bufferPiece.js';
import { Position } from '../../core/position.js';
import { Range } from '../../core/range.js';
import * as strings from '../../../../base/common/strings.js';
var ChunksTextBuffer = /** @class */ (function () {
    function ChunksTextBuffer(pieces, _averageChunkSize, BOM, eol, containsRTL, isBasicASCII) {
        this._BOM = BOM;
        var averageChunkSize = Math.floor(Math.min(65536.0, Math.max(128.0, _averageChunkSize)));
        var delta = Math.floor(averageChunkSize / 3);
        var min = averageChunkSize - delta;
        var max = 2 * min;
        this._actual = new Buffer(pieces, min, max, eol);
        this._mightContainRTL = containsRTL;
        this._mightContainNonBasicASCII = !isBasicASCII;
    }
    ChunksTextBuffer.prototype.equals = function (other) {
        if (!(other instanceof ChunksTextBuffer)) {
            return false;
        }
        return this._actual.equals(other._actual);
    };
    ChunksTextBuffer.prototype.mightContainRTL = function () {
        return this._mightContainRTL;
    };
    ChunksTextBuffer.prototype.mightContainNonBasicASCII = function () {
        return this._mightContainNonBasicASCII;
    };
    ChunksTextBuffer.prototype.getBOM = function () {
        return this._BOM;
    };
    ChunksTextBuffer.prototype.getEOL = function () {
        return this._actual.getEOL();
    };
    ChunksTextBuffer.prototype.getOffsetAt = function (lineNumber, column) {
        return this._actual.convertPositionToOffset(lineNumber, column);
    };
    ChunksTextBuffer.prototype.getPositionAt = function (offset) {
        return this._actual.convertOffsetToPosition(offset);
    };
    ChunksTextBuffer.prototype.getRangeAt = function (offset, length) {
        return this._actual.convertOffsetLenToRange(offset, length);
    };
    ChunksTextBuffer.prototype.getValueInRange = function (range, eol) {
        if (range.isEmpty()) {
            return '';
        }
        var text = this._actual.getValueInRange(range);
        switch (eol) {
            case EndOfLinePreference.TextDefined:
                return text;
            case EndOfLinePreference.LF:
                if (this.getEOL() === '\n') {
                    return text;
                }
                else {
                    return text.replace(/\r\n/g, '\n');
                }
            case EndOfLinePreference.CRLF:
                if (this.getEOL() === '\r\n') {
                    return text;
                }
                else {
                    return text.replace(/\n/g, '\r\n');
                }
        }
        return null;
    };
    ChunksTextBuffer.prototype.createSnapshot = function (preserveBOM) {
        return this._actual.createSnapshot(preserveBOM ? this._BOM : '');
    };
    ChunksTextBuffer.prototype.getValueLengthInRange = function (range, eol) {
        if (range.isEmpty()) {
            return 0;
        }
        var eolCount = range.endLineNumber - range.startLineNumber;
        var result = this._actual.getValueLengthInRange(range);
        switch (eol) {
            case EndOfLinePreference.TextDefined:
                return result;
            case EndOfLinePreference.LF:
                if (this.getEOL() === '\n') {
                    return result;
                }
                else {
                    return result - eolCount; // \r\n => \n
                }
            case EndOfLinePreference.CRLF:
                if (this.getEOL() === '\r\n') {
                    return result;
                }
                else {
                    return result + eolCount; // \n => \r\n
                }
        }
        return 0;
    };
    ChunksTextBuffer.prototype.getLength = function () {
        return this._actual.getLength();
    };
    ChunksTextBuffer.prototype.getLineCount = function () {
        return this._actual.getLineCount();
    };
    ChunksTextBuffer.prototype.getLinesContent = function () {
        return this._actual.getLinesContent();
    };
    ChunksTextBuffer.prototype.getLineContent = function (lineNumber) {
        return this._actual.getLineContent(lineNumber);
    };
    ChunksTextBuffer.prototype.getLineCharCode = function (lineNumber, index) {
        return this._actual.getLineCharCode(lineNumber, index);
    };
    ChunksTextBuffer.prototype.getLineLength = function (lineNumber) {
        return this._actual.getLineLength(lineNumber);
    };
    ChunksTextBuffer.prototype.getLineFirstNonWhitespaceColumn = function (lineNumber) {
        var result = this._actual.getLineFirstNonWhitespaceIndex(lineNumber);
        if (result === -1) {
            return 0;
        }
        return result + 1;
    };
    ChunksTextBuffer.prototype.getLineLastNonWhitespaceColumn = function (lineNumber) {
        var result = this._actual.getLineLastNonWhitespaceIndex(lineNumber);
        if (result === -1) {
            return 0;
        }
        return result + 1;
    };
    ChunksTextBuffer.prototype.setEOL = function (newEOL) {
        if (this.getEOL() === newEOL) {
            // nothing to do...
            return;
        }
        this._actual.setEOL(newEOL);
    };
    ChunksTextBuffer._sortOpsAscending = function (a, b) {
        var r = Range.compareRangesUsingEnds(a.range, b.range);
        if (r === 0) {
            return a.sortIndex - b.sortIndex;
        }
        return r;
    };
    ChunksTextBuffer._sortOpsDescending = function (a, b) {
        var r = Range.compareRangesUsingEnds(a.range, b.range);
        if (r === 0) {
            return b.sortIndex - a.sortIndex;
        }
        return -r;
    };
    ChunksTextBuffer.prototype.applyEdits = function (rawOperations, recordTrimAutoWhitespace) {
        if (rawOperations.length === 0) {
            return new ApplyEditsResult([], [], []);
        }
        var mightContainRTL = this._mightContainRTL;
        var mightContainNonBasicASCII = this._mightContainNonBasicASCII;
        var canReduceOperations = true;
        var operations = [];
        for (var i = 0; i < rawOperations.length; i++) {
            var op = rawOperations[i];
            if (canReduceOperations && op._isTracked) {
                canReduceOperations = false;
            }
            var validatedRange = op.range;
            if (!mightContainRTL && op.text) {
                // check if the new inserted text contains RTL
                mightContainRTL = strings.containsRTL(op.text);
            }
            if (!mightContainNonBasicASCII && op.text) {
                mightContainNonBasicASCII = !strings.isBasicASCII(op.text);
            }
            operations[i] = {
                sortIndex: i,
                identifier: op.identifier || null,
                range: validatedRange,
                rangeOffset: this.getOffsetAt(validatedRange.startLineNumber, validatedRange.startColumn),
                rangeLength: this.getValueLengthInRange(validatedRange, EndOfLinePreference.TextDefined),
                lines: op.text ? op.text.split(/\r\n|\r|\n/) : null,
                forceMoveMarkers: op.forceMoveMarkers || false,
                isAutoWhitespaceEdit: op.isAutoWhitespaceEdit || false
            };
        }
        // Sort operations ascending
        operations.sort(ChunksTextBuffer._sortOpsAscending);
        for (var i = 0, count = operations.length - 1; i < count; i++) {
            var rangeEnd = operations[i].range.getEndPosition();
            var nextRangeStart = operations[i + 1].range.getStartPosition();
            if (nextRangeStart.isBefore(rangeEnd)) {
                // overlapping ranges
                throw new Error('Overlapping ranges are not allowed!');
            }
        }
        if (canReduceOperations) {
            operations = this._reduceOperations(operations);
        }
        // Delta encode operations
        var reverseRanges = ChunksTextBuffer._getInverseEditRanges(operations);
        var newTrimAutoWhitespaceCandidates = [];
        for (var i = 0; i < operations.length; i++) {
            var op = operations[i];
            var reverseRange = reverseRanges[i];
            if (recordTrimAutoWhitespace && op.isAutoWhitespaceEdit && op.range.isEmpty()) {
                // Record already the future line numbers that might be auto whitespace removal candidates on next edit
                for (var lineNumber = reverseRange.startLineNumber; lineNumber <= reverseRange.endLineNumber; lineNumber++) {
                    var currentLineContent = '';
                    if (lineNumber === reverseRange.startLineNumber) {
                        currentLineContent = this.getLineContent(op.range.startLineNumber);
                        if (strings.firstNonWhitespaceIndex(currentLineContent) !== -1) {
                            continue;
                        }
                    }
                    newTrimAutoWhitespaceCandidates.push({ lineNumber: lineNumber, oldContent: currentLineContent });
                }
            }
        }
        var reverseOperations = [];
        for (var i = 0; i < operations.length; i++) {
            var op = operations[i];
            var reverseRange = reverseRanges[i];
            reverseOperations[i] = {
                identifier: op.identifier,
                range: reverseRange,
                text: this.getValueInRange(op.range, EndOfLinePreference.TextDefined),
                forceMoveMarkers: op.forceMoveMarkers
            };
        }
        this._mightContainRTL = mightContainRTL;
        this._mightContainNonBasicASCII = mightContainNonBasicASCII;
        var contentChanges = this._doApplyEdits(operations);
        var trimAutoWhitespaceLineNumbers = null;
        if (recordTrimAutoWhitespace && newTrimAutoWhitespaceCandidates.length > 0) {
            // sort line numbers auto whitespace removal candidates for next edit descending
            newTrimAutoWhitespaceCandidates.sort(function (a, b) { return b.lineNumber - a.lineNumber; });
            trimAutoWhitespaceLineNumbers = [];
            for (var i = 0, len = newTrimAutoWhitespaceCandidates.length; i < len; i++) {
                var lineNumber = newTrimAutoWhitespaceCandidates[i].lineNumber;
                if (i > 0 && newTrimAutoWhitespaceCandidates[i - 1].lineNumber === lineNumber) {
                    // Do not have the same line number twice
                    continue;
                }
                var prevContent = newTrimAutoWhitespaceCandidates[i].oldContent;
                var lineContent = this.getLineContent(lineNumber);
                if (lineContent.length === 0 || lineContent === prevContent || strings.firstNonWhitespaceIndex(lineContent) !== -1) {
                    continue;
                }
                trimAutoWhitespaceLineNumbers.push(lineNumber);
            }
        }
        return new ApplyEditsResult(reverseOperations, contentChanges, trimAutoWhitespaceLineNumbers);
    };
    /**
     * Transform operations such that they represent the same logic edit,
     * but that they also do not cause OOM crashes.
     */
    ChunksTextBuffer.prototype._reduceOperations = function (operations) {
        if (operations.length < 1000) {
            // We know from empirical testing that a thousand edits work fine regardless of their shape.
            return operations;
        }
        // At one point, due to how events are emitted and how each operation is handled,
        // some operations can trigger a high ammount of temporary string allocations,
        // that will immediately get edited again.
        // e.g. a formatter inserting ridiculous ammounts of \n on a model with a single line
        // Therefore, the strategy is to collapse all the operations into a huge single edit operation
        return [this._toSingleEditOperation(operations)];
    };
    ChunksTextBuffer.prototype._toSingleEditOperation = function (operations) {
        var forceMoveMarkers = false, firstEditRange = operations[0].range, lastEditRange = operations[operations.length - 1].range, entireEditRange = new Range(firstEditRange.startLineNumber, firstEditRange.startColumn, lastEditRange.endLineNumber, lastEditRange.endColumn), lastEndLineNumber = firstEditRange.startLineNumber, lastEndColumn = firstEditRange.startColumn, result = [];
        for (var i = 0, len = operations.length; i < len; i++) {
            var operation = operations[i], range = operation.range;
            forceMoveMarkers = forceMoveMarkers || operation.forceMoveMarkers;
            // (1) -- Push old text
            for (var lineNumber = lastEndLineNumber; lineNumber < range.startLineNumber; lineNumber++) {
                if (lineNumber === lastEndLineNumber) {
                    result.push(this.getLineContent(lineNumber).substring(lastEndColumn - 1));
                }
                else {
                    result.push('\n');
                    result.push(this.getLineContent(lineNumber));
                }
            }
            if (range.startLineNumber === lastEndLineNumber) {
                result.push(this.getLineContent(range.startLineNumber).substring(lastEndColumn - 1, range.startColumn - 1));
            }
            else {
                result.push('\n');
                result.push(this.getLineContent(range.startLineNumber).substring(0, range.startColumn - 1));
            }
            // (2) -- Push new text
            if (operation.lines) {
                for (var j = 0, lenJ = operation.lines.length; j < lenJ; j++) {
                    if (j !== 0) {
                        result.push('\n');
                    }
                    result.push(operation.lines[j]);
                }
            }
            lastEndLineNumber = operation.range.endLineNumber;
            lastEndColumn = operation.range.endColumn;
        }
        return {
            sortIndex: 0,
            identifier: operations[0].identifier,
            range: entireEditRange,
            rangeOffset: this.getOffsetAt(entireEditRange.startLineNumber, entireEditRange.startColumn),
            rangeLength: this.getValueLengthInRange(entireEditRange, EndOfLinePreference.TextDefined),
            lines: result.join('').split('\n'),
            forceMoveMarkers: forceMoveMarkers,
            isAutoWhitespaceEdit: false
        };
    };
    ChunksTextBuffer.prototype._doApplyEdits = function (operations) {
        // Sort operations descending
        operations.sort(ChunksTextBuffer._sortOpsDescending);
        var contentChanges = [];
        var edits = [];
        for (var i = 0, len = operations.length; i < len; i++) {
            var op = operations[i];
            var text = (op.lines ? op.lines.join(this.getEOL()) : '');
            edits[i] = new OffsetLenEdit(op.sortIndex, op.rangeOffset, op.rangeLength, text);
            var startLineNumber = op.range.startLineNumber;
            var startColumn = op.range.startColumn;
            var endLineNumber = op.range.endLineNumber;
            var endColumn = op.range.endColumn;
            if (startLineNumber === endLineNumber && startColumn === endColumn && (!op.lines || op.lines.length === 0)) {
                // no-op
                continue;
            }
            contentChanges.push({
                range: op.range,
                rangeLength: op.rangeLength,
                text: text,
                rangeOffset: op.rangeOffset,
                forceMoveMarkers: op.forceMoveMarkers
            });
        }
        this._actual.replaceOffsetLen(edits);
        return contentChanges;
    };
    /**
     * Assumes `operations` are validated and sorted ascending
     */
    ChunksTextBuffer._getInverseEditRanges = function (operations) {
        var result = [];
        var prevOpEndLineNumber;
        var prevOpEndColumn;
        var prevOp = null;
        for (var i = 0, len = operations.length; i < len; i++) {
            var op = operations[i];
            var startLineNumber = void 0;
            var startColumn = void 0;
            if (prevOp) {
                if (prevOp.range.endLineNumber === op.range.startLineNumber) {
                    startLineNumber = prevOpEndLineNumber;
                    startColumn = prevOpEndColumn + (op.range.startColumn - prevOp.range.endColumn);
                }
                else {
                    startLineNumber = prevOpEndLineNumber + (op.range.startLineNumber - prevOp.range.endLineNumber);
                    startColumn = op.range.startColumn;
                }
            }
            else {
                startLineNumber = op.range.startLineNumber;
                startColumn = op.range.startColumn;
            }
            var resultRange = void 0;
            if (op.lines && op.lines.length > 0) {
                // the operation inserts something
                var lineCount = op.lines.length;
                var firstLine = op.lines[0];
                var lastLine = op.lines[lineCount - 1];
                if (lineCount === 1) {
                    // single line insert
                    resultRange = new Range(startLineNumber, startColumn, startLineNumber, startColumn + firstLine.length);
                }
                else {
                    // multi line insert
                    resultRange = new Range(startLineNumber, startColumn, startLineNumber + lineCount - 1, lastLine.length + 1);
                }
            }
            else {
                // There is nothing to insert
                resultRange = new Range(startLineNumber, startColumn, startLineNumber, startColumn);
            }
            prevOpEndLineNumber = resultRange.endLineNumber;
            prevOpEndColumn = resultRange.endColumn;
            result.push(resultRange);
            prevOp = op;
        }
        return result;
    };
    return ChunksTextBuffer;
}());
export { ChunksTextBuffer };
var BufferNodes = /** @class */ (function () {
    function BufferNodes(count) {
        this.length = new Uint32Array(count);
        this.newLineCount = new Uint32Array(count);
    }
    return BufferNodes;
}());
var BufferCursor = /** @class */ (function () {
    function BufferCursor(offset, leafIndex, leafStartOffset, leafStartNewLineCount) {
        this.offset = offset;
        this.leafIndex = leafIndex;
        this.leafStartOffset = leafStartOffset;
        this.leafStartNewLineCount = leafStartNewLineCount;
    }
    BufferCursor.prototype.set = function (offset, leafIndex, leafStartOffset, leafStartNewLineCount) {
        this.offset = offset;
        this.leafIndex = leafIndex;
        this.leafStartOffset = leafStartOffset;
        this.leafStartNewLineCount = leafStartNewLineCount;
    };
    return BufferCursor;
}());
var OffsetLenEdit = /** @class */ (function () {
    function OffsetLenEdit(initialIndex, offset, length, text) {
        this.initialIndex = initialIndex;
        this.offset = offset;
        this.length = length;
        this.text = text;
    }
    return OffsetLenEdit;
}());
var InternalOffsetLenEdit = /** @class */ (function () {
    function InternalOffsetLenEdit(startLeafIndex, startInnerOffset, endLeafIndex, endInnerOffset, text) {
        this.startLeafIndex = startLeafIndex;
        this.startInnerOffset = startInnerOffset;
        this.endLeafIndex = endLeafIndex;
        this.endInnerOffset = endInnerOffset;
        this.text = text;
    }
    return InternalOffsetLenEdit;
}());
var LeafReplacement = /** @class */ (function () {
    function LeafReplacement(startLeafIndex, endLeafIndex, replacements) {
        this.startLeafIndex = startLeafIndex;
        this.endLeafIndex = endLeafIndex;
        this.replacements = replacements;
    }
    return LeafReplacement;
}());
var BUFFER_CURSOR_POOL_SIZE = 10;
var BufferCursorPool = new /** @class */ (function () {
    function class_1() {
        this._pool = [];
        for (var i = 0; i < BUFFER_CURSOR_POOL_SIZE; i++) {
            this._pool[i] = new BufferCursor(0, 0, 0, 0);
        }
        this._len = this._pool.length;
    }
    class_1.prototype.put = function (cursor) {
        if (this._len > this._pool.length) {
            // oh, well
            return;
        }
        this._pool[this._len++] = cursor;
    };
    class_1.prototype.take = function () {
        if (this._len === 0) {
            // oh, well
            console.log("insufficient BufferCursor pool");
            return new BufferCursor(0, 0, 0, 0);
        }
        var result = this._pool[this._len - 1];
        this._pool[this._len--] = null;
        return result;
    };
    return class_1;
}());
var BufferSnapshot = /** @class */ (function () {
    function BufferSnapshot(pieces, BOM) {
        this._pieces = pieces;
        this._piecesLength = this._pieces.length;
        this._BOM = BOM;
        this._piecesIndex = 0;
    }
    BufferSnapshot.prototype.read = function () {
        if (this._piecesIndex >= this._piecesLength) {
            return null;
        }
        var result = null;
        if (this._piecesIndex === 0) {
            result = this._BOM + this._pieces[this._piecesIndex].text;
        }
        else {
            result = this._pieces[this._piecesIndex].text;
        }
        this._piecesIndex++;
        return result;
    };
    return BufferSnapshot;
}());
var Buffer = /** @class */ (function () {
    function Buffer(pieces, minLeafLength, maxLeafLength, eol) {
        if (!(2 * minLeafLength >= maxLeafLength)) {
            throw new Error("assertion violation");
        }
        this._minLeafLength = minLeafLength;
        this._maxLeafLength = maxLeafLength;
        this._idealLeafLength = (minLeafLength + maxLeafLength) >>> 1;
        this._eol = eol;
        this._eolLength = this._eol.length;
        this._leafs = pieces;
        this._nodes = null;
        this._nodesCount = 0;
        this._leafsStart = 0;
        this._leafsEnd = 0;
        this._rebuildNodes();
    }
    Buffer.prototype.equals = function (other) {
        return Buffer.equals(this, other);
    };
    Buffer.equals = function (a, b) {
        var aLength = a.getLength();
        var bLength = b.getLength();
        if (aLength !== bLength) {
            return false;
        }
        if (a.getLineCount() !== b.getLineCount()) {
            return false;
        }
        var remaining = aLength;
        var aLeafIndex = -1, aLeaf = null, aLeafLength = 0, aLeafRemaining = 0;
        var bLeafIndex = -1, bLeaf = null, bLeafLength = 0, bLeafRemaining = 0;
        while (remaining > 0) {
            if (aLeafRemaining === 0) {
                aLeafIndex++;
                aLeaf = a._leafs[aLeafIndex];
                aLeafLength = aLeaf.length();
                aLeafRemaining = aLeafLength;
            }
            if (bLeafRemaining === 0) {
                bLeafIndex++;
                bLeaf = b._leafs[bLeafIndex];
                bLeafLength = bLeaf.length();
                bLeafRemaining = bLeafLength;
            }
            var consuming = Math.min(aLeafRemaining, bLeafRemaining);
            var aStr = aLeaf.substr(aLeafLength - aLeafRemaining, consuming);
            var bStr = bLeaf.substr(bLeafLength - bLeafRemaining, consuming);
            if (aStr !== bStr) {
                return false;
            }
            remaining -= consuming;
            aLeafRemaining -= consuming;
            bLeafRemaining -= consuming;
        }
        return true;
    };
    Buffer.prototype.getEOL = function () {
        return this._eol;
    };
    Buffer.prototype._rebuildNodes = function () {
        var leafsCount = this._leafs.length;
        this._nodesCount = (1 << log2(leafsCount));
        this._leafsStart = this._nodesCount;
        this._leafsEnd = this._leafsStart + leafsCount;
        this._nodes = new BufferNodes(this._nodesCount);
        for (var i = this._nodesCount - 1; i >= 1; i--) {
            this._updateSingleNode(i);
        }
    };
    Buffer.prototype._updateSingleNode = function (nodeIndex) {
        var left = LEFT_CHILD(nodeIndex);
        var right = RIGHT_CHILD(nodeIndex);
        var length = 0;
        var newLineCount = 0;
        if (this.IS_NODE(left)) {
            length += this._nodes.length[left];
            newLineCount += this._nodes.newLineCount[left];
        }
        else if (this.IS_LEAF(left)) {
            var leaf = this._leafs[this.NODE_TO_LEAF_INDEX(left)];
            length += leaf.length();
            newLineCount += leaf.newLineCount();
        }
        if (this.IS_NODE(right)) {
            length += this._nodes.length[right];
            newLineCount += this._nodes.newLineCount[right];
        }
        else if (this.IS_LEAF(right)) {
            var leaf = this._leafs[this.NODE_TO_LEAF_INDEX(right)];
            length += leaf.length();
            newLineCount += leaf.newLineCount();
        }
        this._nodes.length[nodeIndex] = length;
        this._nodes.newLineCount[nodeIndex] = newLineCount;
    };
    Buffer.prototype._findOffset = function (offset, result) {
        if (offset > this._nodes.length[1]) {
            return false;
        }
        var it = 1;
        var searchOffset = offset;
        var leafStartOffset = 0;
        var leafStartNewLineCount = 0;
        while (!this.IS_LEAF(it)) {
            var left = LEFT_CHILD(it);
            var right = RIGHT_CHILD(it);
            var leftNewLineCount = 0;
            var leftLength = 0;
            if (this.IS_NODE(left)) {
                leftNewLineCount = this._nodes.newLineCount[left];
                leftLength = this._nodes.length[left];
            }
            else if (this.IS_LEAF(left)) {
                var leaf = this._leafs[this.NODE_TO_LEAF_INDEX(left)];
                leftNewLineCount = leaf.newLineCount();
                leftLength = leaf.length();
            }
            var rightLength = 0;
            if (this.IS_NODE(right)) {
                rightLength += this._nodes.length[right];
            }
            else if (this.IS_LEAF(right)) {
                rightLength += this._leafs[this.NODE_TO_LEAF_INDEX(right)].length();
            }
            if (searchOffset < leftLength || rightLength === 0) {
                // go left
                it = left;
            }
            else {
                // go right
                searchOffset -= leftLength;
                leafStartOffset += leftLength;
                leafStartNewLineCount += leftNewLineCount;
                it = right;
            }
        }
        it = this.NODE_TO_LEAF_INDEX(it);
        result.set(offset, it, leafStartOffset, leafStartNewLineCount);
        return true;
    };
    Buffer.prototype._findOffsetCloseAfter = function (offset, start, result) {
        if (offset > this._nodes.length[1]) {
            return false;
        }
        var innerOffset = offset - start.leafStartOffset;
        var leafsCount = this._leafs.length;
        var leafIndex = start.leafIndex;
        var leafStartOffset = start.leafStartOffset;
        var leafStartNewLineCount = start.leafStartNewLineCount;
        while (true) {
            var leaf = this._leafs[leafIndex];
            if (innerOffset < leaf.length() || (innerOffset === leaf.length() && leafIndex + 1 === leafsCount)) {
                result.set(offset, leafIndex, leafStartOffset, leafStartNewLineCount);
                return true;
            }
            leafIndex++;
            if (leafIndex >= leafsCount) {
                result.set(offset, leafIndex, leafStartOffset, leafStartNewLineCount);
                return true;
            }
            leafStartOffset += leaf.length();
            leafStartNewLineCount += leaf.newLineCount();
            innerOffset -= leaf.length();
        }
    };
    Buffer.prototype._findLineStart = function (lineNumber, result) {
        var lineIndex = lineNumber - 1;
        if (lineIndex < 0 || lineIndex > this._nodes.newLineCount[1]) {
            result.set(0, 0, 0, 0);
            return false;
        }
        var it = 1;
        var leafStartOffset = 0;
        var leafStartNewLineCount = 0;
        while (!this.IS_LEAF(it)) {
            var left = LEFT_CHILD(it);
            var right = RIGHT_CHILD(it);
            var leftNewLineCount = 0;
            var leftLength = 0;
            if (this.IS_NODE(left)) {
                leftNewLineCount = this._nodes.newLineCount[left];
                leftLength = this._nodes.length[left];
            }
            else if (this.IS_LEAF(left)) {
                var leaf = this._leafs[this.NODE_TO_LEAF_INDEX(left)];
                leftNewLineCount = leaf.newLineCount();
                leftLength = leaf.length();
            }
            if (lineIndex <= leftNewLineCount) {
                // go left
                it = left;
                continue;
            }
            // go right
            lineIndex -= leftNewLineCount;
            leafStartOffset += leftLength;
            leafStartNewLineCount += leftNewLineCount;
            it = right;
        }
        it = this.NODE_TO_LEAF_INDEX(it);
        var innerLineStartOffset = (lineIndex === 0 ? 0 : this._leafs[it].lineStartFor(lineIndex - 1));
        result.set(leafStartOffset + innerLineStartOffset, it, leafStartOffset, leafStartNewLineCount);
        return true;
    };
    Buffer.prototype._findLineEnd = function (start, lineNumber, result) {
        var innerLineIndex = lineNumber - 1 - start.leafStartNewLineCount;
        var leafsCount = this._leafs.length;
        var leafIndex = start.leafIndex;
        var leafStartOffset = start.leafStartOffset;
        var leafStartNewLineCount = start.leafStartNewLineCount;
        while (true) {
            var leaf = this._leafs[leafIndex];
            if (innerLineIndex < leaf.newLineCount()) {
                var lineEndOffset = this._leafs[leafIndex].lineStartFor(innerLineIndex);
                result.set(leafStartOffset + lineEndOffset, leafIndex, leafStartOffset, leafStartNewLineCount);
                return;
            }
            leafIndex++;
            if (leafIndex >= leafsCount) {
                result.set(leafStartOffset + leaf.length(), leafIndex - 1, leafStartOffset, leafStartNewLineCount);
                return;
            }
            leafStartOffset += leaf.length();
            leafStartNewLineCount += leaf.newLineCount();
            innerLineIndex = 0;
        }
    };
    Buffer.prototype._findLine = function (lineNumber, start, end) {
        if (!this._findLineStart(lineNumber, start)) {
            return false;
        }
        this._findLineEnd(start, lineNumber, end);
        return true;
    };
    Buffer.prototype.getLength = function () {
        return this._nodes.length[1];
    };
    Buffer.prototype.getLineCount = function () {
        return this._nodes.newLineCount[1] + 1;
    };
    Buffer.prototype.getLineContent = function (lineNumber) {
        var start = BufferCursorPool.take();
        var end = BufferCursorPool.take();
        if (!this._findLine(lineNumber, start, end)) {
            BufferCursorPool.put(start);
            BufferCursorPool.put(end);
            throw new Error("Line not found");
        }
        var result;
        if (lineNumber === this.getLineCount()) {
            // last line is not trailed by an eol
            result = this.extractString(start, end.offset - start.offset);
        }
        else {
            result = this.extractString(start, end.offset - start.offset - this._eolLength);
        }
        BufferCursorPool.put(start);
        BufferCursorPool.put(end);
        return result;
    };
    Buffer.prototype.getLineCharCode = function (lineNumber, index) {
        var start = BufferCursorPool.take();
        if (!this._findLineStart(lineNumber, start)) {
            BufferCursorPool.put(start);
            throw new Error("Line not found");
        }
        var tmp = BufferCursorPool.take();
        this._findOffsetCloseAfter(start.offset + index, start, tmp);
        var result = this._leafs[tmp.leafIndex].charCodeAt(tmp.offset - tmp.leafStartNewLineCount);
        BufferCursorPool.put(tmp);
        BufferCursorPool.put(start);
        return result;
    };
    Buffer.prototype.getLineLength = function (lineNumber) {
        var start = BufferCursorPool.take();
        var end = BufferCursorPool.take();
        if (!this._findLine(lineNumber, start, end)) {
            BufferCursorPool.put(start);
            BufferCursorPool.put(end);
            throw new Error("Line not found");
        }
        var result;
        if (lineNumber === this.getLineCount()) {
            // last line is not trailed by an eol
            result = end.offset - start.offset;
        }
        else {
            result = end.offset - start.offset - this._eolLength;
        }
        BufferCursorPool.put(start);
        BufferCursorPool.put(end);
        return result;
    };
    Buffer.prototype.getLineFirstNonWhitespaceIndex = function (lineNumber) {
        var start = BufferCursorPool.take();
        if (!this._findLineStart(lineNumber, start)) {
            BufferCursorPool.put(start);
            throw new Error("Line not found");
        }
        var leafIndex = start.leafIndex;
        var searchStartOffset = start.offset - start.leafStartOffset;
        BufferCursorPool.put(start);
        var leafsCount = this._leafs.length;
        var totalDelta = 0;
        while (true) {
            var leaf = this._leafs[leafIndex];
            var leafResult = leaf.findLineFirstNonWhitespaceIndex(searchStartOffset);
            if (leafResult === -2) {
                // reached EOL
                return -1;
            }
            if (leafResult !== -1) {
                return (leafResult - searchStartOffset) + totalDelta;
            }
            leafIndex++;
            if (leafIndex >= leafsCount) {
                return -1;
            }
            totalDelta += (leaf.length() - searchStartOffset);
            searchStartOffset = 0;
        }
    };
    Buffer.prototype.getLineLastNonWhitespaceIndex = function (lineNumber) {
        var start = BufferCursorPool.take();
        var end = BufferCursorPool.take();
        if (!this._findLineStart(lineNumber, start)) {
            BufferCursorPool.put(start);
            BufferCursorPool.put(end);
            throw new Error("Line not found");
        }
        this._findLineEnd(start, lineNumber, end);
        var startOffset = start.offset;
        var endOffset = end.offset;
        var leafIndex = end.leafIndex;
        var searchStartOffset = end.offset - end.leafStartOffset - this._eolLength;
        BufferCursorPool.put(start);
        BufferCursorPool.put(end);
        var totalDelta = 0;
        while (true) {
            var leaf = this._leafs[leafIndex];
            var leafResult = leaf.findLineLastNonWhitespaceIndex(searchStartOffset);
            if (leafResult === -2) {
                // reached EOL
                return -1;
            }
            if (leafResult !== -1) {
                var delta = (searchStartOffset - 1 - leafResult);
                var absoluteOffset = (endOffset - this._eolLength) - delta - totalDelta;
                return absoluteOffset - startOffset;
            }
            leafIndex--;
            if (leafIndex < 0) {
                return -1;
            }
            totalDelta += searchStartOffset;
            searchStartOffset = leaf.length();
        }
    };
    Buffer.prototype.getLinesContent = function () {
        var result = new Array(this.getLineCount());
        var resultIndex = 0;
        var currentLine = '';
        for (var leafIndex = 0, leafsCount = this._leafs.length; leafIndex < leafsCount; leafIndex++) {
            var leaf = this._leafs[leafIndex];
            var leafNewLineCount = leaf.newLineCount();
            if (leafNewLineCount === 0) {
                // special case => push entire leaf text
                currentLine += leaf.text;
                continue;
            }
            var leafSubstrOffset = 0;
            for (var newLineIndex = 0; newLineIndex < leafNewLineCount; newLineIndex++) {
                var newLineStart = leaf.lineStartFor(newLineIndex);
                currentLine += leaf.substr(leafSubstrOffset, newLineStart - leafSubstrOffset - this._eolLength);
                result[resultIndex++] = currentLine;
                currentLine = '';
                leafSubstrOffset = newLineStart;
            }
            currentLine += leaf.substr(leafSubstrOffset, leaf.length());
        }
        result[resultIndex++] = currentLine;
        return result;
    };
    Buffer.prototype.extractString = function (start, len) {
        if (!(start.offset + len <= this._nodes.length[1])) {
            throw new Error("assertion violation");
        }
        var innerLeafOffset = start.offset - start.leafStartOffset;
        var leafIndex = start.leafIndex;
        var res = '';
        while (len > 0) {
            var leaf = this._leafs[leafIndex];
            var cnt = Math.min(len, leaf.length() - innerLeafOffset);
            res += leaf.substr(innerLeafOffset, cnt);
            len -= cnt;
            innerLeafOffset = 0;
            if (len === 0) {
                break;
            }
            leafIndex++;
        }
        return res;
    };
    Buffer.prototype._getOffsetAt = function (lineNumber, column, result) {
        var lineStart = BufferCursorPool.take();
        if (!this._findLineStart(lineNumber, lineStart)) {
            BufferCursorPool.put(lineStart);
            return false;
        }
        var startOffset = lineStart.offset + column - 1;
        if (!this._findOffsetCloseAfter(startOffset, lineStart, result)) {
            BufferCursorPool.put(lineStart);
            return false;
        }
        BufferCursorPool.put(lineStart);
        return true;
    };
    Buffer.prototype.convertPositionToOffset = function (lineNumber, column) {
        var r = BufferCursorPool.take();
        if (!this._findLineStart(lineNumber, r)) {
            BufferCursorPool.put(r);
            throw new Error("Position not found");
        }
        var result = r.offset + column - 1;
        BufferCursorPool.put(r);
        return result;
    };
    /**
     * returns `lineNumber`
     */
    Buffer.prototype._findLineStartBeforeOffsetInLeaf = function (offset, leafIndex, leafStartOffset, leafStartNewLineCount, result) {
        var leaf = this._leafs[leafIndex];
        var lineStartIndex = leaf.findLineStartBeforeOffset(offset - leafStartOffset);
        var lineStartOffset = leafStartOffset + leaf.lineStartFor(lineStartIndex);
        result.set(lineStartOffset, leafIndex, leafStartOffset, leafStartNewLineCount);
        return leafStartNewLineCount + lineStartIndex + 2;
    };
    /**
     * returns `lineNumber`.
     */
    Buffer.prototype._findLineStartBeforeOffset = function (offset, location, result) {
        var leafIndex = location.leafIndex;
        var leafStartOffset = location.leafStartOffset;
        var leafStartNewLineCount = location.leafStartNewLineCount;
        while (true) {
            var leaf = this._leafs[leafIndex];
            if (leaf.newLineCount() >= 1 && leaf.lineStartFor(0) + leafStartOffset <= offset) {
                // must be in this leaf
                return this._findLineStartBeforeOffsetInLeaf(offset, leafIndex, leafStartOffset, leafStartNewLineCount, result);
            }
            // continue looking in previous leaf
            leafIndex--;
            if (leafIndex < 0) {
                result.set(0, 0, 0, 0);
                return 1;
            }
            leafStartOffset -= this._leafs[leafIndex].length();
            leafStartNewLineCount -= this._leafs[leafIndex].newLineCount();
        }
    };
    Buffer.prototype.convertOffsetToPosition = function (offset) {
        var r = BufferCursorPool.take();
        var lineStart = BufferCursorPool.take();
        if (!this._findOffset(offset, r)) {
            BufferCursorPool.put(r);
            BufferCursorPool.put(lineStart);
            throw new Error("Offset not found");
        }
        var lineNumber = this._findLineStartBeforeOffset(offset, r, lineStart);
        var column = offset - lineStart.offset + 1;
        BufferCursorPool.put(r);
        BufferCursorPool.put(lineStart);
        return new Position(lineNumber, column);
    };
    Buffer.prototype.convertOffsetLenToRange = function (offset, len) {
        var r = BufferCursorPool.take();
        var lineStart = BufferCursorPool.take();
        if (!this._findOffset(offset, r)) {
            BufferCursorPool.put(r);
            BufferCursorPool.put(lineStart);
            throw new Error("Offset not found");
        }
        var startLineNumber = this._findLineStartBeforeOffset(offset, r, lineStart);
        var startColumn = offset - lineStart.offset + 1;
        if (!this._findOffset(offset + len, r)) {
            BufferCursorPool.put(r);
            BufferCursorPool.put(lineStart);
            throw new Error("Offset not found");
        }
        var endLineNumber = this._findLineStartBeforeOffset(offset + len, r, lineStart);
        var endColumn = offset + len - lineStart.offset + 1;
        BufferCursorPool.put(r);
        BufferCursorPool.put(lineStart);
        return new Range(startLineNumber, startColumn, endLineNumber, endColumn);
    };
    Buffer.prototype.getValueInRange = function (range) {
        var start = BufferCursorPool.take();
        if (!this._getOffsetAt(range.startLineNumber, range.startColumn, start)) {
            BufferCursorPool.put(start);
            throw new Error("Line not found");
        }
        var endOffset = this.convertPositionToOffset(range.endLineNumber, range.endColumn);
        var result = this.extractString(start, endOffset - start.offset);
        BufferCursorPool.put(start);
        return result;
    };
    Buffer.prototype.createSnapshot = function (BOM) {
        return new BufferSnapshot(this._leafs, BOM);
    };
    Buffer.prototype.getValueLengthInRange = function (range) {
        var startOffset = this.convertPositionToOffset(range.startLineNumber, range.startColumn);
        var endOffset = this.convertPositionToOffset(range.endLineNumber, range.endColumn);
        return endOffset - startOffset;
    };
    //#region Editing
    Buffer.prototype._mergeAdjacentEdits = function (edits) {
        // Check if we must merge adjacent edits
        var merged = [], mergedLength = 0;
        var prev = edits[0];
        for (var i = 1, len = edits.length; i < len; i++) {
            var curr = edits[i];
            if (prev.offset + prev.length === curr.offset) {
                // merge into `prev`
                prev.length = prev.length + curr.length;
                prev.text = prev.text + curr.text;
            }
            else {
                merged[mergedLength++] = prev;
                prev = curr;
            }
        }
        merged[mergedLength++] = prev;
        return merged;
    };
    Buffer.prototype._resolveEdits = function (edits) {
        edits = this._mergeAdjacentEdits(edits);
        var result = [];
        var tmp = new BufferCursor(0, 0, 0, 0);
        var tmp2 = new BufferCursor(0, 0, 0, 0);
        for (var i = 0, len = edits.length; i < len; i++) {
            var edit = edits[i];
            var text = edit.text;
            this._findOffset(edit.offset, tmp);
            var startLeafIndex = tmp.leafIndex;
            var startInnerOffset = tmp.offset - tmp.leafStartOffset;
            if (startInnerOffset > 0) {
                var startLeaf = this._leafs[startLeafIndex];
                var charBefore = startLeaf.charCodeAt(startInnerOffset - 1);
                if (charBefore === 13 /* CarriageReturn */) {
                    // include the replacement of \r in the edit
                    text = '\r' + text;
                    this._findOffsetCloseAfter(edit.offset - 1, tmp, tmp2);
                    startLeafIndex = tmp2.leafIndex;
                    startInnerOffset = tmp2.offset - tmp2.leafStartOffset;
                    // this._findOffset(edit.offset - 1, tmp);
                    // startLeafIndex = tmp.leafIndex;
                    // startInnerOffset = tmp.offset - tmp.leafStartOffset;
                }
            }
            this._findOffset(edit.offset + edit.length, tmp);
            var endLeafIndex = tmp.leafIndex;
            var endInnerOffset = tmp.offset - tmp.leafStartOffset;
            var endLeaf = this._leafs[endLeafIndex];
            if (endInnerOffset < endLeaf.length()) {
                var charAfter = endLeaf.charCodeAt(endInnerOffset);
                if (charAfter === 10 /* LineFeed */) {
                    // include the replacement of \n in the edit
                    text = text + '\n';
                    this._findOffsetCloseAfter(edit.offset + edit.length + 1, tmp, tmp2);
                    endLeafIndex = tmp2.leafIndex;
                    endInnerOffset = tmp2.offset - tmp2.leafStartOffset;
                    // this._findOffset(edit.offset + edit.length + 1, tmp);
                    // endLeafIndex = tmp.leafIndex;
                    // endInnerOffset = tmp.offset - tmp.leafStartOffset;
                }
            }
            result[i] = new InternalOffsetLenEdit(startLeafIndex, startInnerOffset, endLeafIndex, endInnerOffset, text);
        }
        return result;
    };
    Buffer.prototype._pushLeafReplacement = function (startLeafIndex, endLeafIndex, replacements) {
        var res = new LeafReplacement(startLeafIndex, endLeafIndex, []);
        replacements.push(res);
        return res;
    };
    Buffer.prototype._flushLeafEdits = function (accumulatedLeafIndex, accumulatedLeafEdits, replacements) {
        if (accumulatedLeafEdits.length > 0) {
            var rep = this._pushLeafReplacement(accumulatedLeafIndex, accumulatedLeafIndex, replacements);
            BufferPiece.replaceOffsetLen(this._leafs[accumulatedLeafIndex], accumulatedLeafEdits, this._idealLeafLength, this._maxLeafLength, rep.replacements);
        }
        accumulatedLeafEdits.length = 0;
    };
    Buffer.prototype._pushLeafEdits = function (start, length, text, accumulatedLeafEdits) {
        if (length !== 0 || text.length !== 0) {
            accumulatedLeafEdits.push(new LeafOffsetLenEdit(start, length, text));
        }
    };
    Buffer.prototype._appendLeaf = function (leaf, leafs, prevLeaf) {
        if (prevLeaf === null) {
            leafs.push(leaf);
            prevLeaf = leaf;
            return prevLeaf;
        }
        var prevLeafLength = prevLeaf.length();
        var currLeafLength = leaf.length();
        if ((prevLeafLength < this._minLeafLength || currLeafLength < this._minLeafLength) && prevLeafLength + currLeafLength <= this._maxLeafLength) {
            var joinedLeaf = BufferPiece.join(prevLeaf, leaf);
            leafs[leafs.length - 1] = joinedLeaf;
            prevLeaf = joinedLeaf;
            return prevLeaf;
        }
        var lastChar = prevLeaf.charCodeAt(prevLeafLength - 1);
        var firstChar = leaf.charCodeAt(0);
        if ((lastChar >= 0xd800 && lastChar <= 0xdbff) || (lastChar === 13 /* CarriageReturn */ && firstChar === 10 /* LineFeed */)) {
            var modifiedPrevLeaf = BufferPiece.deleteLastChar(prevLeaf);
            leafs[leafs.length - 1] = modifiedPrevLeaf;
            var modifiedLeaf = BufferPiece.insertFirstChar(leaf, lastChar);
            leaf = modifiedLeaf;
        }
        leafs.push(leaf);
        prevLeaf = leaf;
        return prevLeaf;
    };
    Buffer._compareEdits = function (a, b) {
        if (a.offset === b.offset) {
            if (a.length === b.length) {
                return (a.initialIndex - b.initialIndex);
            }
            return (a.length - b.length);
        }
        return a.offset - b.offset;
    };
    Buffer.prototype.replaceOffsetLen = function (_edits) {
        _edits.sort(Buffer._compareEdits);
        var initialLeafLength = this._leafs.length;
        var edits = this._resolveEdits(_edits);
        var accumulatedLeafIndex = 0;
        var accumulatedLeafEdits = [];
        var replacements = [];
        for (var i = 0, len = edits.length; i < len; i++) {
            var edit = edits[i];
            var startLeafIndex = edit.startLeafIndex;
            var endLeafIndex = edit.endLeafIndex;
            if (startLeafIndex !== accumulatedLeafIndex) {
                this._flushLeafEdits(accumulatedLeafIndex, accumulatedLeafEdits, replacements);
                accumulatedLeafIndex = startLeafIndex;
            }
            var leafEditStart = edit.startInnerOffset;
            var leafEditEnd = (startLeafIndex === endLeafIndex ? edit.endInnerOffset : this._leafs[startLeafIndex].length());
            this._pushLeafEdits(leafEditStart, leafEditEnd - leafEditStart, edit.text, accumulatedLeafEdits);
            if (startLeafIndex < endLeafIndex) {
                this._flushLeafEdits(accumulatedLeafIndex, accumulatedLeafEdits, replacements);
                accumulatedLeafIndex = endLeafIndex;
                // delete leafs in the middle
                if (startLeafIndex + 1 < endLeafIndex) {
                    this._pushLeafReplacement(startLeafIndex + 1, endLeafIndex - 1, replacements);
                }
                // delete on last leaf
                var leafEditStart_1 = 0;
                var leafEditEnd_1 = edit.endInnerOffset;
                this._pushLeafEdits(leafEditStart_1, leafEditEnd_1 - leafEditStart_1, '', accumulatedLeafEdits);
            }
        }
        this._flushLeafEdits(accumulatedLeafIndex, accumulatedLeafEdits, replacements);
        var leafs = [];
        var leafIndex = 0;
        var prevLeaf = null;
        for (var i = 0, len = replacements.length; i < len; i++) {
            var replaceStartLeafIndex = replacements[i].startLeafIndex;
            var replaceEndLeafIndex = replacements[i].endLeafIndex;
            var innerLeafs = replacements[i].replacements;
            // add leafs to the left of this replace op.
            while (leafIndex < replaceStartLeafIndex) {
                prevLeaf = this._appendLeaf(this._leafs[leafIndex], leafs, prevLeaf);
                leafIndex++;
            }
            // delete leafs that get replaced.
            while (leafIndex <= replaceEndLeafIndex) {
                leafIndex++;
            }
            // add new leafs.
            for (var j = 0, lenJ = innerLeafs.length; j < lenJ; j++) {
                prevLeaf = this._appendLeaf(innerLeafs[j], leafs, prevLeaf);
            }
        }
        // add remaining leafs to the right of the last replacement.
        while (leafIndex < initialLeafLength) {
            prevLeaf = this._appendLeaf(this._leafs[leafIndex], leafs, prevLeaf);
            leafIndex++;
        }
        if (leafs.length === 0) {
            // don't leave behind an empty leafs array
            leafs.push(new BufferPiece(''));
        }
        this._leafs = leafs;
        this._rebuildNodes();
    };
    Buffer.prototype.setEOL = function (newEOL) {
        var leafs = [];
        for (var i = 0, len = this._leafs.length; i < len; i++) {
            leafs[i] = BufferPiece.normalizeEOL(this._leafs[i], newEOL);
        }
        this._leafs = leafs;
        this._rebuildNodes();
        this._eol = newEOL;
        this._eolLength = this._eol.length;
    };
    //#endregion
    Buffer.prototype.IS_NODE = function (i) {
        return (i < this._nodesCount);
    };
    Buffer.prototype.IS_LEAF = function (i) {
        return (i >= this._leafsStart && i < this._leafsEnd);
    };
    Buffer.prototype.NODE_TO_LEAF_INDEX = function (i) {
        return (i - this._leafsStart);
    };
    return Buffer;
}());
function log2(n) {
    var v = 1;
    for (var pow = 1;; pow++) {
        v = v << 1;
        if (v >= n) {
            return pow;
        }
    }
    // return -1;
}
function LEFT_CHILD(i) {
    return (i << 1);
}
function RIGHT_CHILD(i) {
    return (i << 1) + 1;
}
