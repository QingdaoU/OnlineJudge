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
import { onUnexpectedError } from '../../base/common/errors.js';
import { Emitter } from '../../base/common/event.js';
import { Disposable, dispose } from '../../base/common/lifecycle.js';
import { TPromise } from '../../base/common/winjs.base.js';
import { ServiceCollection } from '../../platform/instantiation/common/serviceCollection.js';
import { IContextKeyService } from '../../platform/contextkey/common/contextkey.js';
import { Cursor } from './controller/cursor.js';
import { CursorColumns } from './controller/cursorCommon.js';
import { Position } from './core/position.js';
import { Range } from './core/range.js';
import { Selection } from './core/selection.js';
import * as editorCommon from './editorCommon.js';
import { ViewModel } from './viewModel/viewModelImpl.js';
import { hash } from '../../base/common/hash.js';
import { EditorContextKeys } from './editorContextKeys.js';
import { ModelDecorationOptions } from './model/textModel.js';
import * as modes from './modes.js';
import { Schemas } from '../../base/common/network.js';
import { EndOfLinePreference } from './model.js';
var EDITOR_ID = 0;
var CommonCodeEditor = /** @class */ (function (_super) {
    __extends(CommonCodeEditor, _super);
    function CommonCodeEditor(domElement, options, instantiationService, contextKeyService) {
        var _this = _super.call(this) || this;
        _this._onDidDispose = _this._register(new Emitter());
        _this.onDidDispose = _this._onDidDispose.event;
        _this._onDidChangeModelContent = _this._register(new Emitter());
        _this.onDidChangeModelContent = _this._onDidChangeModelContent.event;
        _this._onDidChangeModelLanguage = _this._register(new Emitter());
        _this.onDidChangeModelLanguage = _this._onDidChangeModelLanguage.event;
        _this._onDidChangeModelLanguageConfiguration = _this._register(new Emitter());
        _this.onDidChangeModelLanguageConfiguration = _this._onDidChangeModelLanguageConfiguration.event;
        _this._onDidChangeModelOptions = _this._register(new Emitter());
        _this.onDidChangeModelOptions = _this._onDidChangeModelOptions.event;
        _this._onDidChangeModelDecorations = _this._register(new Emitter());
        _this.onDidChangeModelDecorations = _this._onDidChangeModelDecorations.event;
        _this._onDidChangeConfiguration = _this._register(new Emitter());
        _this.onDidChangeConfiguration = _this._onDidChangeConfiguration.event;
        _this._onDidChangeModel = _this._register(new Emitter());
        _this.onDidChangeModel = _this._onDidChangeModel.event;
        _this._onDidChangeCursorPosition = _this._register(new Emitter());
        _this.onDidChangeCursorPosition = _this._onDidChangeCursorPosition.event;
        _this._onDidChangeCursorSelection = _this._register(new Emitter());
        _this.onDidChangeCursorSelection = _this._onDidChangeCursorSelection.event;
        _this._onDidLayoutChange = _this._register(new Emitter());
        _this.onDidLayoutChange = _this._onDidLayoutChange.event;
        _this._onDidFocusEditorText = _this._register(new Emitter());
        _this.onDidFocusEditorText = _this._onDidFocusEditorText.event;
        _this._onDidBlurEditorText = _this._register(new Emitter());
        _this.onDidBlurEditorText = _this._onDidBlurEditorText.event;
        _this._onDidFocusEditor = _this._register(new Emitter());
        _this.onDidFocusEditor = _this._onDidFocusEditor.event;
        _this._onDidBlurEditor = _this._register(new Emitter());
        _this.onDidBlurEditor = _this._onDidBlurEditor.event;
        _this._onWillType = _this._register(new Emitter());
        _this.onWillType = _this._onWillType.event;
        _this._onDidType = _this._register(new Emitter());
        _this.onDidType = _this._onDidType.event;
        _this._onDidPaste = _this._register(new Emitter());
        _this.onDidPaste = _this._onDidPaste.event;
        _this.domElement = domElement;
        _this.id = (++EDITOR_ID);
        _this._decorationTypeKeysToIds = {};
        _this._decorationTypeSubtypes = {};
        options = options || {};
        _this._configuration = _this._register(_this._createConfiguration(options));
        _this._register(_this._configuration.onDidChange(function (e) {
            _this._onDidChangeConfiguration.fire(e);
            if (e.layoutInfo) {
                _this._onDidLayoutChange.fire(_this._configuration.editor.layoutInfo);
            }
        }));
        _this._contextKeyService = _this._register(contextKeyService.createScoped(_this.domElement));
        _this._register(new EditorContextKeysManager(_this, _this._contextKeyService));
        _this._register(new EditorModeContext(_this, _this._contextKeyService));
        _this._instantiationService = instantiationService.createChild(new ServiceCollection([IContextKeyService, _this._contextKeyService]));
        _this._attachModel(null);
        _this._contributions = {};
        _this._actions = {};
        return _this;
    }
    CommonCodeEditor.prototype.getId = function () {
        return this.getEditorType() + ':' + this.id;
    };
    CommonCodeEditor.prototype.getEditorType = function () {
        return editorCommon.EditorType.ICodeEditor;
    };
    CommonCodeEditor.prototype.dispose = function () {
        var keys = Object.keys(this._contributions);
        for (var i = 0, len = keys.length; i < len; i++) {
            var contributionId = keys[i];
            this._contributions[contributionId].dispose();
        }
        this._contributions = {};
        // editor actions don't need to be disposed
        this._actions = {};
        this._removeDecorationTypes();
        this._postDetachModelCleanup(this._detachModel());
        this._onDidDispose.fire();
        _super.prototype.dispose.call(this);
    };
    CommonCodeEditor.prototype.invokeWithinContext = function (fn) {
        return this._instantiationService.invokeFunction(fn);
    };
    CommonCodeEditor.prototype.updateOptions = function (newOptions) {
        this._configuration.updateOptions(newOptions);
    };
    CommonCodeEditor.prototype.getConfiguration = function () {
        return this._configuration.editor;
    };
    CommonCodeEditor.prototype.getRawConfiguration = function () {
        return this._configuration.getRawOptions();
    };
    CommonCodeEditor.prototype.getValue = function (options) {
        if (options === void 0) { options = null; }
        if (this.model) {
            var preserveBOM = (options && options.preserveBOM) ? true : false;
            var eolPreference = EndOfLinePreference.TextDefined;
            if (options && options.lineEnding && options.lineEnding === '\n') {
                eolPreference = EndOfLinePreference.LF;
            }
            else if (options && options.lineEnding && options.lineEnding === '\r\n') {
                eolPreference = EndOfLinePreference.CRLF;
            }
            return this.model.getValue(eolPreference, preserveBOM);
        }
        return '';
    };
    CommonCodeEditor.prototype.setValue = function (newValue) {
        if (this.model) {
            this.model.setValue(newValue);
        }
    };
    CommonCodeEditor.prototype.getModel = function () {
        return this.model;
    };
    CommonCodeEditor.prototype.setModel = function (model) {
        if (model === void 0) { model = null; }
        if (this.model === model) {
            // Current model is the new model
            return;
        }
        var detachedModel = this._detachModel();
        this._attachModel(model);
        var e = {
            oldModelUrl: detachedModel ? detachedModel.uri : null,
            newModelUrl: model ? model.uri : null
        };
        this._removeDecorationTypes();
        this._onDidChangeModel.fire(e);
        this._postDetachModelCleanup(detachedModel);
    };
    CommonCodeEditor.prototype._removeDecorationTypes = function () {
        this._decorationTypeKeysToIds = {};
        if (this._decorationTypeSubtypes) {
            for (var decorationType in this._decorationTypeSubtypes) {
                var subTypes = this._decorationTypeSubtypes[decorationType];
                for (var subType in subTypes) {
                    this._removeDecorationType(decorationType + '-' + subType);
                }
            }
            this._decorationTypeSubtypes = {};
        }
    };
    CommonCodeEditor.prototype.getCenteredRangeInViewport = function () {
        if (!this.hasView) {
            return null;
        }
        return this.viewModel.getCenteredRangeInViewport();
    };
    CommonCodeEditor.prototype.getVisibleRanges = function () {
        if (!this.hasView) {
            return [];
        }
        return this.viewModel.getVisibleRanges();
    };
    CommonCodeEditor.prototype.getWhitespaces = function () {
        if (!this.hasView) {
            return [];
        }
        return this.viewModel.viewLayout.getWhitespaces();
    };
    CommonCodeEditor.prototype._getVerticalOffsetForPosition = function (modelLineNumber, modelColumn) {
        var modelPosition = this.model.validatePosition({
            lineNumber: modelLineNumber,
            column: modelColumn
        });
        var viewPosition = this.viewModel.coordinatesConverter.convertModelPositionToViewPosition(modelPosition);
        return this.viewModel.viewLayout.getVerticalOffsetForLineNumber(viewPosition.lineNumber);
    };
    CommonCodeEditor.prototype.getTopForLineNumber = function (lineNumber) {
        if (!this.hasView) {
            return -1;
        }
        return this._getVerticalOffsetForPosition(lineNumber, 1);
    };
    CommonCodeEditor.prototype.getTopForPosition = function (lineNumber, column) {
        if (!this.hasView) {
            return -1;
        }
        return this._getVerticalOffsetForPosition(lineNumber, column);
    };
    CommonCodeEditor.prototype.setHiddenAreas = function (ranges) {
        if (this.viewModel) {
            this.viewModel.setHiddenAreas(ranges.map(function (r) { return Range.lift(r); }));
        }
    };
    CommonCodeEditor.prototype.getVisibleColumnFromPosition = function (rawPosition) {
        if (!this.model) {
            return rawPosition.column;
        }
        var position = this.model.validatePosition(rawPosition);
        var tabSize = this.model.getOptions().tabSize;
        return CursorColumns.visibleColumnFromColumn(this.model.getLineContent(position.lineNumber), position.column, tabSize) + 1;
    };
    CommonCodeEditor.prototype.getPosition = function () {
        if (!this.cursor) {
            return null;
        }
        return this.cursor.getPosition().clone();
    };
    CommonCodeEditor.prototype.setPosition = function (position) {
        if (!this.cursor) {
            return;
        }
        if (!Position.isIPosition(position)) {
            throw new Error('Invalid arguments');
        }
        this.cursor.setSelections('api', [{
                selectionStartLineNumber: position.lineNumber,
                selectionStartColumn: position.column,
                positionLineNumber: position.lineNumber,
                positionColumn: position.column
            }]);
    };
    CommonCodeEditor.prototype._sendRevealRange = function (modelRange, verticalType, revealHorizontal, scrollType) {
        if (!this.model || !this.cursor) {
            return;
        }
        if (!Range.isIRange(modelRange)) {
            throw new Error('Invalid arguments');
        }
        var validatedModelRange = this.model.validateRange(modelRange);
        var viewRange = this.viewModel.coordinatesConverter.convertModelRangeToViewRange(validatedModelRange);
        this.cursor.emitCursorRevealRange(viewRange, verticalType, revealHorizontal, scrollType);
    };
    CommonCodeEditor.prototype.revealLine = function (lineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLine(lineNumber, 0 /* Simple */, scrollType);
    };
    CommonCodeEditor.prototype.revealLineInCenter = function (lineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLine(lineNumber, 1 /* Center */, scrollType);
    };
    CommonCodeEditor.prototype.revealLineInCenterIfOutsideViewport = function (lineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLine(lineNumber, 2 /* CenterIfOutsideViewport */, scrollType);
    };
    CommonCodeEditor.prototype._revealLine = function (lineNumber, revealType, scrollType) {
        if (typeof lineNumber !== 'number') {
            throw new Error('Invalid arguments');
        }
        this._sendRevealRange(new Range(lineNumber, 1, lineNumber, 1), revealType, false, scrollType);
    };
    CommonCodeEditor.prototype.revealPosition = function (position, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealPosition(position, 0 /* Simple */, true, scrollType);
    };
    CommonCodeEditor.prototype.revealPositionInCenter = function (position, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealPosition(position, 1 /* Center */, true, scrollType);
    };
    CommonCodeEditor.prototype.revealPositionInCenterIfOutsideViewport = function (position, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealPosition(position, 2 /* CenterIfOutsideViewport */, true, scrollType);
    };
    CommonCodeEditor.prototype._revealPosition = function (position, verticalType, revealHorizontal, scrollType) {
        if (!Position.isIPosition(position)) {
            throw new Error('Invalid arguments');
        }
        this._sendRevealRange(new Range(position.lineNumber, position.column, position.lineNumber, position.column), verticalType, revealHorizontal, scrollType);
    };
    CommonCodeEditor.prototype.getSelection = function () {
        if (!this.cursor) {
            return null;
        }
        return this.cursor.getSelection().clone();
    };
    CommonCodeEditor.prototype.getSelections = function () {
        if (!this.cursor) {
            return null;
        }
        var selections = this.cursor.getSelections();
        var result = [];
        for (var i = 0, len = selections.length; i < len; i++) {
            result[i] = selections[i].clone();
        }
        return result;
    };
    CommonCodeEditor.prototype.setSelection = function (something) {
        var isSelection = Selection.isISelection(something);
        var isRange = Range.isIRange(something);
        if (!isSelection && !isRange) {
            throw new Error('Invalid arguments');
        }
        if (isSelection) {
            this._setSelectionImpl(something);
        }
        else if (isRange) {
            // act as if it was an IRange
            var selection = {
                selectionStartLineNumber: something.startLineNumber,
                selectionStartColumn: something.startColumn,
                positionLineNumber: something.endLineNumber,
                positionColumn: something.endColumn
            };
            this._setSelectionImpl(selection);
        }
    };
    CommonCodeEditor.prototype._setSelectionImpl = function (sel) {
        if (!this.cursor) {
            return;
        }
        var selection = new Selection(sel.selectionStartLineNumber, sel.selectionStartColumn, sel.positionLineNumber, sel.positionColumn);
        this.cursor.setSelections('api', [selection]);
    };
    CommonCodeEditor.prototype.revealLines = function (startLineNumber, endLineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLines(startLineNumber, endLineNumber, 0 /* Simple */, scrollType);
    };
    CommonCodeEditor.prototype.revealLinesInCenter = function (startLineNumber, endLineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLines(startLineNumber, endLineNumber, 1 /* Center */, scrollType);
    };
    CommonCodeEditor.prototype.revealLinesInCenterIfOutsideViewport = function (startLineNumber, endLineNumber, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealLines(startLineNumber, endLineNumber, 2 /* CenterIfOutsideViewport */, scrollType);
    };
    CommonCodeEditor.prototype._revealLines = function (startLineNumber, endLineNumber, verticalType, scrollType) {
        if (typeof startLineNumber !== 'number' || typeof endLineNumber !== 'number') {
            throw new Error('Invalid arguments');
        }
        this._sendRevealRange(new Range(startLineNumber, 1, endLineNumber, 1), verticalType, false, scrollType);
    };
    CommonCodeEditor.prototype.revealRange = function (range, scrollType, revealVerticalInCenter, revealHorizontal) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        if (revealVerticalInCenter === void 0) { revealVerticalInCenter = false; }
        if (revealHorizontal === void 0) { revealHorizontal = true; }
        this._revealRange(range, revealVerticalInCenter ? 1 /* Center */ : 0 /* Simple */, revealHorizontal, scrollType);
    };
    CommonCodeEditor.prototype.revealRangeInCenter = function (range, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealRange(range, 1 /* Center */, true, scrollType);
    };
    CommonCodeEditor.prototype.revealRangeInCenterIfOutsideViewport = function (range, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealRange(range, 2 /* CenterIfOutsideViewport */, true, scrollType);
    };
    CommonCodeEditor.prototype.revealRangeAtTop = function (range, scrollType) {
        if (scrollType === void 0) { scrollType = 0 /* Smooth */; }
        this._revealRange(range, 3 /* Top */, true, scrollType);
    };
    CommonCodeEditor.prototype._revealRange = function (range, verticalType, revealHorizontal, scrollType) {
        if (!Range.isIRange(range)) {
            throw new Error('Invalid arguments');
        }
        this._sendRevealRange(Range.lift(range), verticalType, revealHorizontal, scrollType);
    };
    CommonCodeEditor.prototype.setSelections = function (ranges) {
        if (!this.cursor) {
            return;
        }
        if (!ranges || ranges.length === 0) {
            throw new Error('Invalid arguments');
        }
        for (var i = 0, len = ranges.length; i < len; i++) {
            if (!Selection.isISelection(ranges[i])) {
                throw new Error('Invalid arguments');
            }
        }
        this.cursor.setSelections('api', ranges);
    };
    CommonCodeEditor.prototype.getScrollWidth = function () {
        if (!this.hasView) {
            return -1;
        }
        return this.viewModel.viewLayout.getScrollWidth();
    };
    CommonCodeEditor.prototype.getScrollLeft = function () {
        if (!this.hasView) {
            return -1;
        }
        return this.viewModel.viewLayout.getCurrentScrollLeft();
    };
    CommonCodeEditor.prototype.getScrollHeight = function () {
        if (!this.hasView) {
            return -1;
        }
        return this.viewModel.viewLayout.getScrollHeight();
    };
    CommonCodeEditor.prototype.getScrollTop = function () {
        if (!this.hasView) {
            return -1;
        }
        return this.viewModel.viewLayout.getCurrentScrollTop();
    };
    CommonCodeEditor.prototype.setScrollLeft = function (newScrollLeft) {
        if (!this.hasView) {
            return;
        }
        if (typeof newScrollLeft !== 'number') {
            throw new Error('Invalid arguments');
        }
        this.viewModel.viewLayout.setScrollPositionNow({
            scrollLeft: newScrollLeft
        });
    };
    CommonCodeEditor.prototype.setScrollTop = function (newScrollTop) {
        if (!this.hasView) {
            return;
        }
        if (typeof newScrollTop !== 'number') {
            throw new Error('Invalid arguments');
        }
        this.viewModel.viewLayout.setScrollPositionNow({
            scrollTop: newScrollTop
        });
    };
    CommonCodeEditor.prototype.setScrollPosition = function (position) {
        if (!this.hasView) {
            return;
        }
        this.viewModel.viewLayout.setScrollPositionNow(position);
    };
    CommonCodeEditor.prototype.saveViewState = function () {
        if (!this.cursor || !this.hasView) {
            return null;
        }
        var contributionsState = {};
        var keys = Object.keys(this._contributions);
        for (var i = 0, len = keys.length; i < len; i++) {
            var id = keys[i];
            var contribution = this._contributions[id];
            if (typeof contribution.saveViewState === 'function') {
                contributionsState[id] = contribution.saveViewState();
            }
        }
        var cursorState = this.cursor.saveState();
        var viewState = this.viewModel.viewLayout.saveState();
        return {
            cursorState: cursorState,
            viewState: viewState,
            contributionsState: contributionsState
        };
    };
    CommonCodeEditor.prototype.restoreViewState = function (s) {
        if (!this.cursor || !this.hasView) {
            return;
        }
        if (s && s.cursorState && s.viewState) {
            var codeEditorState = s;
            var cursorState = codeEditorState.cursorState;
            if (Array.isArray(cursorState)) {
                this.cursor.restoreState(cursorState);
            }
            else {
                // Backwards compatibility
                this.cursor.restoreState([cursorState]);
            }
            var contributionsState = s.contributionsState || {};
            var keys = Object.keys(this._contributions);
            for (var i = 0, len = keys.length; i < len; i++) {
                var id = keys[i];
                var contribution = this._contributions[id];
                if (typeof contribution.restoreViewState === 'function') {
                    contribution.restoreViewState(contributionsState[id]);
                }
            }
        }
    };
    CommonCodeEditor.prototype.onVisible = function () {
    };
    CommonCodeEditor.prototype.onHide = function () {
    };
    CommonCodeEditor.prototype.getContribution = function (id) {
        return (this._contributions[id] || null);
    };
    CommonCodeEditor.prototype.getActions = function () {
        var result = [];
        var keys = Object.keys(this._actions);
        for (var i = 0, len = keys.length; i < len; i++) {
            var id = keys[i];
            result.push(this._actions[id]);
        }
        return result;
    };
    CommonCodeEditor.prototype.getSupportedActions = function () {
        var result = this.getActions();
        result = result.filter(function (action) { return action.isSupported(); });
        return result;
    };
    CommonCodeEditor.prototype.getAction = function (id) {
        return this._actions[id] || null;
    };
    CommonCodeEditor.prototype.trigger = function (source, handlerId, payload) {
        payload = payload || {};
        // Special case for typing
        if (handlerId === editorCommon.Handler.Type) {
            if (!this.cursor || typeof payload.text !== 'string' || payload.text.length === 0) {
                // nothing to do
                return;
            }
            if (source === 'keyboard') {
                this._onWillType.fire(payload.text);
            }
            this.cursor.trigger(source, handlerId, payload);
            if (source === 'keyboard') {
                this._onDidType.fire(payload.text);
            }
            return;
        }
        // Special case for pasting
        if (handlerId === editorCommon.Handler.Paste) {
            if (!this.cursor || typeof payload.text !== 'string' || payload.text.length === 0) {
                // nothing to do
                return;
            }
            var startPosition = this.cursor.getSelection().getStartPosition();
            this.cursor.trigger(source, handlerId, payload);
            var endPosition = this.cursor.getSelection().getStartPosition();
            if (source === 'keyboard') {
                this._onDidPaste.fire(new Range(startPosition.lineNumber, startPosition.column, endPosition.lineNumber, endPosition.column));
            }
            return;
        }
        var action = this.getAction(handlerId);
        if (action) {
            TPromise.as(action.run()).then(null, onUnexpectedError);
            return;
        }
        if (!this.cursor) {
            return;
        }
        if (this._triggerEditorCommand(source, handlerId, payload)) {
            return;
        }
        this.cursor.trigger(source, handlerId, payload);
    };
    CommonCodeEditor.prototype._getCursors = function () {
        return this.cursor;
    };
    CommonCodeEditor.prototype._getCursorConfiguration = function () {
        return this.cursor.context.config;
    };
    CommonCodeEditor.prototype.pushUndoStop = function () {
        if (!this.model) {
            return false;
        }
        if (this._configuration.editor.readOnly) {
            // read only editor => sorry!
            return false;
        }
        this.model.pushStackElement();
        return true;
    };
    CommonCodeEditor.prototype.executeEdits = function (source, edits, endCursorState) {
        var _this = this;
        if (!this.cursor) {
            // no view, no cursor
            return false;
        }
        if (this._configuration.editor.readOnly) {
            // read only editor => sorry!
            return false;
        }
        this.model.pushEditOperations(this.cursor.getSelections(), edits, function () {
            return endCursorState ? endCursorState : _this.cursor.getSelections();
        });
        if (endCursorState) {
            this.cursor.setSelections(source, endCursorState);
        }
        return true;
    };
    CommonCodeEditor.prototype.executeCommand = function (source, command) {
        if (!this.cursor) {
            return;
        }
        this.cursor.trigger(source, editorCommon.Handler.ExecuteCommand, command);
    };
    CommonCodeEditor.prototype.executeCommands = function (source, commands) {
        if (!this.cursor) {
            return;
        }
        this.cursor.trigger(source, editorCommon.Handler.ExecuteCommands, commands);
    };
    CommonCodeEditor.prototype.changeDecorations = function (callback) {
        if (!this.model) {
            //			console.warn('Cannot change decorations on editor that is not attached to a model');
            // callback will not be called
            return null;
        }
        return this.model.changeDecorations(callback, this.id);
    };
    CommonCodeEditor.prototype.getLineDecorations = function (lineNumber) {
        if (!this.model) {
            return null;
        }
        return this.model.getLineDecorations(lineNumber, this.id, this._configuration.editor.readOnly);
    };
    CommonCodeEditor.prototype.deltaDecorations = function (oldDecorations, newDecorations) {
        if (!this.model) {
            return [];
        }
        if (oldDecorations.length === 0 && newDecorations.length === 0) {
            return oldDecorations;
        }
        return this.model.deltaDecorations(oldDecorations, newDecorations, this.id);
    };
    CommonCodeEditor.prototype.setDecorations = function (decorationTypeKey, decorationOptions) {
        var newDecorationsSubTypes = {};
        var oldDecorationsSubTypes = this._decorationTypeSubtypes[decorationTypeKey] || {};
        this._decorationTypeSubtypes[decorationTypeKey] = newDecorationsSubTypes;
        var newModelDecorations = [];
        for (var _i = 0, decorationOptions_1 = decorationOptions; _i < decorationOptions_1.length; _i++) {
            var decorationOption = decorationOptions_1[_i];
            var typeKey = decorationTypeKey;
            if (decorationOption.renderOptions) {
                // identify custom reder options by a hash code over all keys and values
                // For custom render options register a decoration type if necessary
                var subType = hash(decorationOption.renderOptions).toString(16);
                // The fact that `decorationTypeKey` appears in the typeKey has no influence
                // it is just a mechanism to get predictable and unique keys (repeatable for the same options and unique across clients)
                typeKey = decorationTypeKey + '-' + subType;
                if (!oldDecorationsSubTypes[subType] && !newDecorationsSubTypes[subType]) {
                    // decoration type did not exist before, register new one
                    this._registerDecorationType(typeKey, decorationOption.renderOptions, decorationTypeKey);
                }
                newDecorationsSubTypes[subType] = true;
            }
            var opts = this._resolveDecorationOptions(typeKey, !!decorationOption.hoverMessage);
            if (decorationOption.hoverMessage) {
                opts.hoverMessage = decorationOption.hoverMessage;
            }
            newModelDecorations.push({ range: decorationOption.range, options: opts });
        }
        // remove decoration sub types that are no longer used, deregister decoration type if necessary
        for (var subType in oldDecorationsSubTypes) {
            if (!newDecorationsSubTypes[subType]) {
                this._removeDecorationType(decorationTypeKey + '-' + subType);
            }
        }
        // update all decorations
        var oldDecorationsIds = this._decorationTypeKeysToIds[decorationTypeKey] || [];
        this._decorationTypeKeysToIds[decorationTypeKey] = this.deltaDecorations(oldDecorationsIds, newModelDecorations);
    };
    CommonCodeEditor.prototype.setDecorationsFast = function (decorationTypeKey, ranges) {
        // remove decoration sub types that are no longer used, deregister decoration type if necessary
        var oldDecorationsSubTypes = this._decorationTypeSubtypes[decorationTypeKey] || {};
        for (var subType in oldDecorationsSubTypes) {
            this._removeDecorationType(decorationTypeKey + '-' + subType);
        }
        this._decorationTypeSubtypes[decorationTypeKey] = {};
        var opts = ModelDecorationOptions.createDynamic(this._resolveDecorationOptions(decorationTypeKey, false));
        var newModelDecorations = new Array(ranges.length);
        for (var i = 0, len = ranges.length; i < len; i++) {
            newModelDecorations[i] = { range: ranges[i], options: opts };
        }
        // update all decorations
        var oldDecorationsIds = this._decorationTypeKeysToIds[decorationTypeKey] || [];
        this._decorationTypeKeysToIds[decorationTypeKey] = this.deltaDecorations(oldDecorationsIds, newModelDecorations);
    };
    CommonCodeEditor.prototype.removeDecorations = function (decorationTypeKey) {
        // remove decorations for type and sub type
        var oldDecorationsIds = this._decorationTypeKeysToIds[decorationTypeKey];
        if (oldDecorationsIds) {
            this.deltaDecorations(oldDecorationsIds, []);
        }
        if (this._decorationTypeKeysToIds.hasOwnProperty(decorationTypeKey)) {
            delete this._decorationTypeKeysToIds[decorationTypeKey];
        }
        if (this._decorationTypeSubtypes.hasOwnProperty(decorationTypeKey)) {
            delete this._decorationTypeSubtypes[decorationTypeKey];
        }
    };
    CommonCodeEditor.prototype.getLayoutInfo = function () {
        return this._configuration.editor.layoutInfo;
    };
    CommonCodeEditor.prototype._attachModel = function (model) {
        var _this = this;
        this.model = model ? model : null;
        this.listenersToRemove = [];
        this.viewModel = null;
        this.cursor = null;
        if (this.model) {
            this.domElement.setAttribute('data-mode-id', this.model.getLanguageIdentifier().language);
            this._configuration.setIsDominatedByLongLines(this.model.isDominatedByLongLines());
            this._configuration.setMaxLineNumber(this.model.getLineCount());
            this.model.onBeforeAttached();
            this.viewModel = new ViewModel(this.id, this._configuration, this.model, function (callback) { return _this._scheduleAtNextAnimationFrame(callback); });
            this.listenersToRemove.push(this.model.onDidChangeDecorations(function (e) { return _this._onDidChangeModelDecorations.fire(e); }));
            this.listenersToRemove.push(this.model.onDidChangeLanguage(function (e) {
                if (!_this.model) {
                    return;
                }
                _this.domElement.setAttribute('data-mode-id', _this.model.getLanguageIdentifier().language);
                _this._onDidChangeModelLanguage.fire(e);
            }));
            this.listenersToRemove.push(this.model.onDidChangeLanguageConfiguration(function (e) { return _this._onDidChangeModelLanguageConfiguration.fire(e); }));
            this.listenersToRemove.push(this.model.onDidChangeContent(function (e) { return _this._onDidChangeModelContent.fire(e); }));
            this.listenersToRemove.push(this.model.onDidChangeOptions(function (e) { return _this._onDidChangeModelOptions.fire(e); }));
            // Someone might destroy the model from under the editor, so prevent any exceptions by setting a null model
            this.listenersToRemove.push(this.model.onWillDispose(function () { return _this.setModel(null); }));
            this.cursor = new Cursor(this._configuration, this.model, this.viewModel);
            this._createView();
            this.listenersToRemove.push(this.cursor.onDidChange(function (e) {
                var positions = [];
                for (var i = 0, len = e.selections.length; i < len; i++) {
                    positions[i] = e.selections[i].getPosition();
                }
                var e1 = {
                    position: positions[0],
                    secondaryPositions: positions.slice(1),
                    reason: e.reason,
                    source: e.source
                };
                _this._onDidChangeCursorPosition.fire(e1);
                var e2 = {
                    selection: e.selections[0],
                    secondarySelections: e.selections.slice(1),
                    source: e.source,
                    reason: e.reason
                };
                _this._onDidChangeCursorSelection.fire(e2);
            }));
        }
        else {
            this.hasView = false;
        }
    };
    CommonCodeEditor.prototype._postDetachModelCleanup = function (detachedModel) {
        if (detachedModel) {
            detachedModel.removeAllDecorationsWithOwnerId(this.id);
        }
    };
    CommonCodeEditor.prototype._detachModel = function () {
        if (this.model) {
            this.model.onBeforeDetached();
        }
        this.hasView = false;
        this.listenersToRemove = dispose(this.listenersToRemove);
        if (this.cursor) {
            this.cursor.dispose();
            this.cursor = null;
        }
        if (this.viewModel) {
            this.viewModel.dispose();
            this.viewModel = null;
        }
        var result = this.model;
        this.model = null;
        this.domElement.removeAttribute('data-mode-id');
        return result;
    };
    /* __GDPR__FRAGMENT__
        "EditorTelemetryData" : {}
    */
    CommonCodeEditor.prototype.getTelemetryData = function () {
        return null;
    };
    return CommonCodeEditor;
}(Disposable));
export { CommonCodeEditor };
var EditorContextKeysManager = /** @class */ (function (_super) {
    __extends(EditorContextKeysManager, _super);
    function EditorContextKeysManager(editor, contextKeyService) {
        var _this = _super.call(this) || this;
        _this._editor = editor;
        contextKeyService.createKey('editorId', editor.getId());
        _this._editorFocus = EditorContextKeys.focus.bindTo(contextKeyService);
        _this._editorTextFocus = EditorContextKeys.textFocus.bindTo(contextKeyService);
        _this._editorTabMovesFocus = EditorContextKeys.tabMovesFocus.bindTo(contextKeyService);
        _this._editorReadonly = EditorContextKeys.readOnly.bindTo(contextKeyService);
        _this._hasMultipleSelections = EditorContextKeys.hasMultipleSelections.bindTo(contextKeyService);
        _this._hasNonEmptySelection = EditorContextKeys.hasNonEmptySelection.bindTo(contextKeyService);
        _this._register(_this._editor.onDidChangeConfiguration(function () { return _this._updateFromConfig(); }));
        _this._register(_this._editor.onDidChangeCursorSelection(function () { return _this._updateFromSelection(); }));
        _this._register(_this._editor.onDidFocusEditor(function () { return _this._updateFromFocus(); }));
        _this._register(_this._editor.onDidBlurEditor(function () { return _this._updateFromFocus(); }));
        _this._register(_this._editor.onDidFocusEditorText(function () { return _this._updateFromFocus(); }));
        _this._register(_this._editor.onDidBlurEditorText(function () { return _this._updateFromFocus(); }));
        _this._updateFromConfig();
        _this._updateFromSelection();
        _this._updateFromFocus();
        return _this;
    }
    EditorContextKeysManager.prototype._updateFromConfig = function () {
        var config = this._editor.getConfiguration();
        this._editorTabMovesFocus.set(config.tabFocusMode);
        this._editorReadonly.set(config.readOnly);
    };
    EditorContextKeysManager.prototype._updateFromSelection = function () {
        var selections = this._editor.getSelections();
        if (!selections) {
            this._hasMultipleSelections.reset();
            this._hasNonEmptySelection.reset();
        }
        else {
            this._hasMultipleSelections.set(selections.length > 1);
            this._hasNonEmptySelection.set(selections.some(function (s) { return !s.isEmpty(); }));
        }
    };
    EditorContextKeysManager.prototype._updateFromFocus = function () {
        this._editorFocus.set(this._editor.hasWidgetFocus());
        this._editorTextFocus.set(this._editor.isFocused());
    };
    return EditorContextKeysManager;
}(Disposable));
var EditorModeContext = /** @class */ (function (_super) {
    __extends(EditorModeContext, _super);
    function EditorModeContext(editor, contextKeyService) {
        var _this = _super.call(this) || this;
        _this._editor = editor;
        _this._langId = EditorContextKeys.languageId.bindTo(contextKeyService);
        _this._hasCompletionItemProvider = EditorContextKeys.hasCompletionItemProvider.bindTo(contextKeyService);
        _this._hasCodeActionsProvider = EditorContextKeys.hasCodeActionsProvider.bindTo(contextKeyService);
        _this._hasCodeLensProvider = EditorContextKeys.hasCodeLensProvider.bindTo(contextKeyService);
        _this._hasDefinitionProvider = EditorContextKeys.hasDefinitionProvider.bindTo(contextKeyService);
        _this._hasImplementationProvider = EditorContextKeys.hasImplementationProvider.bindTo(contextKeyService);
        _this._hasTypeDefinitionProvider = EditorContextKeys.hasTypeDefinitionProvider.bindTo(contextKeyService);
        _this._hasHoverProvider = EditorContextKeys.hasHoverProvider.bindTo(contextKeyService);
        _this._hasDocumentHighlightProvider = EditorContextKeys.hasDocumentHighlightProvider.bindTo(contextKeyService);
        _this._hasDocumentSymbolProvider = EditorContextKeys.hasDocumentSymbolProvider.bindTo(contextKeyService);
        _this._hasReferenceProvider = EditorContextKeys.hasReferenceProvider.bindTo(contextKeyService);
        _this._hasRenameProvider = EditorContextKeys.hasRenameProvider.bindTo(contextKeyService);
        _this._hasDocumentFormattingProvider = EditorContextKeys.hasDocumentFormattingProvider.bindTo(contextKeyService);
        _this._hasDocumentSelectionFormattingProvider = EditorContextKeys.hasDocumentSelectionFormattingProvider.bindTo(contextKeyService);
        _this._hasSignatureHelpProvider = EditorContextKeys.hasSignatureHelpProvider.bindTo(contextKeyService);
        _this._isInWalkThrough = EditorContextKeys.isInEmbeddedEditor.bindTo(contextKeyService);
        var update = function () { return _this._update(); };
        // update when model/mode changes
        _this._register(editor.onDidChangeModel(update));
        _this._register(editor.onDidChangeModelLanguage(update));
        // update when registries change
        _this._register(modes.SuggestRegistry.onDidChange(update));
        _this._register(modes.CodeActionProviderRegistry.onDidChange(update));
        _this._register(modes.CodeLensProviderRegistry.onDidChange(update));
        _this._register(modes.DefinitionProviderRegistry.onDidChange(update));
        _this._register(modes.ImplementationProviderRegistry.onDidChange(update));
        _this._register(modes.TypeDefinitionProviderRegistry.onDidChange(update));
        _this._register(modes.HoverProviderRegistry.onDidChange(update));
        _this._register(modes.DocumentHighlightProviderRegistry.onDidChange(update));
        _this._register(modes.DocumentSymbolProviderRegistry.onDidChange(update));
        _this._register(modes.ReferenceProviderRegistry.onDidChange(update));
        _this._register(modes.RenameProviderRegistry.onDidChange(update));
        _this._register(modes.DocumentFormattingEditProviderRegistry.onDidChange(update));
        _this._register(modes.DocumentRangeFormattingEditProviderRegistry.onDidChange(update));
        _this._register(modes.SignatureHelpProviderRegistry.onDidChange(update));
        update();
        return _this;
    }
    EditorModeContext.prototype.dispose = function () {
        _super.prototype.dispose.call(this);
    };
    EditorModeContext.prototype.reset = function () {
        this._langId.reset();
        this._hasCompletionItemProvider.reset();
        this._hasCodeActionsProvider.reset();
        this._hasCodeLensProvider.reset();
        this._hasDefinitionProvider.reset();
        this._hasImplementationProvider.reset();
        this._hasTypeDefinitionProvider.reset();
        this._hasHoverProvider.reset();
        this._hasDocumentHighlightProvider.reset();
        this._hasDocumentSymbolProvider.reset();
        this._hasReferenceProvider.reset();
        this._hasRenameProvider.reset();
        this._hasDocumentFormattingProvider.reset();
        this._hasDocumentSelectionFormattingProvider.reset();
        this._hasSignatureHelpProvider.reset();
        this._isInWalkThrough.reset();
    };
    EditorModeContext.prototype._update = function () {
        var model = this._editor.getModel();
        if (!model) {
            this.reset();
            return;
        }
        this._langId.set(model.getLanguageIdentifier().language);
        this._hasCompletionItemProvider.set(modes.SuggestRegistry.has(model));
        this._hasCodeActionsProvider.set(modes.CodeActionProviderRegistry.has(model));
        this._hasCodeLensProvider.set(modes.CodeLensProviderRegistry.has(model));
        this._hasDefinitionProvider.set(modes.DefinitionProviderRegistry.has(model));
        this._hasImplementationProvider.set(modes.ImplementationProviderRegistry.has(model));
        this._hasTypeDefinitionProvider.set(modes.TypeDefinitionProviderRegistry.has(model));
        this._hasHoverProvider.set(modes.HoverProviderRegistry.has(model));
        this._hasDocumentHighlightProvider.set(modes.DocumentHighlightProviderRegistry.has(model));
        this._hasDocumentSymbolProvider.set(modes.DocumentSymbolProviderRegistry.has(model));
        this._hasReferenceProvider.set(modes.ReferenceProviderRegistry.has(model));
        this._hasRenameProvider.set(modes.RenameProviderRegistry.has(model));
        this._hasSignatureHelpProvider.set(modes.SignatureHelpProviderRegistry.has(model));
        this._hasDocumentFormattingProvider.set(modes.DocumentFormattingEditProviderRegistry.has(model) || modes.DocumentRangeFormattingEditProviderRegistry.has(model));
        this._hasDocumentSelectionFormattingProvider.set(modes.DocumentRangeFormattingEditProviderRegistry.has(model));
        this._isInWalkThrough.set(model.uri.scheme === Schemas.walkThroughSnippet);
    };
    return EditorModeContext;
}(Disposable));
export { EditorModeContext };
