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
import { RunOnceScheduler } from '../../../base/common/async.js';
import { Selection } from '../../common/core/selection.js';
import * as strings from '../../../base/common/strings.js';
import { Emitter } from '../../../base/common/event.js';
import { Disposable } from '../../../base/common/lifecycle.js';
import { TextAreaState } from './textAreaState.js';
import * as browser from '../../../base/browser/browser.js';
import * as platform from '../../../base/common/platform.js';
import * as dom from '../../../base/browser/dom.js';
export var CopyOptions = {
    forceCopyWithSyntaxHighlighting: false
};
/**
 * Writes screen reader content to the textarea and is able to analyze its input events to generate:
 *  - onCut
 *  - onPaste
 *  - onType
 *
 * Composition events are generated for presentation purposes (composition input is reflected in onType).
 */
var TextAreaInput = /** @class */ (function (_super) {
    __extends(TextAreaInput, _super);
    function TextAreaInput(host, textArea) {
        var _this = _super.call(this) || this;
        _this._onFocus = _this._register(new Emitter());
        _this.onFocus = _this._onFocus.event;
        _this._onBlur = _this._register(new Emitter());
        _this.onBlur = _this._onBlur.event;
        _this._onKeyDown = _this._register(new Emitter());
        _this.onKeyDown = _this._onKeyDown.event;
        _this._onKeyUp = _this._register(new Emitter());
        _this.onKeyUp = _this._onKeyUp.event;
        _this._onCut = _this._register(new Emitter());
        _this.onCut = _this._onCut.event;
        _this._onPaste = _this._register(new Emitter());
        _this.onPaste = _this._onPaste.event;
        _this._onType = _this._register(new Emitter());
        _this.onType = _this._onType.event;
        _this._onCompositionStart = _this._register(new Emitter());
        _this.onCompositionStart = _this._onCompositionStart.event;
        _this._onCompositionUpdate = _this._register(new Emitter());
        _this.onCompositionUpdate = _this._onCompositionUpdate.event;
        _this._onCompositionEnd = _this._register(new Emitter());
        _this.onCompositionEnd = _this._onCompositionEnd.event;
        _this._onSelectionChangeRequest = _this._register(new Emitter());
        _this.onSelectionChangeRequest = _this._onSelectionChangeRequest.event;
        _this._host = host;
        _this._textArea = _this._register(new TextAreaWrapper(textArea));
        _this._asyncTriggerCut = _this._register(new RunOnceScheduler(function () { return _this._onCut.fire(); }, 0));
        _this._textAreaState = TextAreaState.EMPTY;
        _this.writeScreenReaderContent('ctor');
        _this._hasFocus = false;
        _this._isDoingComposition = false;
        _this._nextCommand = 0 /* Type */;
        _this._register(dom.addStandardDisposableListener(textArea.domNode, 'keydown', function (e) {
            if (_this._isDoingComposition && e.keyCode === 109 /* KEY_IN_COMPOSITION */) {
                // Stop propagation for keyDown events if the IME is processing key input
                e.stopPropagation();
            }
            if (e.equals(9 /* Escape */)) {
                // Prevent default always for `Esc`, otherwise it will generate a keypress
                // See https://msdn.microsoft.com/en-us/library/ie/ms536939(v=vs.85).aspx
                e.preventDefault();
            }
            _this._onKeyDown.fire(e);
        }));
        _this._register(dom.addStandardDisposableListener(textArea.domNode, 'keyup', function (e) {
            _this._onKeyUp.fire(e);
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'compositionstart', function (e) {
            if (_this._isDoingComposition) {
                return;
            }
            _this._isDoingComposition = true;
            // In IE we cannot set .value when handling 'compositionstart' because the entire composition will get canceled.
            if (!browser.isEdgeOrIE) {
                _this._setAndWriteTextAreaState('compositionstart', TextAreaState.EMPTY);
            }
            _this._onCompositionStart.fire();
        }));
        /**
         * Deduce the typed input from a text area's value and the last observed state.
         */
        var deduceInputFromTextAreaValue = function (couldBeEmojiInput) {
            var oldState = _this._textAreaState;
            var newState = _this._textAreaState.readFromTextArea(_this._textArea);
            return [newState, TextAreaState.deduceInput(oldState, newState, couldBeEmojiInput)];
        };
        /**
         * Deduce the composition input from a string.
         */
        var deduceComposition = function (text) {
            var oldState = _this._textAreaState;
            var newState = TextAreaState.selectedText(text);
            var typeInput = {
                text: newState.value,
                replaceCharCnt: oldState.selectionEnd - oldState.selectionStart
            };
            return [newState, typeInput];
        };
        var compositionDataInValid = function (locale) {
            // https://github.com/Microsoft/monaco-editor/issues/339
            // Multi-part Japanese compositions reset cursor in Edge/IE, Chinese and Korean IME don't have this issue.
            // The reason that we can't use this path for all CJK IME is IE and Edge behave differently when handling Korean IME,
            // which breaks this path of code.
            if (browser.isEdgeOrIE && locale === 'ja') {
                return true;
            }
            // https://github.com/Microsoft/monaco-editor/issues/545
            // On IE11, we can't trust composition data when typing Chinese as IE11 doesn't emit correct
            // events when users type numbers in IME.
            // Chinese: zh-Hans-CN, zh-Hans-SG, zh-Hant-TW, zh-Hant-HK
            if (browser.isIE && locale.indexOf('zh-Han') === 0) {
                return true;
            }
            return false;
        };
        _this._register(dom.addDisposableListener(textArea.domNode, 'compositionupdate', function (e) {
            if (browser.isChromev56) {
                // See https://github.com/Microsoft/monaco-editor/issues/320
                // where compositionupdate .data is broken in Chrome v55 and v56
                // See https://bugs.chromium.org/p/chromium/issues/detail?id=677050#c9
                // The textArea doesn't get the composition update yet, the value of textarea is still obsolete
                // so we can't correct e at this moment.
                return;
            }
            if (compositionDataInValid(e.locale)) {
                var _a = deduceInputFromTextAreaValue(/*couldBeEmojiInput*/ false), newState_1 = _a[0], typeInput_1 = _a[1];
                _this._textAreaState = newState_1;
                _this._onType.fire(typeInput_1);
                _this._onCompositionUpdate.fire(e);
                return;
            }
            var _b = deduceComposition(e.data), newState = _b[0], typeInput = _b[1];
            _this._textAreaState = newState;
            _this._onType.fire(typeInput);
            _this._onCompositionUpdate.fire(e);
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'compositionend', function (e) {
            if (compositionDataInValid(e.locale)) {
                // https://github.com/Microsoft/monaco-editor/issues/339
                var _a = deduceInputFromTextAreaValue(/*couldBeEmojiInput*/ false), newState = _a[0], typeInput = _a[1];
                _this._textAreaState = newState;
                _this._onType.fire(typeInput);
            }
            else {
                var _b = deduceComposition(e.data), newState = _b[0], typeInput = _b[1];
                _this._textAreaState = newState;
                _this._onType.fire(typeInput);
            }
            // Due to isEdgeOrIE (where the textarea was not cleared initially) and isChrome (the textarea is not updated correctly when composition ends)
            // we cannot assume the text at the end consists only of the composited text
            if (browser.isEdgeOrIE || browser.isChrome) {
                _this._textAreaState = _this._textAreaState.readFromTextArea(_this._textArea);
            }
            if (!_this._isDoingComposition) {
                return;
            }
            _this._isDoingComposition = false;
            _this._onCompositionEnd.fire();
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'input', function () {
            // Pretend here we touched the text area, as the `input` event will most likely
            // result in a `selectionchange` event which we want to ignore
            _this._textArea.setIgnoreSelectionChangeTime('received input event');
            if (_this._isDoingComposition) {
                // See https://github.com/Microsoft/monaco-editor/issues/320
                if (browser.isChromev56) {
                    var _a = deduceComposition(_this._textArea.getValue()), newState_2 = _a[0], typeInput_2 = _a[1];
                    _this._textAreaState = newState_2;
                    _this._onType.fire(typeInput_2);
                    var e = {
                        data: typeInput_2.text
                    };
                    _this._onCompositionUpdate.fire(e);
                }
                return;
            }
            var _b = deduceInputFromTextAreaValue(/*couldBeEmojiInput*/ platform.isMacintosh), newState = _b[0], typeInput = _b[1];
            if (typeInput.replaceCharCnt === 0 && typeInput.text.length === 1 && strings.isHighSurrogate(typeInput.text.charCodeAt(0))) {
                // Ignore invalid input but keep it around for next time
                return;
            }
            _this._textAreaState = newState;
            // console.log('==> DEDUCED INPUT: ' + JSON.stringify(typeInput));
            if (_this._nextCommand === 0 /* Type */) {
                if (typeInput.text !== '') {
                    _this._onType.fire(typeInput);
                }
            }
            else {
                if (typeInput.text !== '') {
                    _this._onPaste.fire({
                        text: typeInput.text
                    });
                }
                _this._nextCommand = 0 /* Type */;
            }
        }));
        // --- Clipboard operations
        _this._register(dom.addDisposableListener(textArea.domNode, 'cut', function (e) {
            // Pretend here we touched the text area, as the `cut` event will most likely
            // result in a `selectionchange` event which we want to ignore
            _this._textArea.setIgnoreSelectionChangeTime('received cut event');
            _this._ensureClipboardGetsEditorSelection(e);
            _this._asyncTriggerCut.schedule();
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'copy', function (e) {
            _this._ensureClipboardGetsEditorSelection(e);
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'paste', function (e) {
            // Pretend here we touched the text area, as the `paste` event will most likely
            // result in a `selectionchange` event which we want to ignore
            _this._textArea.setIgnoreSelectionChangeTime('received paste event');
            if (ClipboardEventUtils.canUseTextData(e)) {
                var pastePlainText = ClipboardEventUtils.getTextData(e);
                if (pastePlainText !== '') {
                    _this._onPaste.fire({
                        text: pastePlainText
                    });
                }
            }
            else {
                if (_this._textArea.getSelectionStart() !== _this._textArea.getSelectionEnd()) {
                    // Clean up the textarea, to get a clean paste
                    _this._setAndWriteTextAreaState('paste', TextAreaState.EMPTY);
                }
                _this._nextCommand = 1 /* Paste */;
            }
        }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'focus', function () { return _this._setHasFocus(true); }));
        _this._register(dom.addDisposableListener(textArea.domNode, 'blur', function () { return _this._setHasFocus(false); }));
        // See https://github.com/Microsoft/vscode/issues/27216
        // When using a Braille display, it is possible for users to reposition the
        // system caret. This is reflected in Chrome as a `selectionchange` event.
        //
        // The `selectionchange` event appears to be emitted under numerous other circumstances,
        // so it is quite a challenge to distinguish a `selectionchange` coming in from a user
        // using a Braille display from all the other cases.
        //
        // The problems with the `selectionchange` event are:
        //  * the event is emitted when the textarea is focused programmatically -- textarea.focus()
        //  * the event is emitted when the selection is changed in the textarea programatically -- textarea.setSelectionRange(...)
        //  * the event is emitted when the value of the textarea is changed programmatically -- textarea.value = '...'
        //  * the event is emitted when tabbing into the textarea
        //  * the event is emitted asynchronously (sometimes with a delay as high as a few tens of ms)
        //  * the event sometimes comes in bursts for a single logical textarea operation
        // `selectionchange` events often come multiple times for a single logical change
        // so throttle multiple `selectionchange` events that burst in a short period of time.
        var previousSelectionChangeEventTime = 0;
        _this._register(dom.addDisposableListener(document, 'selectionchange', function (e) {
            if (!_this._hasFocus) {
                return;
            }
            if (_this._isDoingComposition) {
                return;
            }
            if (!browser.isChrome || !platform.isWindows) {
                // Support only for Chrome on Windows until testing happens on other browsers + OS configurations
                return;
            }
            var now = Date.now();
            var delta1 = now - previousSelectionChangeEventTime;
            previousSelectionChangeEventTime = now;
            if (delta1 < 5) {
                // received another `selectionchange` event within 5ms of the previous `selectionchange` event
                // => ignore it
                return;
            }
            var delta2 = now - _this._textArea.getIgnoreSelectionChangeTime();
            _this._textArea.resetSelectionChangeTime();
            if (delta2 < 100) {
                // received a `selectionchange` event within 100ms since we touched the textarea
                // => ignore it, since we caused it
                return;
            }
            if (!_this._textAreaState.selectionStartPosition || !_this._textAreaState.selectionEndPosition) {
                // Cannot correlate a position in the textarea with a position in the editor...
                return;
            }
            var newValue = _this._textArea.getValue();
            if (_this._textAreaState.value !== newValue) {
                // Cannot correlate a position in the textarea with a position in the editor...
                return;
            }
            var newSelectionStart = _this._textArea.getSelectionStart();
            var newSelectionEnd = _this._textArea.getSelectionEnd();
            if (_this._textAreaState.selectionStart === newSelectionStart && _this._textAreaState.selectionEnd === newSelectionEnd) {
                // Nothing to do...
                return;
            }
            var _newSelectionStartPosition = _this._textAreaState.deduceEditorPosition(newSelectionStart);
            var newSelectionStartPosition = _this._host.deduceModelPosition(_newSelectionStartPosition[0], _newSelectionStartPosition[1], _newSelectionStartPosition[2]);
            var _newSelectionEndPosition = _this._textAreaState.deduceEditorPosition(newSelectionEnd);
            var newSelectionEndPosition = _this._host.deduceModelPosition(_newSelectionEndPosition[0], _newSelectionEndPosition[1], _newSelectionEndPosition[2]);
            var newSelection = new Selection(newSelectionStartPosition.lineNumber, newSelectionStartPosition.column, newSelectionEndPosition.lineNumber, newSelectionEndPosition.column);
            _this._onSelectionChangeRequest.fire(newSelection);
        }));
        return _this;
    }
    TextAreaInput.prototype.dispose = function () {
        _super.prototype.dispose.call(this);
    };
    TextAreaInput.prototype.focusTextArea = function () {
        // Setting this._hasFocus and writing the screen reader content
        // will result in a focus() and setSelectionRange() in the textarea
        this._setHasFocus(true);
    };
    TextAreaInput.prototype.isFocused = function () {
        return this._hasFocus;
    };
    TextAreaInput.prototype._setHasFocus = function (newHasFocus) {
        if (this._hasFocus === newHasFocus) {
            // no change
            return;
        }
        this._hasFocus = newHasFocus;
        if (this._isDoingComposition) {
            // textarea gets focus, so the state should be clean
            // https://github.com/Microsoft/monaco-editor/issues/552
            this._isDoingComposition = false;
        }
        if (this._hasFocus) {
            if (browser.isEdge) {
                // Edge has a bug where setting the selection range while the focus event
                // is dispatching doesn't work. To reproduce, "tab into" the editor.
                this._setAndWriteTextAreaState('focusgain', TextAreaState.EMPTY);
            }
            else {
                this.writeScreenReaderContent('focusgain');
            }
        }
        if (this._hasFocus) {
            this._onFocus.fire();
        }
        else {
            this._onBlur.fire();
        }
    };
    TextAreaInput.prototype._setAndWriteTextAreaState = function (reason, textAreaState) {
        if (!this._hasFocus) {
            textAreaState = textAreaState.collapseSelection();
        }
        textAreaState.writeToTextArea(reason, this._textArea, this._hasFocus);
        this._textAreaState = textAreaState;
    };
    TextAreaInput.prototype.writeScreenReaderContent = function (reason) {
        if (this._isDoingComposition) {
            // Do not write to the text area when doing composition
            return;
        }
        this._setAndWriteTextAreaState(reason, this._host.getScreenReaderContent(this._textAreaState));
    };
    TextAreaInput.prototype._ensureClipboardGetsEditorSelection = function (e) {
        var copyPlainText = this._host.getPlainTextToCopy();
        if (!ClipboardEventUtils.canUseTextData(e)) {
            // Looks like an old browser. The strategy is to place the text
            // we'd like to be copied to the clipboard in the textarea and select it.
            this._setAndWriteTextAreaState('copy or cut', TextAreaState.selectedText(copyPlainText));
            return;
        }
        var copyHTML = null;
        if (!browser.isEdgeOrIE && (copyPlainText.length < 65536 || CopyOptions.forceCopyWithSyntaxHighlighting)) {
            copyHTML = this._host.getHTMLToCopy();
        }
        ClipboardEventUtils.setTextData(e, copyPlainText, copyHTML);
    };
    return TextAreaInput;
}(Disposable));
export { TextAreaInput };
var ClipboardEventUtils = /** @class */ (function () {
    function ClipboardEventUtils() {
    }
    ClipboardEventUtils.canUseTextData = function (e) {
        if (e.clipboardData) {
            return true;
        }
        if (window.clipboardData) {
            return true;
        }
        return false;
    };
    ClipboardEventUtils.getTextData = function (e) {
        if (e.clipboardData) {
            e.preventDefault();
            return e.clipboardData.getData('text/plain');
        }
        if (window.clipboardData) {
            e.preventDefault();
            return window.clipboardData.getData('Text');
        }
        throw new Error('ClipboardEventUtils.getTextData: Cannot use text data!');
    };
    ClipboardEventUtils.setTextData = function (e, text, richText) {
        if (e.clipboardData) {
            e.clipboardData.setData('text/plain', text);
            if (richText !== null) {
                e.clipboardData.setData('text/html', richText);
            }
            e.preventDefault();
            return;
        }
        if (window.clipboardData) {
            window.clipboardData.setData('Text', text);
            e.preventDefault();
            return;
        }
        throw new Error('ClipboardEventUtils.setTextData: Cannot use text data!');
    };
    return ClipboardEventUtils;
}());
var TextAreaWrapper = /** @class */ (function (_super) {
    __extends(TextAreaWrapper, _super);
    function TextAreaWrapper(_textArea) {
        var _this = _super.call(this) || this;
        _this._actual = _textArea;
        _this._ignoreSelectionChangeTime = 0;
        return _this;
    }
    TextAreaWrapper.prototype.setIgnoreSelectionChangeTime = function (reason) {
        this._ignoreSelectionChangeTime = Date.now();
    };
    TextAreaWrapper.prototype.getIgnoreSelectionChangeTime = function () {
        return this._ignoreSelectionChangeTime;
    };
    TextAreaWrapper.prototype.resetSelectionChangeTime = function () {
        this._ignoreSelectionChangeTime = 0;
    };
    TextAreaWrapper.prototype.getValue = function () {
        // console.log('current value: ' + this._textArea.value);
        return this._actual.domNode.value;
    };
    TextAreaWrapper.prototype.setValue = function (reason, value) {
        var textArea = this._actual.domNode;
        if (textArea.value === value) {
            // No change
            return;
        }
        // console.log('reason: ' + reason + ', current value: ' + textArea.value + ' => new value: ' + value);
        this.setIgnoreSelectionChangeTime('setValue');
        textArea.value = value;
    };
    TextAreaWrapper.prototype.getSelectionStart = function () {
        return this._actual.domNode.selectionStart;
    };
    TextAreaWrapper.prototype.getSelectionEnd = function () {
        return this._actual.domNode.selectionEnd;
    };
    TextAreaWrapper.prototype.setSelectionRange = function (reason, selectionStart, selectionEnd) {
        var textArea = this._actual.domNode;
        var currentIsFocused = (document.activeElement === textArea);
        var currentSelectionStart = textArea.selectionStart;
        var currentSelectionEnd = textArea.selectionEnd;
        if (currentIsFocused && currentSelectionStart === selectionStart && currentSelectionEnd === selectionEnd) {
            // No change
            // Firefox iframe bug https://github.com/Microsoft/monaco-editor/issues/643#issuecomment-367871377
            if (browser.isFirefox && window.parent !== window) {
                textArea.focus();
            }
            return;
        }
        // console.log('reason: ' + reason + ', setSelectionRange: ' + selectionStart + ' -> ' + selectionEnd);
        if (currentIsFocused) {
            // No need to focus, only need to change the selection range
            this.setIgnoreSelectionChangeTime('setSelectionRange');
            textArea.setSelectionRange(selectionStart, selectionEnd);
            if (browser.isFirefox && window.parent !== window) {
                textArea.focus();
            }
            return;
        }
        // If the focus is outside the textarea, browsers will try really hard to reveal the textarea.
        // Here, we try to undo the browser's desperate reveal.
        try {
            var scrollState = dom.saveParentsScrollTop(textArea);
            this.setIgnoreSelectionChangeTime('setSelectionRange');
            textArea.focus();
            textArea.setSelectionRange(selectionStart, selectionEnd);
            dom.restoreParentsScrollTop(textArea, scrollState);
        }
        catch (e) {
            // Sometimes IE throws when setting selection (e.g. textarea is off-DOM)
        }
    };
    return TextAreaWrapper;
}(Disposable));
