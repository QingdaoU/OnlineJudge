/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { createDecorator } from '../../../platform/instantiation/common/instantiation.js';
import { isCodeEditor, isDiffEditor } from '../editorBrowser.js';
export var ICodeEditorService = createDecorator('codeEditorService');
/**
 * Uses `editor.getControl()` and returns either a `codeEditor` or a `diffEditor` or nothing.
 */
export function getCodeOrDiffEditor(editor) {
    if (editor) {
        var control = editor.getControl();
        if (control) {
            if (isCodeEditor(control)) {
                return {
                    codeEditor: control,
                    diffEditor: null
                };
            }
            if (isDiffEditor(control)) {
                return {
                    codeEditor: null,
                    diffEditor: control
                };
            }
        }
    }
    return {
        codeEditor: null,
        diffEditor: null
    };
}
/**
 * Uses `editor.getControl()` and returns either the code editor, or the modified editor of a diff editor or nothing.
 */
export function getCodeEditor(editor) {
    var r = getCodeOrDiffEditor(editor);
    return r.codeEditor || (r.diffEditor && r.diffEditor.getModifiedEditor()) || null;
}
