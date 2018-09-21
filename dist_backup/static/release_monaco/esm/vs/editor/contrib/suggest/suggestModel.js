/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { onUnexpectedError } from '../../../base/common/errors.js';
import { isFalsyOrEmpty } from '../../../base/common/arrays.js';
import { TimeoutTimer } from '../../../base/common/async.js';
import { Emitter } from '../../../base/common/event.js';
import { dispose } from '../../../base/common/lifecycle.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { SuggestRegistry, SuggestTriggerKind } from '../../common/modes.js';
import { Position } from '../../common/core/position.js';
import { provideSuggestionItems, getSuggestionComparator } from './suggest.js';
import { CompletionModel } from './completionModel.js';
import { CursorChangeReason } from '../../common/controller/cursorEvents.js';
var LineContext = /** @class */ (function () {
    function LineContext(model, position, auto) {
        this.leadingLineContent = model.getLineContent(position.lineNumber).substr(0, position.column - 1);
        this.leadingWord = model.getWordUntilPosition(position);
        this.lineNumber = position.lineNumber;
        this.column = position.column;
        this.auto = auto;
    }
    LineContext.shouldAutoTrigger = function (editor) {
        var model = editor.getModel();
        if (!model) {
            return false;
        }
        var pos = editor.getPosition();
        model.tokenizeIfCheap(pos.lineNumber);
        var word = model.getWordAtPosition(pos);
        if (!word) {
            return false;
        }
        if (word.endColumn !== pos.column) {
            return false;
        }
        if (!isNaN(Number(word.word))) {
            return false;
        }
        return true;
    };
    return LineContext;
}());
export { LineContext };
var SuggestModel = /** @class */ (function () {
    function SuggestModel(editor) {
        var _this = this;
        this._toDispose = [];
        this._triggerRefilter = new TimeoutTimer();
        this._onDidCancel = new Emitter();
        this._onDidTrigger = new Emitter();
        this._onDidSuggest = new Emitter();
        this.onDidCancel = this._onDidCancel.event;
        this.onDidTrigger = this._onDidTrigger.event;
        this.onDidSuggest = this._onDidSuggest.event;
        this._editor = editor;
        this._state = 0 /* Idle */;
        this._triggerAutoSuggestPromise = null;
        this._requestPromise = null;
        this._completionModel = null;
        this._context = null;
        this._currentPosition = this._editor.getPosition() || new Position(1, 1);
        // wire up various listeners
        this._toDispose.push(this._editor.onDidChangeModel(function () {
            _this._updateTriggerCharacters();
            _this.cancel();
        }));
        this._toDispose.push(this._editor.onDidChangeModelLanguage(function () {
            _this._updateTriggerCharacters();
            _this.cancel();
        }));
        this._toDispose.push(this._editor.onDidChangeConfiguration(function () {
            _this._updateTriggerCharacters();
            _this._updateQuickSuggest();
        }));
        this._toDispose.push(SuggestRegistry.onDidChange(function () {
            _this._updateTriggerCharacters();
            _this._updateActiveSuggestSession();
        }));
        this._toDispose.push(this._editor.onDidChangeCursorSelection(function (e) {
            _this._onCursorChange(e);
        }));
        this._toDispose.push(this._editor.onDidChangeModelContent(function (e) {
            _this._refilterCompletionItems();
        }));
        this._updateTriggerCharacters();
        this._updateQuickSuggest();
    }
    SuggestModel.prototype.dispose = function () {
        dispose([this._onDidCancel, this._onDidSuggest, this._onDidTrigger, this._triggerCharacterListener, this._triggerRefilter]);
        this._toDispose = dispose(this._toDispose);
        dispose(this._completionModel);
        this.cancel();
    };
    // --- handle configuration & precondition changes
    SuggestModel.prototype._updateQuickSuggest = function () {
        this._quickSuggestDelay = this._editor.getConfiguration().contribInfo.quickSuggestionsDelay;
        if (isNaN(this._quickSuggestDelay) || (!this._quickSuggestDelay && this._quickSuggestDelay !== 0) || this._quickSuggestDelay < 0) {
            this._quickSuggestDelay = 10;
        }
    };
    SuggestModel.prototype._updateTriggerCharacters = function () {
        var _this = this;
        dispose(this._triggerCharacterListener);
        if (this._editor.getConfiguration().readOnly
            || !this._editor.getModel()
            || !this._editor.getConfiguration().contribInfo.suggestOnTriggerCharacters) {
            return;
        }
        var supportsByTriggerCharacter = Object.create(null);
        for (var _i = 0, _a = SuggestRegistry.all(this._editor.getModel()); _i < _a.length; _i++) {
            var support = _a[_i];
            if (isFalsyOrEmpty(support.triggerCharacters)) {
                continue;
            }
            for (var _b = 0, _c = support.triggerCharacters; _b < _c.length; _b++) {
                var ch = _c[_b];
                var array = supportsByTriggerCharacter[ch];
                if (!array) {
                    supportsByTriggerCharacter[ch] = [support];
                }
                else {
                    array.push(support);
                }
            }
        }
        this._triggerCharacterListener = this._editor.onDidType(function (text) {
            var lastChar = text.charAt(text.length - 1);
            var supports = supportsByTriggerCharacter[lastChar];
            if (supports) {
                // keep existing items that where not computed by the
                // supports/providers that want to trigger now
                var items = [];
                if (_this._completionModel) {
                    for (var _i = 0, _a = _this._completionModel.items; _i < _a.length; _i++) {
                        var item = _a[_i];
                        if (supports.indexOf(item.support) < 0) {
                            items.push(item);
                        }
                    }
                }
                _this.trigger({ auto: true, triggerCharacter: lastChar }, Boolean(_this._completionModel), supports, items);
            }
        });
    };
    Object.defineProperty(SuggestModel.prototype, "state", {
        // --- trigger/retrigger/cancel suggest
        get: function () {
            return this._state;
        },
        enumerable: true,
        configurable: true
    });
    SuggestModel.prototype.cancel = function (retrigger) {
        if (retrigger === void 0) { retrigger = false; }
        this._triggerRefilter.cancel();
        if (this._triggerAutoSuggestPromise) {
            this._triggerAutoSuggestPromise.cancel();
            this._triggerAutoSuggestPromise = null;
        }
        if (this._requestPromise) {
            this._requestPromise.cancel();
            this._requestPromise = null;
        }
        this._state = 0 /* Idle */;
        dispose(this._completionModel);
        this._completionModel = null;
        this._context = null;
        this._onDidCancel.fire({ retrigger: retrigger });
    };
    SuggestModel.prototype._updateActiveSuggestSession = function () {
        if (this._state !== 0 /* Idle */) {
            if (!SuggestRegistry.has(this._editor.getModel())) {
                this.cancel();
            }
            else {
                this.trigger({ auto: this._state === 2 /* Auto */ }, true);
            }
        }
    };
    SuggestModel.prototype._onCursorChange = function (e) {
        var _this = this;
        var prevPosition = this._currentPosition;
        this._currentPosition = this._editor.getPosition();
        if (!e.selection.isEmpty()
            || e.reason !== CursorChangeReason.NotSet
            || (e.source !== 'keyboard' && e.source !== 'deleteLeft')) {
            // Early exit if nothing needs to be done!
            // Leave some form of early exit check here if you wish to continue being a cursor position change listener ;)
            if (this._state !== 0 /* Idle */) {
                this.cancel();
            }
            return;
        }
        if (!SuggestRegistry.has(this._editor.getModel())) {
            return;
        }
        var model = this._editor.getModel();
        if (!model) {
            return;
        }
        if (this._state === 0 /* Idle */) {
            // trigger 24x7 IntelliSense when idle, enabled, when cursor
            // moved RIGHT, and when at a good position
            if (this._editor.getConfiguration().contribInfo.quickSuggestions !== false
                && prevPosition.isBefore(this._currentPosition)) {
                this.cancel();
                this._triggerAutoSuggestPromise = TPromise.timeout(this._quickSuggestDelay);
                this._triggerAutoSuggestPromise.then(function () {
                    if (LineContext.shouldAutoTrigger(_this._editor)) {
                        var model_1 = _this._editor.getModel();
                        var pos = _this._editor.getPosition();
                        if (!model_1) {
                            return;
                        }
                        // validate enabled now
                        var quickSuggestions = _this._editor.getConfiguration().contribInfo.quickSuggestions;
                        if (quickSuggestions === false) {
                            return;
                        }
                        else if (quickSuggestions === true) {
                            // all good
                        }
                        else {
                            // Check the type of the token that triggered this
                            model_1.tokenizeIfCheap(pos.lineNumber);
                            var lineTokens = model_1.getLineTokens(pos.lineNumber);
                            var tokenType = lineTokens.getStandardTokenType(lineTokens.findTokenIndexAtOffset(Math.max(pos.column - 1 - 1, 0)));
                            var inValidScope = quickSuggestions.other && tokenType === 0 /* Other */
                                || quickSuggestions.comments && tokenType === 1 /* Comment */
                                || quickSuggestions.strings && tokenType === 2 /* String */;
                            if (!inValidScope) {
                                return;
                            }
                        }
                        _this.trigger({ auto: true });
                    }
                    _this._triggerAutoSuggestPromise = null;
                });
            }
        }
    };
    SuggestModel.prototype._refilterCompletionItems = function () {
        var _this = this;
        if (this._state === 0 /* Idle */) {
            return;
        }
        var model = this._editor.getModel();
        if (model) {
            // refine active suggestion
            this._triggerRefilter.cancelAndSet(function () {
                var position = _this._editor.getPosition();
                var ctx = new LineContext(model, position, _this._state === 2 /* Auto */);
                _this._onNewContext(ctx);
            }, 25);
        }
    };
    SuggestModel.prototype.trigger = function (context, retrigger, onlyFrom, existingItems) {
        var _this = this;
        if (retrigger === void 0) { retrigger = false; }
        var model = this._editor.getModel();
        if (!model) {
            return;
        }
        var auto = context.auto;
        var ctx = new LineContext(model, this._editor.getPosition(), auto);
        // Cancel previous requests, change state & update UI
        this.cancel(retrigger);
        this._state = auto ? 2 /* Auto */ : 1 /* Manual */;
        this._onDidTrigger.fire({ auto: auto });
        // Capture context when request was sent
        this._context = ctx;
        // Build context for request
        var suggestCtx;
        if (context.triggerCharacter) {
            suggestCtx = {
                triggerKind: SuggestTriggerKind.TriggerCharacter,
                triggerCharacter: context.triggerCharacter
            };
        }
        else if (onlyFrom && onlyFrom.length) {
            suggestCtx = { triggerKind: SuggestTriggerKind.TriggerForIncompleteCompletions };
        }
        else {
            suggestCtx = { triggerKind: SuggestTriggerKind.Invoke };
        }
        this._requestPromise = provideSuggestionItems(model, this._editor.getPosition(), this._editor.getConfiguration().contribInfo.snippetSuggestions, onlyFrom, suggestCtx).then(function (items) {
            _this._requestPromise = null;
            if (_this._state === 0 /* Idle */) {
                return;
            }
            var model = _this._editor.getModel();
            if (!model) {
                return;
            }
            if (!isFalsyOrEmpty(existingItems)) {
                var cmpFn = getSuggestionComparator(_this._editor.getConfiguration().contribInfo.snippetSuggestions);
                items = items.concat(existingItems).sort(cmpFn);
            }
            var ctx = new LineContext(model, _this._editor.getPosition(), auto);
            dispose(_this._completionModel);
            _this._completionModel = new CompletionModel(items, _this._context.column, {
                leadingLineContent: ctx.leadingLineContent,
                characterCountDelta: _this._context ? ctx.column - _this._context.column : 0
            }, _this._editor.getConfiguration().contribInfo.snippetSuggestions);
            _this._onNewContext(ctx);
        }).then(null, onUnexpectedError);
    };
    SuggestModel.prototype._onNewContext = function (ctx) {
        if (!this._context) {
            // happens when 24x7 IntelliSense is enabled and still in its delay
            return;
        }
        if (ctx.lineNumber !== this._context.lineNumber) {
            // e.g. happens when pressing Enter while IntelliSense is computed
            this.cancel();
            return;
        }
        if (ctx.column < this._context.column) {
            // typed -> moved cursor LEFT -> retrigger if still on a word
            if (ctx.leadingWord.word) {
                this.trigger({ auto: this._context.auto }, true);
            }
            else {
                this.cancel();
            }
            return;
        }
        if (!this._completionModel) {
            // happens when IntelliSense is not yet computed
            return;
        }
        if (ctx.column > this._context.column && this._completionModel.incomplete && ctx.leadingWord.word.length !== 0) {
            // typed -> moved cursor RIGHT & incomple model & still on a word -> retrigger
            var _a = this._completionModel.resolveIncompleteInfo(), complete = _a.complete, incomplete = _a.incomplete;
            this.trigger({ auto: this._state === 2 /* Auto */ }, true, incomplete, complete);
        }
        else {
            // typed -> moved cursor RIGHT -> update UI
            var oldLineContext = this._completionModel.lineContext;
            var isFrozen = false;
            this._completionModel.lineContext = {
                leadingLineContent: ctx.leadingLineContent,
                characterCountDelta: ctx.column - this._context.column
            };
            if (this._completionModel.items.length === 0) {
                if (LineContext.shouldAutoTrigger(this._editor) && this._context.leadingWord.endColumn < ctx.leadingWord.startColumn) {
                    // retrigger when heading into a new word
                    this.trigger({ auto: this._context.auto }, true);
                    return;
                }
                if (!this._context.auto) {
                    // freeze when IntelliSense was manually requested
                    this._completionModel.lineContext = oldLineContext;
                    isFrozen = this._completionModel.items.length > 0;
                    if (isFrozen && ctx.leadingWord.word.length === 0) {
                        // there were results before but now there aren't
                        // and also we are not on a word anymore -> cancel
                        this.cancel();
                        return;
                    }
                }
                else {
                    // nothing left
                    this.cancel();
                    return;
                }
            }
            this._onDidSuggest.fire({
                completionModel: this._completionModel,
                auto: this._context.auto,
                isFrozen: isFrozen,
            });
        }
    };
    return SuggestModel;
}());
export { SuggestModel };
