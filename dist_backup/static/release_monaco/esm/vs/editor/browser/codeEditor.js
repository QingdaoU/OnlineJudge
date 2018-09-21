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
import { IInstantiationService } from '../../platform/instantiation/common/instantiation.js';
import { ICommandService } from '../../platform/commands/common/commands.js';
import { IContextKeyService } from '../../platform/contextkey/common/contextkey.js';
import { ICodeEditorService } from './services/codeEditorService.js';
import { CodeEditorWidget } from './widget/codeEditorWidget.js';
import { EditorExtensionsRegistry } from './editorExtensions.js';
import { IThemeService } from '../../platform/theme/common/themeService.js';
var CodeEditor = /** @class */ (function (_super) {
    __extends(CodeEditor, _super);
    function CodeEditor(domElement, options, instantiationService, codeEditorService, commandService, contextKeyService, themeService) {
        return _super.call(this, domElement, options, instantiationService, codeEditorService, commandService, contextKeyService, themeService) || this;
    }
    CodeEditor.prototype._getContributions = function () {
        return EditorExtensionsRegistry.getEditorContributions();
    };
    CodeEditor.prototype._getActions = function () {
        return EditorExtensionsRegistry.getEditorActions();
    };
    CodeEditor = __decorate([
        __param(2, IInstantiationService),
        __param(3, ICodeEditorService),
        __param(4, ICommandService),
        __param(5, IContextKeyService),
        __param(6, IThemeService)
    ], CodeEditor);
    return CodeEditor;
}(CodeEditorWidget));
export { CodeEditor };
