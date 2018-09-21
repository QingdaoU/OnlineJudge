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
import './media/editor.css';
import './media/tokens.css';
import { onUnexpectedError } from '../../../base/common/errors.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import * as dom from '../../../base/browser/dom.js';
import { IInstantiationService } from '../../../platform/instantiation/common/instantiation.js';
import { ICommandService } from '../../../platform/commands/common/commands.js';
import { IContextKeyService } from '../../../platform/contextkey/common/contextkey.js';
import { CommonCodeEditor } from '../../common/commonCodeEditor.js';
import { EditorExtensionsRegistry } from '../editorExtensions.js';
import { ICodeEditorService } from '../services/codeEditorService.js';
import { Configuration } from '../config/configuration.js';
import { View } from '../view/viewImpl.js';
import { Disposable } from '../../../base/common/lifecycle.js';
import { Emitter } from '../../../base/common/event.js';
import { InternalEditorAction } from '../../common/editorAction.js';
import { IThemeService, registerThemingParticipant } from '../../../platform/theme/common/themeService.js';
import { editorErrorForeground, editorErrorBorder, editorWarningForeground, editorWarningBorder, editorInfoBorder, editorInfoForeground } from '../../common/view/editorColorRegistry.js';
import { ClassName } from '../../common/model/intervalTree.js';
var CodeEditorWidget = /** @class */ (function (_super) {
    __extends(CodeEditorWidget, _super);
    function CodeEditorWidget(domElement, options, instantiationService, codeEditorService, commandService, contextKeyService, themeService) {
        var _this = _super.call(this, domElement, options, instantiationService, contextKeyService) || this;
        _this._onMouseUp = _this._register(new Emitter());
        _this.onMouseUp = _this._onMouseUp.event;
        _this._onMouseDown = _this._register(new Emitter());
        _this.onMouseDown = _this._onMouseDown.event;
        _this._onMouseDrag = _this._register(new Emitter());
        _this.onMouseDrag = _this._onMouseDrag.event;
        _this._onMouseDrop = _this._register(new Emitter());
        _this.onMouseDrop = _this._onMouseDrop.event;
        _this._onContextMenu = _this._register(new Emitter());
        _this.onContextMenu = _this._onContextMenu.event;
        _this._onMouseMove = _this._register(new Emitter());
        _this.onMouseMove = _this._onMouseMove.event;
        _this._onMouseLeave = _this._register(new Emitter());
        _this.onMouseLeave = _this._onMouseLeave.event;
        _this._onKeyUp = _this._register(new Emitter());
        _this.onKeyUp = _this._onKeyUp.event;
        _this._onKeyDown = _this._register(new Emitter());
        _this.onKeyDown = _this._onKeyDown.event;
        _this._onDidScrollChange = _this._register(new Emitter());
        _this.onDidScrollChange = _this._onDidScrollChange.event;
        _this._onDidChangeViewZones = _this._register(new Emitter());
        _this.onDidChangeViewZones = _this._onDidChangeViewZones.event;
        _this._codeEditorService = codeEditorService;
        _this._commandService = commandService;
        _this._themeService = themeService;
        _this._focusTracker = new CodeEditorWidgetFocusTracker(domElement);
        _this._focusTracker.onChange(function () {
            var hasFocus = _this._focusTracker.hasFocus();
            if (hasFocus) {
                _this._onDidFocusEditor.fire();
            }
            else {
                _this._onDidBlurEditor.fire();
            }
        });
        _this.contentWidgets = {};
        _this.overlayWidgets = {};
        var contributions = _this._getContributions();
        for (var i = 0, len = contributions.length; i < len; i++) {
            var ctor = contributions[i];
            try {
                var contribution = _this._instantiationService.createInstance(ctor, _this);
                _this._contributions[contribution.getId()] = contribution;
            }
            catch (err) {
                onUnexpectedError(err);
            }
        }
        _this._getActions().forEach(function (action) {
            var internalAction = new InternalEditorAction(action.id, action.label, action.alias, action.precondition, function () {
                return _this._instantiationService.invokeFunction(function (accessor) {
                    return action.runEditorCommand(accessor, _this, null);
                });
            }, _this._contextKeyService);
            _this._actions[internalAction.id] = internalAction;
        });
        _this._codeEditorService.addCodeEditor(_this);
        return _this;
    }
    CodeEditorWidget.prototype._createConfiguration = function (options) {
        return new Configuration(options, this.domElement);
    };
    CodeEditorWidget.prototype.dispose = function () {
        this._codeEditorService.removeCodeEditor(this);
        this.contentWidgets = {};
        this.overlayWidgets = {};
        this._focusTracker.dispose();
        _super.prototype.dispose.call(this);
    };
    CodeEditorWidget.prototype.createOverviewRuler = function (cssClassName) {
        return this._view.createOverviewRuler(cssClassName);
    };
    CodeEditorWidget.prototype.getDomNode = function () {
        if (!this.hasView) {
            return null;
        }
        return this._view.domNode.domNode;
    };
    CodeEditorWidget.prototype.delegateVerticalScrollbarMouseDown = function (browserEvent) {
        if (!this.hasView) {
            return;
        }
        this._view.delegateVerticalScrollbarMouseDown(browserEvent);
    };
    CodeEditorWidget.prototype.layout = function (dimension) {
        this._configuration.observeReferenceElement(dimension);
        this.render();
    };
    CodeEditorWidget.prototype.focus = function () {
        if (!this.hasView) {
            return;
        }
        this._view.focus();
    };
    CodeEditorWidget.prototype.isFocused = function () {
        return this.hasView && this._view.isFocused();
    };
    CodeEditorWidget.prototype.hasWidgetFocus = function () {
        return this._focusTracker && this._focusTracker.hasFocus();
    };
    CodeEditorWidget.prototype.addContentWidget = function (widget) {
        var widgetData = {
            widget: widget,
            position: widget.getPosition()
        };
        if (this.contentWidgets.hasOwnProperty(widget.getId())) {
            console.warn('Overwriting a content widget with the same id.');
        }
        this.contentWidgets[widget.getId()] = widgetData;
        if (this.hasView) {
            this._view.addContentWidget(widgetData);
        }
    };
    CodeEditorWidget.prototype.layoutContentWidget = function (widget) {
        var widgetId = widget.getId();
        if (this.contentWidgets.hasOwnProperty(widgetId)) {
            var widgetData = this.contentWidgets[widgetId];
            widgetData.position = widget.getPosition();
            if (this.hasView) {
                this._view.layoutContentWidget(widgetData);
            }
        }
    };
    CodeEditorWidget.prototype.removeContentWidget = function (widget) {
        var widgetId = widget.getId();
        if (this.contentWidgets.hasOwnProperty(widgetId)) {
            var widgetData = this.contentWidgets[widgetId];
            delete this.contentWidgets[widgetId];
            if (this.hasView) {
                this._view.removeContentWidget(widgetData);
            }
        }
    };
    CodeEditorWidget.prototype.addOverlayWidget = function (widget) {
        var widgetData = {
            widget: widget,
            position: widget.getPosition()
        };
        if (this.overlayWidgets.hasOwnProperty(widget.getId())) {
            console.warn('Overwriting an overlay widget with the same id.');
        }
        this.overlayWidgets[widget.getId()] = widgetData;
        if (this.hasView) {
            this._view.addOverlayWidget(widgetData);
        }
    };
    CodeEditorWidget.prototype.layoutOverlayWidget = function (widget) {
        var widgetId = widget.getId();
        if (this.overlayWidgets.hasOwnProperty(widgetId)) {
            var widgetData = this.overlayWidgets[widgetId];
            widgetData.position = widget.getPosition();
            if (this.hasView) {
                this._view.layoutOverlayWidget(widgetData);
            }
        }
    };
    CodeEditorWidget.prototype.removeOverlayWidget = function (widget) {
        var widgetId = widget.getId();
        if (this.overlayWidgets.hasOwnProperty(widgetId)) {
            var widgetData = this.overlayWidgets[widgetId];
            delete this.overlayWidgets[widgetId];
            if (this.hasView) {
                this._view.removeOverlayWidget(widgetData);
            }
        }
    };
    CodeEditorWidget.prototype.changeViewZones = function (callback) {
        if (!this.hasView) {
            return;
        }
        var hasChanges = this._view.change(callback);
        if (hasChanges) {
            this._onDidChangeViewZones.fire();
        }
    };
    CodeEditorWidget.prototype.getTargetAtClientPoint = function (clientX, clientY) {
        if (!this.hasView) {
            return null;
        }
        return this._view.getTargetAtClientPoint(clientX, clientY);
    };
    CodeEditorWidget.prototype.getScrolledVisiblePosition = function (rawPosition) {
        if (!this.hasView) {
            return null;
        }
        var position = this.model.validatePosition(rawPosition);
        var layoutInfo = this._configuration.editor.layoutInfo;
        var top = this._getVerticalOffsetForPosition(position.lineNumber, position.column) - this.getScrollTop();
        var left = this._view.getOffsetForColumn(position.lineNumber, position.column) + layoutInfo.glyphMarginWidth + layoutInfo.lineNumbersWidth + layoutInfo.decorationsWidth - this.getScrollLeft();
        return {
            top: top,
            left: left,
            height: this._configuration.editor.lineHeight
        };
    };
    CodeEditorWidget.prototype.getOffsetForColumn = function (lineNumber, column) {
        if (!this.hasView) {
            return -1;
        }
        return this._view.getOffsetForColumn(lineNumber, column);
    };
    CodeEditorWidget.prototype.render = function () {
        if (!this.hasView) {
            return;
        }
        this._view.render(true, false);
    };
    CodeEditorWidget.prototype.applyFontInfo = function (target) {
        Configuration.applyFontInfoSlow(target, this._configuration.editor.fontInfo);
    };
    CodeEditorWidget.prototype._attachModel = function (model) {
        this._view = null;
        _super.prototype._attachModel.call(this, model);
        if (this._view) {
            this.domElement.appendChild(this._view.domNode.domNode);
            var keys = Object.keys(this.contentWidgets);
            for (var i = 0, len = keys.length; i < len; i++) {
                var widgetId = keys[i];
                this._view.addContentWidget(this.contentWidgets[widgetId]);
            }
            keys = Object.keys(this.overlayWidgets);
            for (var i = 0, len = keys.length; i < len; i++) {
                var widgetId = keys[i];
                this._view.addOverlayWidget(this.overlayWidgets[widgetId]);
            }
            this._view.render(false, true);
            this.hasView = true;
            this._view.domNode.domNode.setAttribute('data-uri', model.uri.toString());
        }
    };
    CodeEditorWidget.prototype._scheduleAtNextAnimationFrame = function (callback) {
        return dom.scheduleAtNextAnimationFrame(callback);
    };
    CodeEditorWidget.prototype._createView = function () {
        var _this = this;
        this._view = new View(this._commandService, this._configuration, this._themeService, this.viewModel, this.cursor, function (editorCommand, args) {
            if (!_this.cursor) {
                return;
            }
            editorCommand.runCoreEditorCommand(_this.cursor, args);
        });
        var viewEventBus = this._view.getInternalEventBus();
        viewEventBus.onDidGainFocus = function () {
            _this._onDidFocusEditorText.fire();
            // In IE, the focus is not synchronous, so we give it a little help
            _this._onDidFocusEditor.fire();
        };
        viewEventBus.onDidScroll = function (e) { return _this._onDidScrollChange.fire(e); };
        viewEventBus.onDidLoseFocus = function () { return _this._onDidBlurEditorText.fire(); };
        viewEventBus.onContextMenu = function (e) { return _this._onContextMenu.fire(e); };
        viewEventBus.onMouseDown = function (e) { return _this._onMouseDown.fire(e); };
        viewEventBus.onMouseUp = function (e) { return _this._onMouseUp.fire(e); };
        viewEventBus.onMouseDrag = function (e) { return _this._onMouseDrag.fire(e); };
        viewEventBus.onMouseDrop = function (e) { return _this._onMouseDrop.fire(e); };
        viewEventBus.onKeyUp = function (e) { return _this._onKeyUp.fire(e); };
        viewEventBus.onMouseMove = function (e) { return _this._onMouseMove.fire(e); };
        viewEventBus.onMouseLeave = function (e) { return _this._onMouseLeave.fire(e); };
        viewEventBus.onKeyDown = function (e) { return _this._onKeyDown.fire(e); };
    };
    CodeEditorWidget.prototype.restoreViewState = function (s) {
        _super.prototype.restoreViewState.call(this, s);
        if (!this.cursor || !this.hasView) {
            return;
        }
        if (s && s.cursorState && s.viewState) {
            this._view.restoreState(this.viewModel.viewLayout.reduceRestoreState(s.viewState));
        }
    };
    CodeEditorWidget.prototype._detachModel = function () {
        var removeDomNode = null;
        if (this._view) {
            this._view.dispose();
            removeDomNode = this._view.domNode.domNode;
            this._view = null;
        }
        var result = _super.prototype._detachModel.call(this);
        if (removeDomNode) {
            this.domElement.removeChild(removeDomNode);
        }
        return result;
    };
    // BEGIN decorations
    CodeEditorWidget.prototype._registerDecorationType = function (key, options, parentTypeKey) {
        this._codeEditorService.registerDecorationType(key, options, parentTypeKey);
    };
    CodeEditorWidget.prototype._removeDecorationType = function (key) {
        this._codeEditorService.removeDecorationType(key);
    };
    CodeEditorWidget.prototype._resolveDecorationOptions = function (typeKey, writable) {
        return this._codeEditorService.resolveDecorationOptions(typeKey, writable);
    };
    // END decorations
    CodeEditorWidget.prototype._triggerEditorCommand = function (source, handlerId, payload) {
        var command = EditorExtensionsRegistry.getEditorCommand(handlerId);
        if (command) {
            payload = payload || {};
            payload.source = source;
            TPromise.as(command.runEditorCommand(null, this, payload)).done(null, onUnexpectedError);
            return true;
        }
        return false;
    };
    CodeEditorWidget = __decorate([
        __param(2, IInstantiationService),
        __param(3, ICodeEditorService),
        __param(4, ICommandService),
        __param(5, IContextKeyService),
        __param(6, IThemeService)
    ], CodeEditorWidget);
    return CodeEditorWidget;
}(CommonCodeEditor));
export { CodeEditorWidget };
var CodeEditorWidgetFocusTracker = /** @class */ (function (_super) {
    __extends(CodeEditorWidgetFocusTracker, _super);
    function CodeEditorWidgetFocusTracker(domElement) {
        var _this = _super.call(this) || this;
        _this._onChange = _this._register(new Emitter());
        _this.onChange = _this._onChange.event;
        _this._hasFocus = false;
        _this._domFocusTracker = _this._register(dom.trackFocus(domElement));
        _this._register(_this._domFocusTracker.onDidFocus(function () {
            _this._hasFocus = true;
            _this._onChange.fire(void 0);
        }));
        _this._register(_this._domFocusTracker.onDidBlur(function () {
            _this._hasFocus = false;
            _this._onChange.fire(void 0);
        }));
        return _this;
    }
    CodeEditorWidgetFocusTracker.prototype.hasFocus = function () {
        return this._hasFocus;
    };
    return CodeEditorWidgetFocusTracker;
}(Disposable));
var squigglyStart = encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 6 3' enable-background='new 0 0 6 3' height='3' width='6'><g fill='");
var squigglyEnd = encodeURIComponent("'><polygon points='5.5,0 2.5,3 1.1,3 4.1,0'/><polygon points='4,0 6,2 6,0.6 5.4,0'/><polygon points='0,2 1,3 2.4,3 0,0.6'/></g></svg>");
function getSquigglySVGData(color) {
    return squigglyStart + encodeURIComponent(color.toString()) + squigglyEnd;
}
registerThemingParticipant(function (theme, collector) {
    var errorBorderColor = theme.getColor(editorErrorBorder);
    if (errorBorderColor) {
        collector.addRule(".monaco-editor ." + ClassName.EditorErrorDecoration + " { border-bottom: 4px double " + errorBorderColor + "; }");
    }
    var errorForeground = theme.getColor(editorErrorForeground);
    if (errorForeground) {
        collector.addRule(".monaco-editor ." + ClassName.EditorErrorDecoration + " { background: url(\"data:image/svg+xml;utf8," + getSquigglySVGData(errorForeground) + "\") repeat-x bottom left; }");
    }
    var warningBorderColor = theme.getColor(editorWarningBorder);
    if (warningBorderColor) {
        collector.addRule(".monaco-editor ." + ClassName.EditorWarningDecoration + " { border-bottom: 4px double " + warningBorderColor + "; }");
    }
    var warningForeground = theme.getColor(editorWarningForeground);
    if (warningForeground) {
        collector.addRule(".monaco-editor ." + ClassName.EditorWarningDecoration + " { background: url(\"data:image/svg+xml;utf8," + getSquigglySVGData(warningForeground) + "\") repeat-x bottom left; }");
    }
    var infoBorderColor = theme.getColor(editorInfoBorder);
    if (infoBorderColor) {
        collector.addRule(".monaco-editor ." + ClassName.EditorInfoDecoration + " { border-bottom: 4px double " + infoBorderColor + "; }");
    }
    var infoForeground = theme.getColor(editorInfoForeground);
    if (infoForeground) {
        collector.addRule(".monaco-editor ." + ClassName.EditorInfoDecoration + " { background: url(\"data:image/svg+xml;utf8," + getSquigglySVGData(infoForeground) + "\") repeat-x bottom left; }");
    }
});
