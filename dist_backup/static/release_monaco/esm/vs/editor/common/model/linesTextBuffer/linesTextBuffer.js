/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { Range } from '../../core/range.js';
import { Position } from '../../core/position.js';
import * as strings from '../../../../base/common/strings.js';
import * as arrays from '../../../../base/common/arrays.js';
import { PrefixSumComputer } from '../../viewModel/prefixSumComputer.js';
import { EndOfLinePreference, ApplyEditsResult } from '../../model.js';
var LinesTextBufferSnapshot = /** @class */ (function () {
    function LinesTextBufferSnapshot(lines, eol, bom) {
        this._lines = lines;
        this._linesLength = this._lines.length;
        this._eol = eol;
        this._bom = bom;
        this._lineIndex = 0;
    }
    LinesTextBufferSnapshot.prototype.read = function () {
        if (this._lineIndex >= this._linesLength) {
            return null;
        }
        var result = null;
        if (this._lineIndex === 0) {
            result = this._bom + this._lines[this._lineIndex];
        }
        else {
            result = this._lines[this._lineIndex];
        }
        this._lineIndex++;
        if (this._lineIndex < this._linesLength) {
            result += this._eol;
        }
        return result;
    };
    return LinesTextBufferSnapshot;
}());
var LinesTextBuffer = /** @class */ (function () {
    function LinesTextBuffer(textSource) {
        this._lines = textSource.lines.slice(0);
        this._BOM = textSource.BOM;
        this._EOL = textSource.EOL;
        this._mightContainRTL = textSource.containsRTL;
        this._mightContainNonBasicASCII = !textSource.isBasicASCII;
        this._constructLineStarts();
    }
    LinesTextBuffer.prototype._constructLineStarts = function () {
        var eolLength = this._EOL.length;
        var linesLength = this._lines.length;
        var lineStartValues = new Uint32Array(linesLength);
        for (var i = 0; i < linesLength; i++) {
            lineStartValues[i] = this._lines[i].length + eolLength;
        }
        this._lineStarts = new PrefixSumComputer(lineStartValues);
    };
    LinesTextBuffer.prototype.equals = function (other) {
        if (!(other instanceof LinesTextBuffer)) {
            return false;
        }
        if (this._BOM !== other._BOM) {
            return false;
        }
        if (this._EOL !== other._EOL) {
            return false;
        }
        if (this._lines.length !== other._lines.length) {
            return false;
        }
        for (var i = 0, len = this._lines.length; i < len; i++) {
            if (this._lines[i] !== other._lines[i]) {
                return false;
            }
        }
        return true;
    };
    LinesTextBuffer.prototype.mightContainRTL = function () {
        return this._mightContainRTL;
    };
    LinesTextBuffer.prototype.mightContainNonBasicASCII = function () {
        return this._mightContainNonBasicASCII;
    };
    LinesTextBuffer.prototype.getBOM = function () {
        return this._BOM;
    };
    LinesTextBuffer.prototype.getEOL = function () {
        return this._EOL;
    };
    LinesTextBuffer.prototype.getOffsetAt = function (lineNumber, column) {
        return this._lineStarts.getAccumulatedValue(lineNumber - 2) + column - 1;
    };
    LinesTextBuffer.prototype.getPositionAt = function (offset) {
        offset = Math.floor(offset);
        offset = Math.max(0, offset);
        var out = this._lineStarts.getIndexOf(offset);
        var lineLength = this._lines[out.index].length;
        // Ensure we return a valid position
        return new Position(out.index + 1, Math.min(out.remainder + 1, lineLength + 1));
    };
    LinesTextBuffer.prototype.getRangeAt = function (offset, length) {
        var startResult = this._lineStarts.getIndexOf(offset);
        var startLineLength = this._lines[startResult.index].length;
        var startColumn = Math.min(startResult.remainder + 1, startLineLength + 1);
        var endResult = this._lineStarts.getIndexOf(offset + length);
        var endLineLength = this._lines[endResult.index].length;
        var endColumn = Math.min(endResult.remainder + 1, endLineLength + 1);
        return new Range(startResult.index + 1, startColumn, endResult.index + 1, endColumn);
    };
    LinesTextBuffer.prototype._getEndOfLine = function (eol) {
        switch (eol) {
            case EndOfLinePreference.LF:
                return '\n';
            case EndOfLinePreference.CRLF:
                return '\r\n';
            case EndOfLinePreference.TextDefined:
                return this.getEOL();
        }
        throw new Error('Unknown EOL preference');
    };
    LinesTextBuffer.prototype.getValueInRange = function (range, eol) {
        if (range.isEmpty()) {
            return '';
        }
        if (range.startLineNumber === range.endLineNumber) {
            return this._lines[range.startLineNumber - 1].substring(range.startColumn - 1, range.endColumn - 1);
        }
        var lineEnding = this._getEndOfLine(eol);
        var startLineIndex = range.startLineNumber - 1;
        var endLineIndex = range.endLineNumber - 1;
        var resultLines = [];
        resultLines.push(this._lines[startLineIndex].substring(range.startColumn - 1));
        for (var i = startLineIndex + 1; i < endLineIndex; i++) {
            resultLines.push(this._lines[i]);
        }
        resultLines.push(this._lines[endLineIndex].substring(0, range.endColumn - 1));
        return resultLines.join(lineEnding);
    };
    LinesTextBuffer.prototype.createSnapshot = function (preserveBOM) {
        return new LinesTextBufferSnapshot(this._lines.slice(0), this._EOL, preserveBOM ? this._BOM : '');
    };
    LinesTextBuffer.prototype.getValueLengthInRange = function (range, eol) {
        if (range.isEmpty()) {
            return 0;
        }
        if (range.startLineNumber === range.endLineNumber) {
            return (range.endColumn - range.startColumn);
        }
        var startOffset = this.getOffsetAt(range.startLineNumber, range.startColumn);
        var endOffset = this.getOffsetAt(range.endLineNumber, range.endColumn);
        return endOffset - startOffset;
    };
    LinesTextBuffer.prototype.getLineCount = function () {
        return this._lines.length;
    };
    LinesTextBuffer.prototype.getLinesContent = function () {
        return this._lines.slice(0);
    };
    LinesTextBuffer.prototype.getLength = function () {
        return this._lineStarts.getTotalValue();
    };
    LinesTextBuffer.prototype.getLineContent = function (lineNumber) {
        return this._lines[lineNumber - 1];
    };
    LinesTextBuffer.prototype.getLineCharCode = function (lineNumber, index) {
        return this._lines[lineNumber - 1].charCodeAt(index);
    };
    LinesTextBuffer.prototype.getLineLength = function (lineNumber) {
        return this._lines[lineNumber - 1].length;
    };
    LinesTextBuffer.prototype.getLineFirstNonWhitespaceColumn = function (lineNumber) {
        var result = strings.firstNonWhitespaceIndex(this._lines[lineNumber - 1]);
        if (result === -1) {
            return 0;
        }
        return result + 1;
    };
    LinesTextBuffer.prototype.getLineLastNonWhitespaceColumn = function (lineNumber) {
        var result = strings.lastNonWhitespaceIndex(this._lines[lineNumber - 1]);
        if (result === -1) {
            return 0;
        }
        return result + 2;
    };
    //#region Editing
    LinesTextBuffer.prototype.setEOL = function (newEOL) {
        this._EOL = newEOL;
        this._constructLineStarts();
    };
    LinesTextBuffer._sortOpsAscending = function (a, b) {
        var r = Range.compareRangesUsingEnds(a.range, b.range);
        if (r === 0) {
            return a.sortIndex - b.sortIndex;
        }
        return r;
    };
    LinesTextBuffer._sortOpsDescending = function (a, b) {
        var r = Range.compareRangesUsingEnds(a.range, b.range);
        if (r === 0) {
            return b.sortIndex - a.sortIndex;
        }
        return -r;
    };
    LinesTextBuffer.prototype.applyEdits = function (rawOperations, recordTrimAutoWhitespace) {
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
        operations.sort(LinesTextBuffer._sortOpsAscending);
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
        var reverseRanges = LinesTextBuffer._getInverseEditRanges(operations);
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
    LinesTextBuffer.prototype._reduceOperations = function (operations) {
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
    LinesTextBuffer.prototype._toSingleEditOperation = function (operations) {
        var forceMoveMarkers = false, firstEditRange = operations[0].range, lastEditRange = operations[operations.length - 1].range, entireEditRange = new Range(firstEditRange.startLineNumber, firstEditRange.startColumn, lastEditRange.endLineNumber, lastEditRange.endColumn), lastEndLineNumber = firstEditRange.startLineNumber, lastEndColumn = firstEditRange.startColumn, result = [];
        for (var i = 0, len = operations.length; i < len; i++) {
            var operation = operations[i], range = operation.range;
            forceMoveMarkers = forceMoveMarkers || operation.forceMoveMarkers;
            // (1) -- Push old text
            for (var lineNumber = lastEndLineNumber; lineNumber < range.startLineNumber; lineNumber++) {
                if (lineNumber === lastEndLineNumber) {
                    result.push(this._lines[lineNumber - 1].substring(lastEndColumn - 1));
                }
                else {
                    result.push('\n');
                    result.push(this._lines[lineNumber - 1]);
                }
            }
            if (range.startLineNumber === lastEndLineNumber) {
                result.push(this._lines[range.startLineNumber - 1].substring(lastEndColumn - 1, range.startColumn - 1));
            }
            else {
                result.push('\n');
                result.push(this._lines[range.startLineNumber - 1].substring(0, range.startColumn - 1));
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
    LinesTextBuffer.prototype._setLineContent = function (lineNumber, content) {
        this._lines[lineNumber - 1] = content;
        this._lineStarts.changeValue(lineNumber - 1, content.length + this._EOL.length);
    };
    LinesTextBuffer.prototype._doApplyEdits = function (operations) {
        // Sort operations descending
        operations.sort(LinesTextBuffer._sortOpsDescending);
        var contentChanges = [];
        for (var i = 0, len = operations.length; i < len; i++) {
            var op = operations[i];
            var startLineNumber = op.range.startLineNumber;
            var startColumn = op.range.startColumn;
            var endLineNumber = op.range.endLineNumber;
            var endColumn = op.range.endColumn;
            if (startLineNumber === endLineNumber && startColumn === endColumn && (!op.lines || op.lines.length === 0)) {
                // no-op
                continue;
            }
            var deletingLinesCnt = endLineNumber - startLineNumber;
            var insertingLinesCnt = (op.lines ? op.lines.length - 1 : 0);
            var editingLinesCnt = Math.min(deletingLinesCnt, insertingLinesCnt);
            for (var j = editingLinesCnt; j >= 0; j--) {
                var editLineNumber = startLineNumber + j;
                var editText = (op.lines ? op.lines[j] : '');
                if (editLineNumber === startLineNumber || editLineNumber === endLineNumber) {
                    var editStartColumn = (editLineNumber === startLineNumber ? startColumn : 1);
                    var editEndColumn = (editLineNumber === endLineNumber ? endColumn : this.getLineLength(editLineNumber) + 1);
                    editText = (this._lines[editLineNumber - 1].substring(0, editStartColumn - 1)
                        + editText
                        + this._lines[editLineNumber - 1].substring(editEndColumn - 1));
                }
                this._setLineContent(editLineNumber, editText);
            }
            if (editingLinesCnt < deletingLinesCnt) {
                // Must delete some lines
                var spliceStartLineNumber = startLineNumber + editingLinesCnt;
                var endLineRemains = this._lines[endLineNumber - 1].substring(endColumn - 1);
                // Reconstruct first line
                this._setLineContent(spliceStartLineNumber, this._lines[spliceStartLineNumber - 1] + endLineRemains);
                this._lines.splice(spliceStartLineNumber, endLineNumber - spliceStartLineNumber);
                this._lineStarts.removeValues(spliceStartLineNumber, endLineNumber - spliceStartLineNumber);
            }
            if (editingLinesCnt < insertingLinesCnt) {
                // Must insert some lines
                var spliceLineNumber = startLineNumber + editingLinesCnt;
                var spliceColumn = (spliceLineNumber === startLineNumber ? startColumn : 1);
                if (op.lines) {
                    spliceColumn += op.lines[editingLinesCnt].length;
                }
                // Split last line
                var leftoverLine = this._lines[spliceLineNumber - 1].substring(spliceColumn - 1);
                this._setLineContent(spliceLineNumber, this._lines[spliceLineNumber - 1].substring(0, spliceColumn - 1));
                // Lines in the middle
                var newLines = new Array(insertingLinesCnt - editingLinesCnt);
                var newLinesLengths = new Uint32Array(insertingLinesCnt - editingLinesCnt);
                for (var j = editingLinesCnt + 1; j <= insertingLinesCnt; j++) {
                    newLines[j - editingLinesCnt - 1] = op.lines[j];
                    newLinesLengths[j - editingLinesCnt - 1] = op.lines[j].length + this._EOL.length;
                }
                newLines[newLines.length - 1] += leftoverLine;
                newLinesLengths[newLines.length - 1] += leftoverLine.length;
                this._lines = arrays.arrayInsert(this._lines, startLineNumber + editingLinesCnt, newLines);
                this._lineStarts.insertValues(startLineNumber + editingLinesCnt, newLinesLengths);
            }
            var contentChangeRange = new Range(startLineNumber, startColumn, endLineNumber, endColumn);
            var text = (op.lines ? op.lines.join(this.getEOL()) : '');
            contentChanges.push({
                range: contentChangeRange,
                rangeLength: op.rangeLength,
                text: text,
                rangeOffset: op.rangeOffset,
                forceMoveMarkers: op.forceMoveMarkers
            });
        }
        return contentChanges;
    };
    /**
     * Assumes `operations` are validated and sorted ascending
     */
    LinesTextBuffer._getInverseEditRanges = function (operations) {
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
    return LinesTextBuffer;
}());
export { LinesTextBuffer };
