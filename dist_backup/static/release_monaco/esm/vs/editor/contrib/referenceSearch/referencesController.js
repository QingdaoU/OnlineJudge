/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
import * as nls from '../../../nls.js';
import { onUnexpectedError } from '../../../base/common/errors.js';
import { dispose } from '../../../base/common/lifecycle.js';
import { IEditorService } from '../../../platform/editor/common/editor.js';
import { IInstantiationService, optional } from '../../../platform/instantiation/common/instantiation.js';
import { IContextKeyService, RawContextKey } from '../../../platform/contextkey/common/contextkey.js';
import { IConfigurationService } from '../../../platform/configuration/common/configuration.js';
import { IWorkspaceContextService } from '../../../platform/workspace/common/workspace.js';
import { IStorageService } from '../../../platform/storage/common/storage.js';
import { registerEditorContribution } from '../../browser/editorExtensions.js';
import { ReferenceWidget } from './referencesWidget.js';
import { ITextModelService } from '../../common/services/resolverService.js';
import { IThemeService } from '../../../platform/theme/common/themeService.js';
import { Position } from '../../common/core/position.js';
import { IEnvironmentService } from '../../../platform/environment/common/environment.js';
import { INotificationService } from '../../../platform/notification/common/notification.js';
export var ctxReferenceSearchVisible = new RawContextKey('referenceSearchVisible', false);
var ReferencesController = /** @class */ (function () {
    function ReferencesController(editor, contextKeyService, _editorService, _textModelResolverService, _notificationService, _instantiationService, _contextService, _storageService, _themeService, _configurationService, _environmentService) {
        this._editorService = _editorService;
        this._textModelResolverService = _textModelResolverService;
        this._notificationService = _notificationService;
        this._instantiationService = _instantiationService;
        this._contextService = _contextService;
        this._storageService = _storageService;
        this._themeService = _themeService;
        this._configurationService = _configurationService;
        this._environmentService = _environmentService;
        this._requestIdPool = 0;
        this._disposables = [];
        this._ignoreModelChangeEvent = false;
        this._editor = editor;
        this._referenceSearchVisible = ctxReferenceSearchVisible.bindTo(contextKeyService);
    }
    ReferencesController.get = function (editor) {
        return editor.getContribution(ReferencesController.ID);
    };
    ReferencesController.prototype.getId = function () {
        return ReferencesController.ID;
    };
    ReferencesController.prototype.dispose = function () {
        if (this._widget) {
            this._widget.dispose();
            this._widget = null;
        }
        this._editor = null;
    };
    ReferencesController.prototype.toggleWidget = function (range, modelPromise, options) {
        var _this = this;
        // close current widget and return early is position didn't change
        var widgetPosition;
        if (this._widget) {
            widgetPosition = this._widget.position;
        }
        this.closeWidget();
        if (!!widgetPosition && range.containsPosition(widgetPosition)) {
            return null;
        }
        this._referenceSearchVisible.set(true);
        // close the widget on model/mode changes
        this._disposables.push(this._editor.onDidChangeModelLanguage(function () { _this.closeWidget(); }));
        this._disposables.push(this._editor.onDidChangeModel(function () {
            if (!_this._ignoreModelChangeEvent) {
                _this.closeWidget();
            }
        }));
        var storageKey = 'peekViewLayout';
        var data = JSON.parse(this._storageService.get(storageKey, undefined, '{}'));
        this._widget = new ReferenceWidget(this._editor, data, this._textModelResolverService, this._contextService, this._themeService, this._instantiationService, this._environmentService);
        this._widget.setTitle(nls.localize('labelLoading', "Loading..."));
        this._widget.show(range);
        this._disposables.push(this._widget.onDidClose(function () {
            modelPromise.cancel();
            _this._storageService.store(storageKey, JSON.stringify(_this._widget.layoutData));
            _this._widget = null;
            _this.closeWidget();
        }));
        this._disposables.push(this._widget.onDidSelectReference(function (event) {
            var element = event.element, kind = event.kind;
            switch (kind) {
                case 'open':
                    if (event.source === 'editor'
                        && _this._configurationService.getValue('editor.stablePeek')) {
                        // when stable peek is configured we don't close
                        // the peek window on selecting the editor
                        break;
                    }
                case 'side':
                    _this.openReference(element, kind === 'side');
                    break;
                case 'goto':
                    if (options.onGoto) {
                        options.onGoto(element);
                    }
                    else {
                        _this._gotoReference(element);
                    }
                    break;
            }
        }));
        var requestId = ++this._requestIdPool;
        modelPromise.then(function (model) {
            // still current request? widget still open?
            if (requestId !== _this._requestIdPool || !_this._widget) {
                return undefined;
            }
            if (_this._model) {
                _this._model.dispose();
            }
            _this._model = model;
            // show widget
            return _this._widget.setModel(_this._model).then(function () {
                // set title
                _this._widget.setMetaTitle(options.getMetaTitle(_this._model));
                // set 'best' selection
                var uri = _this._editor.getModel().uri;
                var pos = new Position(range.startLineNumber, range.startColumn);
                var selection = _this._model.nearestReference(uri, pos);
                if (selection) {
                    return _this._widget.setSelection(selection);
                }
                return undefined;
            });
        }, function (error) {
            _this._notificationService.error(error);
        });
    };
    ReferencesController.prototype.closeWidget = function () {
        if (this._widget) {
            this._widget.dispose();
            this._widget = null;
        }
        this._referenceSearchVisible.reset();
        this._disposables = dispose(this._disposables);
        if (this._model) {
            this._model.dispose();
            this._model = null;
        }
        this._editor.focus();
        this._requestIdPool += 1; // Cancel pending requests
    };
    ReferencesController.prototype._gotoReference = function (ref) {
        var _this = this;
        this._widget.hide();
        this._ignoreModelChangeEvent = true;
        var uri = ref.uri, range = ref.range;
        this._editorService.openEditor({
            resource: uri,
            options: { selection: range }
        }).done(function (openedEditor) {
            _this._ignoreModelChangeEvent = false;
            if (!openedEditor || openedEditor.getControl() !== _this._editor) {
                // TODO@Alex TODO@Joh
                // when opening the current reference we might end up
                // in a different editor instance. that means we also have
                // a different instance of this reference search controller
                // and cannot hold onto the widget (which likely doesn't
                // exist). Instead of bailing out we should find the
                // 'sister' action and pass our current model on to it.
                _this.closeWidget();
                return;
            }
            _this._widget.show(range);
            _this._widget.focus();
        }, function (err) {
            _this._ignoreModelChangeEvent = false;
            onUnexpectedError(err);
        });
    };
    ReferencesController.prototype.openReference = function (ref, sideBySide) {
        var uri = ref.uri, range = ref.range;
        this._editorService.openEditor({
            resource: uri,
            options: { selection: range }
        }, sideBySide);
        // clear stage
        if (!sideBySide) {
            this.closeWidget();
        }
    };
    ReferencesController.ID = 'editor.contrib.referencesController';
    ReferencesController = __decorate([
        __param(1, IContextKeyService),
        __param(2, IEditorService),
        __param(3, ITextModelService),
        __param(4, INotificationService),
        __param(5, IInstantiationService),
        __param(6, IWorkspaceContextService),
        __param(7, IStorageService),
        __param(8, IThemeService),
        __param(9, IConfigurationService),
        __param(10, optional(IEnvironmentService))
    ], ReferencesController);
    return ReferencesController;
}());
export { ReferencesController };
registerEditorContribution(ReferencesController);
