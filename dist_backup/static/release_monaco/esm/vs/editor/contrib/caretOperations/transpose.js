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
import * as nls from '../../../nls.js';
import { Range } from '../../common/core/range.js';
import { EditorContextKeys } from '../../common/editorContextKeys.js';
import { registerEditorAction, EditorAction } from '../../browser/editorExtensions.js';
import { ReplaceCommand } from '../../common/commands/replaceCommand.js';
var TransposeLettersAction = /** @class */ (function (_super) {
    __extends(TransposeLettersAction, _super);
    function TransposeLettersAction() {
        return _super.call(this, {
            id: 'editor.action.transposeLetters',
            label: nls.localize('transposeLetters.label', "Transpose Letters"),
            alias: 'Transpose Letters',
            precondition: EditorContextKeys.writable,
            kbOpts: {
                kbExpr: EditorContextKeys.textFocus,
                primary: 0,
                mac: {
                    primary: 256 /* WinCtrl */ | 50 /* KEY_T */
                }
            }
        }) || this;
    }
    TransposeLettersAction.prototype.run = function (accessor, editor) {
        var model = editor.getModel();
        var commands = [];
        var selections = editor.getSelections();
        for (var i = 0; i < selections.length; i++) {
            var selection = selections[i];
            if (!selection.isEmpty()) {
                continue;
            }
            var lineNumber = selection.startLineNumber;
            var column = selection.startColumn;
            if (column === 1) {
                // at the beginning of line
                continue;
            }
            var maxColumn = model.getLineMaxColumn(lineNumber);
            if (column === maxColumn) {
                // at the end of line
                continue;
            }
            var lineContent = model.getLineContent(lineNumber);
            var charToTheLeft = lineContent.charAt(column - 2);
            var charToTheRight = lineContent.charAt(column - 1);
            var replaceRange = new Range(lineNumber, column - 1, lineNumber, column + 1);
            commands.push(new ReplaceCommand(replaceRange, charToTheRight + charToTheLeft));
        }
        if (commands.length > 0) {
            editor.pushUndoStop();
            editor.executeCommands(this.id, commands);
            editor.pushUndoStop();
        }
    };
    return TransposeLettersAction;
}(EditorAction));
registerEditorAction(TransposeLettersAction);
