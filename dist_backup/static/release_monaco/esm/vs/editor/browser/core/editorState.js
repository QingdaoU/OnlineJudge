/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as strings from '../../../base/common/strings.js';
var EditorState = /** @class */ (function () {
    function EditorState(editor, flags) {
        this.flags = flags;
        if ((this.flags & 1 /* Value */) !== 0) {
            var model = editor.getModel();
            this.modelVersionId = model ? strings.format('{0}#{1}', model.uri.toString(), model.getVersionId()) : null;
        }
        if ((this.flags & 4 /* Position */) !== 0) {
            this.position = editor.getPosition();
        }
        if ((this.flags & 2 /* Selection */) !== 0) {
            this.selection = editor.getSelection();
        }
        if ((this.flags & 8 /* Scroll */) !== 0) {
            this.scrollLeft = editor.getScrollLeft();
            this.scrollTop = editor.getScrollTop();
        }
    }
    EditorState.prototype._equals = function (other) {
        if (!(other instanceof EditorState)) {
            return false;
        }
        var state = other;
        if (this.modelVersionId !== state.modelVersionId) {
            return false;
        }
        if (this.scrollLeft !== state.scrollLeft || this.scrollTop !== state.scrollTop) {
            return false;
        }
        if (!this.position && state.position || this.position && !state.position || this.position && state.position && !this.position.equals(state.position)) {
            return false;
        }
        if (!this.selection && state.selection || this.selection && !state.selection || this.selection && state.selection && !this.selection.equalsRange(state.selection)) {
            return false;
        }
        return true;
    };
    EditorState.prototype.validate = function (editor) {
        return this._equals(new EditorState(editor, this.flags));
    };
    return EditorState;
}());
export { EditorState };
