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
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = y[op[0] & 2 ? "return" : op[0] ? "throw" : "next"]) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [0, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
import * as nls from '../../../nls.js';
import { isPromiseCanceledError, illegalArgument, onUnexpectedExternalError } from '../../../base/common/errors.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { IFileService } from '../../../platform/files/common/files.js';
import { RawContextKey, IContextKeyService, ContextKeyExpr } from '../../../platform/contextkey/common/contextkey.js';
import { IProgressService } from '../../../platform/progress/common/progress.js';
import { registerEditorAction, registerEditorContribution, EditorAction, EditorCommand, registerEditorCommand, registerDefaultLanguageCommand } from '../../browser/editorExtensions.js';
import { EditorContextKeys } from '../../common/editorContextKeys.js';
import { BulkEdit } from '../../browser/services/bulkEdit.js';
import RenameInputField from './renameInputField.js';
import { ITextModelService } from '../../common/services/resolverService.js';
import { optional } from '../../../platform/instantiation/common/instantiation.js';
import { IThemeService } from '../../../platform/theme/common/themeService.js';
import { sequence, asWinJsPromise } from '../../../base/common/async.js';
import { RenameProviderRegistry } from '../../common/modes.js';
import { alert } from '../../../base/browser/ui/aria/aria.js';
import { Range } from '../../common/core/range.js';
import { MessageController } from '../message/messageController.js';
import { EditorState } from '../../browser/core/editorState.js';
import { KeybindingsRegistry } from '../../../platform/keybinding/common/keybindingsRegistry.js';
import { INotificationService } from '../../../platform/notification/common/notification.js';
export function rename(model, position, newName) {
    var supports = RenameProviderRegistry.ordered(model);
    var rejects = [];
    var hasResult = false;
    var factory = supports.map(function (support) {
        return function () {
            if (!hasResult) {
                return asWinJsPromise(function (token) {
                    return support.provideRenameEdits(model, position, newName, token);
                }).then(function (result) {
                    if (!result) {
                        // ignore
                    }
                    else if (!result.rejectReason) {
                        hasResult = true;
                        return result;
                    }
                    else {
                        rejects.push(result.rejectReason);
                    }
                    return undefined;
                });
            }
            return undefined;
        };
    });
    return sequence(factory).then(function (values) {
        var result = values[0];
        if (rejects.length > 0) {
            return {
                edits: undefined,
                rejectReason: rejects.join('\n')
            };
        }
        else if (!result) {
            return {
                edits: undefined,
                rejectReason: nls.localize('no result', "No result.")
            };
        }
        else {
            return result;
        }
    });
}
// TODO@joh
// merge this into above function to make we always
// use the same provider for resolving and renamin
function resolveInitialRenameValue(model, position) {
    var first = RenameProviderRegistry.ordered(model)[0];
    if (!first || typeof first.resolveInitialRenameValue !== 'function') {
        return TPromise.as(null);
    }
    //Use first rename provider so that we always use the same for resolving the location and for the actual rename
    return asWinJsPromise(function (token) { return first.resolveInitialRenameValue(model, position, token); }).then(function (result) {
        return !result ? undefined : result;
    }, function (err) {
        onUnexpectedExternalError(err);
        return TPromise.wrapError(new Error('provider failed'));
    });
}
// ---  register actions and commands
var CONTEXT_RENAME_INPUT_VISIBLE = new RawContextKey('renameInputVisible', false);
var RenameController = /** @class */ (function () {
    function RenameController(editor, _notificationService, _textModelResolverService, _progressService, contextKeyService, themeService, _fileService) {
        this.editor = editor;
        this._notificationService = _notificationService;
        this._textModelResolverService = _textModelResolverService;
        this._progressService = _progressService;
        this._fileService = _fileService;
        this._renameInputField = new RenameInputField(editor, themeService);
        this._renameInputVisible = CONTEXT_RENAME_INPUT_VISIBLE.bindTo(contextKeyService);
    }
    RenameController.get = function (editor) {
        return editor.getContribution(RenameController.ID);
    };
    RenameController.prototype.dispose = function () {
        this._renameInputField.dispose();
    };
    RenameController.prototype.getId = function () {
        return RenameController.ID;
    };
    RenameController.prototype.run = function () {
        return __awaiter(this, void 0, TPromise, function () {
            var _this = this;
            var selection, lineNumber, selectionStart, selectionEnd, wordRange, word, initialValue, wordAtPosition;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        selection = this.editor.getSelection();
                        lineNumber = selection.startLineNumber, selectionStart = 0, selectionEnd = 0;
                        return [4 /*yield*/, resolveInitialRenameValue(this.editor.getModel(), this.editor.getPosition())];
                    case 1:
                        initialValue = _a.sent();
                        if (initialValue) {
                            lineNumber = initialValue.range.startLineNumber;
                            if (initialValue.text) {
                                word = initialValue.text;
                            }
                            else {
                                word = this.editor.getModel().getValueInRange(initialValue.range);
                            }
                            selectionEnd = word.length;
                            if (!selection.isEmpty() && selection.startLineNumber === selection.endLineNumber) {
                                selectionStart = Math.max(0, selection.startColumn - initialValue.range.startColumn);
                                selectionEnd = Math.min(initialValue.range.endColumn, selection.endColumn) - initialValue.range.startColumn;
                            }
                            wordRange = new Range(lineNumber, initialValue.range.startColumn, lineNumber, initialValue.range.endColumn);
                        }
                        else {
                            wordAtPosition = this.editor.getModel().getWordAtPosition(selection.getStartPosition());
                            if (!wordAtPosition) {
                                return [2 /*return*/, undefined];
                            }
                            word = wordAtPosition.word;
                            selectionEnd = word.length;
                            if (!selection.isEmpty() && selection.startLineNumber === selection.endLineNumber) {
                                selectionStart = Math.max(0, selection.startColumn - wordAtPosition.startColumn);
                                selectionEnd = Math.min(wordAtPosition.endColumn, selection.endColumn) - wordAtPosition.startColumn;
                            }
                            wordRange = new Range(lineNumber, wordAtPosition.startColumn, lineNumber, wordAtPosition.endColumn);
                        }
                        this._renameInputVisible.set(true);
                        return [2 /*return*/, this._renameInputField.getInput(wordRange, word, selectionStart, selectionEnd).then(function (newName) {
                                _this._renameInputVisible.reset();
                                _this.editor.focus();
                                var edit = new BulkEdit(_this.editor, null, _this._textModelResolverService, _this._fileService);
                                var state = new EditorState(_this.editor, 4 /* Position */ | 1 /* Value */ | 2 /* Selection */ | 8 /* Scroll */);
                                var renameOperation = rename(_this.editor.getModel(), _this.editor.getPosition(), newName).then(function (result) {
                                    if (result.rejectReason) {
                                        if (state.validate(_this.editor)) {
                                            MessageController.get(_this.editor).showMessage(result.rejectReason, _this.editor.getPosition());
                                        }
                                        else {
                                            _this._notificationService.info(result.rejectReason);
                                        }
                                        return undefined;
                                    }
                                    edit.add(result.edits);
                                    return edit.perform().then(function (selection) {
                                        if (selection) {
                                            _this.editor.setSelection(selection);
                                        }
                                        // alert
                                        alert(nls.localize('aria', "Successfully renamed '{0}' to '{1}'. Summary: {2}", word, newName, edit.ariaMessage()));
                                    });
                                }, function (err) {
                                    _this._notificationService.error(nls.localize('rename.failed', "Rename failed to execute."));
                                    return TPromise.wrapError(err);
                                });
                                _this._progressService.showWhile(renameOperation, 250);
                                return renameOperation;
                            }, function (err) {
                                _this._renameInputVisible.reset();
                                _this.editor.focus();
                                if (!isPromiseCanceledError(err)) {
                                    return TPromise.wrapError(err);
                                }
                                return undefined;
                            })];
                }
            });
        });
    };
    RenameController.prototype.acceptRenameInput = function () {
        this._renameInputField.acceptInput();
    };
    RenameController.prototype.cancelRenameInput = function () {
        this._renameInputField.cancelInput();
    };
    RenameController.ID = 'editor.contrib.renameController';
    RenameController = __decorate([
        __param(1, INotificationService),
        __param(2, ITextModelService),
        __param(3, IProgressService),
        __param(4, IContextKeyService),
        __param(5, IThemeService),
        __param(6, optional(IFileService))
    ], RenameController);
    return RenameController;
}());
// ---- action implementation
var RenameAction = /** @class */ (function (_super) {
    __extends(RenameAction, _super);
    function RenameAction() {
        return _super.call(this, {
            id: 'editor.action.rename',
            label: nls.localize('rename.label', "Rename Symbol"),
            alias: 'Rename Symbol',
            precondition: ContextKeyExpr.and(EditorContextKeys.writable, EditorContextKeys.hasRenameProvider),
            kbOpts: {
                kbExpr: EditorContextKeys.textFocus,
                primary: 60 /* F2 */
            },
            menuOpts: {
                group: '1_modification',
                order: 1.1
            }
        }) || this;
    }
    RenameAction.prototype.run = function (accessor, editor) {
        var controller = RenameController.get(editor);
        if (controller) {
            return controller.run();
        }
        return undefined;
    };
    return RenameAction;
}(EditorAction));
export { RenameAction };
registerEditorContribution(RenameController);
registerEditorAction(RenameAction);
var RenameCommand = EditorCommand.bindToContribution(RenameController.get);
registerEditorCommand(new RenameCommand({
    id: 'acceptRenameInput',
    precondition: CONTEXT_RENAME_INPUT_VISIBLE,
    handler: function (x) { return x.acceptRenameInput(); },
    kbOpts: {
        weight: KeybindingsRegistry.WEIGHT.editorContrib(99),
        kbExpr: EditorContextKeys.focus,
        primary: 3 /* Enter */
    }
}));
registerEditorCommand(new RenameCommand({
    id: 'cancelRenameInput',
    precondition: CONTEXT_RENAME_INPUT_VISIBLE,
    handler: function (x) { return x.cancelRenameInput(); },
    kbOpts: {
        weight: KeybindingsRegistry.WEIGHT.editorContrib(99),
        kbExpr: EditorContextKeys.focus,
        primary: 9 /* Escape */,
        secondary: [1024 /* Shift */ | 9 /* Escape */]
    }
}));
// ---- api bridge command
registerDefaultLanguageCommand('_executeDocumentRenameProvider', function (model, position, args) {
    var newName = args.newName;
    if (typeof newName !== 'string') {
        throw illegalArgument('newName');
    }
    return rename(model, position, newName);
});
