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
import { dispose } from '../../../base/common/lifecycle.js';
import { ICommandService } from '../../../platform/commands/common/commands.js';
import { IContextMenuService } from '../../../platform/contextview/browser/contextView.js';
import { ContextKeyExpr, IContextKeyService } from '../../../platform/contextkey/common/contextkey.js';
import { IKeybindingService } from '../../../platform/keybinding/common/keybinding.js';
import { optional } from '../../../platform/instantiation/common/instantiation.js';
import { IMarkerService } from '../../../platform/markers/common/markers.js';
import { EditorContextKeys } from '../../common/editorContextKeys.js';
import { registerEditorAction, registerEditorContribution, EditorAction, EditorCommand, registerEditorCommand } from '../../browser/editorExtensions.js';
import { QuickFixContextMenu } from './quickFixWidget.js';
import { LightBulbWidget } from './lightBulbWidget.js';
import { QuickFixModel } from './quickFixModel.js';
import { CodeActionKind, CodeActionAutoApply } from './codeActionTrigger.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { BulkEdit } from '../../browser/services/bulkEdit.js';
import { IFileService } from '../../../platform/files/common/files.js';
import { ITextModelService } from '../../common/services/resolverService.js';
var QuickFixController = /** @class */ (function () {
    function QuickFixController(editor, markerService, contextKeyService, _commandService, contextMenuService, _keybindingService, _textModelService, _fileService) {
        var _this = this;
        this._commandService = _commandService;
        this._keybindingService = _keybindingService;
        this._textModelService = _textModelService;
        this._fileService = _fileService;
        this._disposables = [];
        this._editor = editor;
        this._model = new QuickFixModel(this._editor, markerService);
        this._quickFixContextMenu = new QuickFixContextMenu(editor, contextMenuService, function (action) { return _this._onApplyCodeAction(action); });
        this._lightBulbWidget = new LightBulbWidget(editor);
        this._updateLightBulbTitle();
        this._disposables.push(this._quickFixContextMenu.onDidExecuteCodeAction(function (_) { return _this._model.trigger({ type: 'auto' }); }), this._lightBulbWidget.onClick(this._handleLightBulbSelect, this), this._model.onDidChangeFixes(function (e) { return _this._onQuickFixEvent(e); }), this._keybindingService.onDidUpdateKeybindings(this._updateLightBulbTitle, this));
    }
    QuickFixController.get = function (editor) {
        return editor.getContribution(QuickFixController.ID);
    };
    QuickFixController.prototype.dispose = function () {
        this._model.dispose();
        dispose(this._disposables);
    };
    QuickFixController.prototype._onQuickFixEvent = function (e) {
        var _this = this;
        if (e && e.trigger.kind) {
            // Triggered for specific scope
            // Apply if we only have one action or requested autoApply, otherwise show menu
            e.fixes.then(function (fixes) {
                if (e.trigger.autoApply === CodeActionAutoApply.First || (e.trigger.autoApply === CodeActionAutoApply.IfSingle && fixes.length === 1)) {
                    _this._onApplyCodeAction(fixes[0]);
                }
                else {
                    _this._quickFixContextMenu.show(e.fixes, e.position);
                }
            });
            return;
        }
        if (e && e.trigger.type === 'manual') {
            this._quickFixContextMenu.show(e.fixes, e.position);
        }
        else if (e && e.fixes) {
            // auto magically triggered
            // * update an existing list of code actions
            // * manage light bulb
            if (this._quickFixContextMenu.isVisible) {
                this._quickFixContextMenu.show(e.fixes, e.position);
            }
            else {
                this._lightBulbWidget.model = e;
            }
        }
        else {
            this._lightBulbWidget.hide();
        }
    };
    QuickFixController.prototype.getId = function () {
        return QuickFixController.ID;
    };
    QuickFixController.prototype._handleLightBulbSelect = function (coords) {
        this._quickFixContextMenu.show(this._lightBulbWidget.model.fixes, coords);
    };
    QuickFixController.prototype.triggerFromEditorSelection = function () {
        this._model.trigger({ type: 'manual' });
    };
    QuickFixController.prototype.triggerCodeActionFromEditorSelection = function (kind, autoApply) {
        this._model.trigger({ type: 'manual', kind: kind, autoApply: autoApply });
    };
    QuickFixController.prototype._updateLightBulbTitle = function () {
        var kb = this._keybindingService.lookupKeybinding(QuickFixAction.Id);
        var title;
        if (kb) {
            title = nls.localize('quickFixWithKb', "Show Fixes ({0})", kb.getLabel());
        }
        else {
            title = nls.localize('quickFix', "Show Fixes");
        }
        this._lightBulbWidget.title = title;
    };
    QuickFixController.prototype._onApplyCodeAction = function (action) {
        return __awaiter(this, void 0, TPromise, function () {
            var _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!action.edit) return [3 /*break*/, 2];
                        return [4 /*yield*/, BulkEdit.perform(action.edit.edits, this._textModelService, this._fileService, this._editor)];
                    case 1:
                        _b.sent();
                        _b.label = 2;
                    case 2:
                        if (!action.command) return [3 /*break*/, 4];
                        return [4 /*yield*/, (_a = this._commandService).executeCommand.apply(_a, [action.command.id].concat(action.command.arguments))];
                    case 3:
                        _b.sent();
                        _b.label = 4;
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    QuickFixController.ID = 'editor.contrib.quickFixController';
    QuickFixController = __decorate([
        __param(1, IMarkerService),
        __param(2, IContextKeyService),
        __param(3, ICommandService),
        __param(4, IContextMenuService),
        __param(5, IKeybindingService),
        __param(6, ITextModelService),
        __param(7, optional(IFileService))
    ], QuickFixController);
    return QuickFixController;
}());
export { QuickFixController };
var QuickFixAction = /** @class */ (function (_super) {
    __extends(QuickFixAction, _super);
    function QuickFixAction() {
        return _super.call(this, {
            id: QuickFixAction.Id,
            label: nls.localize('quickfix.trigger.label', "Quick Fix"),
            alias: 'Quick Fix',
            precondition: ContextKeyExpr.and(EditorContextKeys.writable, EditorContextKeys.hasCodeActionsProvider),
            kbOpts: {
                kbExpr: EditorContextKeys.textFocus,
                primary: 2048 /* CtrlCmd */ | 84 /* US_DOT */
            }
        }) || this;
    }
    QuickFixAction.prototype.run = function (accessor, editor) {
        var controller = QuickFixController.get(editor);
        if (controller) {
            controller.triggerFromEditorSelection();
        }
    };
    QuickFixAction.Id = 'editor.action.quickFix';
    return QuickFixAction;
}(EditorAction));
export { QuickFixAction };
var CodeActionCommandArgs = /** @class */ (function () {
    function CodeActionCommandArgs(kind, apply) {
        this.kind = kind;
        this.apply = apply;
    }
    CodeActionCommandArgs.fromUser = function (arg) {
        if (!arg || typeof arg !== 'object') {
            return new CodeActionCommandArgs(CodeActionKind.Empty, CodeActionAutoApply.IfSingle);
        }
        return new CodeActionCommandArgs(CodeActionCommandArgs.getKindFromUser(arg), CodeActionCommandArgs.getApplyFromUser(arg));
    };
    CodeActionCommandArgs.getApplyFromUser = function (arg) {
        switch (typeof arg.apply === 'string' ? arg.apply.toLowerCase() : '') {
            case 'first':
                return CodeActionAutoApply.First;
            case 'never':
                return CodeActionAutoApply.Never;
            case 'ifsingle':
            default:
                return CodeActionAutoApply.IfSingle;
        }
    };
    CodeActionCommandArgs.getKindFromUser = function (arg) {
        return typeof arg.kind === 'string'
            ? new CodeActionKind(arg.kind)
            : CodeActionKind.Empty;
    };
    return CodeActionCommandArgs;
}());
var CodeActionCommand = /** @class */ (function (_super) {
    __extends(CodeActionCommand, _super);
    function CodeActionCommand() {
        return _super.call(this, {
            id: CodeActionCommand.Id,
            precondition: ContextKeyExpr.and(EditorContextKeys.writable, EditorContextKeys.hasCodeActionsProvider)
        }) || this;
    }
    CodeActionCommand.prototype.runEditorCommand = function (accessor, editor, userArg) {
        var controller = QuickFixController.get(editor);
        if (controller) {
            var args = CodeActionCommandArgs.fromUser(userArg);
            controller.triggerCodeActionFromEditorSelection(args.kind, args.apply);
        }
    };
    CodeActionCommand.Id = 'editor.action.codeAction';
    return CodeActionCommand;
}(EditorCommand));
export { CodeActionCommand };
var RefactorAction = /** @class */ (function (_super) {
    __extends(RefactorAction, _super);
    function RefactorAction() {
        return _super.call(this, {
            id: RefactorAction.Id,
            label: nls.localize('refactor.label', "Refactor"),
            alias: 'Refactor',
            precondition: ContextKeyExpr.and(EditorContextKeys.writable, EditorContextKeys.hasCodeActionsProvider),
            kbOpts: {
                kbExpr: EditorContextKeys.textFocus,
                primary: 256 /* WinCtrl */ | 1024 /* Shift */ | 48 /* KEY_R */
            }
        }) || this;
    }
    RefactorAction.prototype.run = function (accessor, editor) {
        var controller = QuickFixController.get(editor);
        if (controller) {
            controller.triggerCodeActionFromEditorSelection(CodeActionKind.Refactor, CodeActionAutoApply.Never);
        }
    };
    RefactorAction.Id = 'editor.action.refactor';
    return RefactorAction;
}(EditorAction));
export { RefactorAction };
registerEditorContribution(QuickFixController);
registerEditorAction(QuickFixAction);
registerEditorAction(RefactorAction);
registerEditorCommand(new CodeActionCommand());
