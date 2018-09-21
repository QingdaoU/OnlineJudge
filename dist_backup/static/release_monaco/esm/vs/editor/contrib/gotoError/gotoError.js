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
import './gotoError.css';
import * as nls from '../../../nls.js';
import { Emitter } from '../../../base/common/event.js';
import { dispose } from '../../../base/common/lifecycle.js';
import Severity from '../../../base/common/severity.js';
import * as dom from '../../../base/browser/dom.js';
import { RawContextKey, IContextKeyService } from '../../../platform/contextkey/common/contextkey.js';
import { IMarkerService } from '../../../platform/markers/common/markers.js';
import { Position } from '../../common/core/position.js';
import { Range } from '../../common/core/range.js';
import * as editorCommon from '../../common/editorCommon.js';
import { registerEditorAction, registerEditorContribution, EditorAction, EditorCommand, registerEditorCommand } from '../../browser/editorExtensions.js';
import { ZoneWidget } from '../zoneWidget/zoneWidget.js';
import { registerColor, oneOf } from '../../../platform/theme/common/colorRegistry.js';
import { IThemeService } from '../../../platform/theme/common/themeService.js';
import { Color } from '../../../base/common/color.js';
import { EditorContextKeys } from '../../common/editorContextKeys.js';
import { editorErrorForeground, editorErrorBorder, editorWarningForeground, editorWarningBorder, editorInfoForeground, editorInfoBorder } from '../../common/view/editorColorRegistry.js';
import { ScrollableElement } from '../../../base/browser/ui/scrollbar/scrollableElement.js';
import { ScrollbarVisibility } from '../../../base/common/scrollable.js';
import { KeybindingsRegistry } from '../../../platform/keybinding/common/keybindingsRegistry.js';
var MarkerModel = /** @class */ (function () {
    function MarkerModel(editor, markers) {
        var _this = this;
        this._editor = editor;
        this._markers = null;
        this._nextIdx = -1;
        this._toUnbind = [];
        this._ignoreSelectionChange = false;
        this._onCurrentMarkerChanged = new Emitter();
        this._onMarkerSetChanged = new Emitter();
        this.setMarkers(markers);
        // listen on editor
        this._toUnbind.push(this._editor.onDidDispose(function () { return _this.dispose(); }));
        this._toUnbind.push(this._editor.onDidChangeCursorPosition(function () {
            if (!_this._ignoreSelectionChange) {
                _this._nextIdx = -1;
            }
        }));
    }
    Object.defineProperty(MarkerModel.prototype, "onCurrentMarkerChanged", {
        get: function () {
            return this._onCurrentMarkerChanged.event;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(MarkerModel.prototype, "onMarkerSetChanged", {
        get: function () {
            return this._onMarkerSetChanged.event;
        },
        enumerable: true,
        configurable: true
    });
    MarkerModel.prototype.setMarkers = function (markers) {
        // assign
        this._markers = markers || [];
        // sort markers
        this._markers.sort(function (left, right) { return Severity.compare(left.severity, right.severity) || Range.compareRangesUsingStarts(left, right); });
        this._nextIdx = -1;
        this._onMarkerSetChanged.fire(this);
    };
    MarkerModel.prototype.withoutWatchingEditorPosition = function (callback) {
        this._ignoreSelectionChange = true;
        try {
            callback();
        }
        finally {
            this._ignoreSelectionChange = false;
        }
    };
    MarkerModel.prototype._initIdx = function (fwd) {
        var found = false;
        var position = this._editor.getPosition();
        for (var i = 0; i < this._markers.length; i++) {
            var range = Range.lift(this._markers[i]);
            if (range.isEmpty()) {
                var word = this._editor.getModel().getWordAtPosition(range.getStartPosition());
                if (word) {
                    range = new Range(range.startLineNumber, word.startColumn, range.startLineNumber, word.endColumn);
                }
            }
            if (range.containsPosition(position) || position.isBeforeOrEqual(range.getStartPosition())) {
                this._nextIdx = i + (fwd ? 0 : -1);
                found = true;
                break;
            }
        }
        if (!found) {
            // after the last change
            this._nextIdx = fwd ? 0 : this._markers.length - 1;
        }
        if (this._nextIdx < 0) {
            this._nextIdx = this._markers.length - 1;
        }
    };
    MarkerModel.prototype.move = function (fwd) {
        if (!this.canNavigate()) {
            this._onCurrentMarkerChanged.fire(undefined);
            return;
        }
        if (this._nextIdx === -1) {
            this._initIdx(fwd);
        }
        else if (fwd) {
            this._nextIdx += 1;
            if (this._nextIdx >= this._markers.length) {
                this._nextIdx = 0;
            }
        }
        else {
            this._nextIdx -= 1;
            if (this._nextIdx < 0) {
                this._nextIdx = this._markers.length - 1;
            }
        }
        var marker = this._markers[this._nextIdx];
        this._onCurrentMarkerChanged.fire(marker);
    };
    MarkerModel.prototype.canNavigate = function () {
        return this._markers.length > 0;
    };
    MarkerModel.prototype.next = function () {
        this.move(true);
    };
    MarkerModel.prototype.previous = function () {
        this.move(false);
    };
    MarkerModel.prototype.findMarkerAtPosition = function (pos) {
        for (var _i = 0, _a = this._markers; _i < _a.length; _i++) {
            var marker = _a[_i];
            if (Range.containsPosition(marker, pos)) {
                return marker;
            }
        }
        return undefined;
    };
    Object.defineProperty(MarkerModel.prototype, "total", {
        get: function () {
            return this._markers.length;
        },
        enumerable: true,
        configurable: true
    });
    MarkerModel.prototype.indexOf = function (marker) {
        return 1 + this._markers.indexOf(marker);
    };
    MarkerModel.prototype.reveal = function () {
        var _this = this;
        if (this._nextIdx === -1) {
            return;
        }
        this.withoutWatchingEditorPosition(function () {
            var pos = new Position(_this._markers[_this._nextIdx].startLineNumber, _this._markers[_this._nextIdx].startColumn);
            _this._editor.setPosition(pos);
            _this._editor.revealPositionInCenter(pos, 0 /* Smooth */);
        });
    };
    MarkerModel.prototype.dispose = function () {
        this._toUnbind = dispose(this._toUnbind);
    };
    return MarkerModel;
}());
var MessageWidget = /** @class */ (function () {
    function MessageWidget(parent, editor) {
        var _this = this;
        this.lines = 0;
        this.longestLineLength = 0;
        this._disposables = [];
        this._editor = editor;
        this._domNode = document.createElement('span');
        this._domNode.className = 'descriptioncontainer';
        this._domNode.setAttribute('aria-live', 'assertive');
        this._domNode.setAttribute('role', 'alert');
        this._scrollable = new ScrollableElement(this._domNode, {
            horizontal: ScrollbarVisibility.Auto,
            vertical: ScrollbarVisibility.Hidden,
            useShadows: false,
            horizontalScrollbarSize: 3
        });
        dom.addClass(this._scrollable.getDomNode(), 'block');
        parent.appendChild(this._scrollable.getDomNode());
        this._disposables.push(this._scrollable.onScroll(function (e) { return _this._domNode.style.left = "-" + e.scrollLeft + "px"; }));
        this._disposables.push(this._scrollable);
    }
    MessageWidget.prototype.dispose = function () {
        dispose(this._disposables);
    };
    MessageWidget.prototype.update = function (_a) {
        var source = _a.source, message = _a.message;
        if (source) {
            this.lines = 0;
            this.longestLineLength = 0;
            var indent = new Array(source.length + 3 + 1).join(' ');
            var lines = message.split(/\r\n|\r|\n/g);
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                this.lines += 1;
                this.longestLineLength = Math.max(line.length, this.longestLineLength);
                if (i === 0) {
                    message = "[" + source + "] " + line;
                }
                else {
                    message += "\n" + indent + line;
                }
            }
        }
        else {
            this.lines = 1;
            this.longestLineLength = message.length;
        }
        this._domNode.innerText = message;
        this._editor.applyFontInfo(this._domNode);
        var width = Math.floor(this._editor.getConfiguration().fontInfo.typicalFullwidthCharacterWidth * this.longestLineLength);
        this._scrollable.setScrollDimensions({ scrollWidth: width });
    };
    MessageWidget.prototype.layout = function (height, width) {
        this._scrollable.setScrollDimensions({ width: width });
    };
    return MessageWidget;
}());
var MarkerNavigationWidget = /** @class */ (function (_super) {
    __extends(MarkerNavigationWidget, _super);
    function MarkerNavigationWidget(editor, _model, _themeService) {
        var _this = _super.call(this, editor, { showArrow: true, showFrame: true, isAccessible: true }) || this;
        _this._model = _model;
        _this._themeService = _themeService;
        _this._callOnDispose = [];
        _this._severity = Severity.Warning;
        _this._backgroundColor = Color.white;
        _this._applyTheme(_themeService.getTheme());
        _this._callOnDispose.push(_themeService.onThemeChange(_this._applyTheme.bind(_this)));
        _this.create();
        _this._wireModelAndView();
        return _this;
    }
    MarkerNavigationWidget.prototype._applyTheme = function (theme) {
        this._backgroundColor = theme.getColor(editorMarkerNavigationBackground);
        var colorId = editorMarkerNavigationError;
        if (this._severity === Severity.Warning) {
            colorId = editorMarkerNavigationWarning;
        }
        else if (this._severity === Severity.Info) {
            colorId = editorMarkerNavigationInfo;
        }
        var frameColor = theme.getColor(colorId);
        this.style({
            arrowColor: frameColor,
            frameColor: frameColor
        }); // style() will trigger _applyStyles
    };
    MarkerNavigationWidget.prototype._applyStyles = function () {
        if (this._parentContainer) {
            this._parentContainer.style.backgroundColor = this._backgroundColor.toString();
        }
        _super.prototype._applyStyles.call(this);
    };
    MarkerNavigationWidget.prototype.dispose = function () {
        this._callOnDispose = dispose(this._callOnDispose);
        _super.prototype.dispose.call(this);
    };
    MarkerNavigationWidget.prototype.focus = function () {
        this._parentContainer.focus();
    };
    MarkerNavigationWidget.prototype._fillContainer = function (container) {
        this._parentContainer = container;
        dom.addClass(container, 'marker-widget');
        this._parentContainer.tabIndex = 0;
        this._parentContainer.setAttribute('role', 'tooltip');
        this._container = document.createElement('div');
        container.appendChild(this._container);
        this._title = document.createElement('div');
        this._title.className = 'block title';
        this._container.appendChild(this._title);
        this._message = new MessageWidget(this._container, this.editor);
        this._disposables.push(this._message);
    };
    MarkerNavigationWidget.prototype.show = function (where, heightInLines) {
        _super.prototype.show.call(this, where, heightInLines);
        if (this.editor.getConfiguration().accessibilitySupport !== 1 /* Disabled */) {
            this.focus();
        }
    };
    MarkerNavigationWidget.prototype._wireModelAndView = function () {
        // listen to events
        this._model.onCurrentMarkerChanged(this.showAtMarker, this, this._callOnDispose);
        this._model.onMarkerSetChanged(this._onMarkersChanged, this, this._callOnDispose);
    };
    MarkerNavigationWidget.prototype.showAtMarker = function (marker) {
        var _this = this;
        if (!marker) {
            return;
        }
        // update:
        // * title
        // * message
        this._container.classList.remove('stale');
        this._title.innerHTML = nls.localize('title.wo_source', "({0}/{1})", this._model.indexOf(marker), this._model.total);
        this._message.update(marker);
        this._model.withoutWatchingEditorPosition(function () {
            // update frame color (only applied on 'show')
            _this._severity = marker.severity;
            _this._applyTheme(_this._themeService.getTheme());
            _this.show(new Position(marker.startLineNumber, marker.startColumn), _this.computeRequiredHeight());
        });
    };
    MarkerNavigationWidget.prototype._onMarkersChanged = function () {
        var marker = this._model.findMarkerAtPosition(this.position);
        if (marker) {
            this._container.classList.remove('stale');
            this._message.update(marker);
        }
        else {
            this._container.classList.add('stale');
        }
        this._relayout();
    };
    MarkerNavigationWidget.prototype._doLayout = function (heightInPixel, widthInPixel) {
        this._message.layout(heightInPixel, widthInPixel);
    };
    MarkerNavigationWidget.prototype._relayout = function () {
        _super.prototype._relayout.call(this, this.computeRequiredHeight());
    };
    MarkerNavigationWidget.prototype.computeRequiredHeight = function () {
        return 1 + this._message.lines;
    };
    return MarkerNavigationWidget;
}(ZoneWidget));
var MarkerNavigationAction = /** @class */ (function (_super) {
    __extends(MarkerNavigationAction, _super);
    function MarkerNavigationAction(next, opts) {
        var _this = _super.call(this, opts) || this;
        _this._isNext = next;
        return _this;
    }
    MarkerNavigationAction.prototype.run = function (accessor, editor) {
        var controller = MarkerController.get(editor);
        if (!controller) {
            return;
        }
        var model = controller.getOrCreateModel();
        if (model) {
            if (this._isNext) {
                model.next();
            }
            else {
                model.previous();
            }
            model.reveal();
        }
    };
    return MarkerNavigationAction;
}(EditorAction));
var MarkerController = /** @class */ (function () {
    function MarkerController(editor, _markerService, _contextKeyService, _themeService) {
        this._markerService = _markerService;
        this._contextKeyService = _contextKeyService;
        this._themeService = _themeService;
        this._callOnClose = [];
        this._editor = editor;
        this._markersNavigationVisible = CONTEXT_MARKERS_NAVIGATION_VISIBLE.bindTo(this._contextKeyService);
    }
    MarkerController.get = function (editor) {
        return editor.getContribution(MarkerController.ID);
    };
    MarkerController.prototype.getId = function () {
        return MarkerController.ID;
    };
    MarkerController.prototype.dispose = function () {
        this._cleanUp();
    };
    MarkerController.prototype._cleanUp = function () {
        this._markersNavigationVisible.reset();
        this._callOnClose = dispose(this._callOnClose);
        this._zone = null;
        this._model = null;
    };
    MarkerController.prototype.getOrCreateModel = function () {
        var _this = this;
        if (this._model) {
            return this._model;
        }
        var markers = this._getMarkers();
        this._model = new MarkerModel(this._editor, markers);
        this._zone = new MarkerNavigationWidget(this._editor, this._model, this._themeService);
        this._markersNavigationVisible.set(true);
        this._callOnClose.push(this._model);
        this._callOnClose.push(this._zone);
        this._callOnClose.push(this._editor.onDidChangeModel(function () { return _this._cleanUp(); }));
        this._model.onCurrentMarkerChanged(function (marker) { return !marker && _this._cleanUp(); }, undefined, this._callOnClose);
        this._markerService.onMarkerChanged(this._onMarkerChanged, this, this._callOnClose);
        return this._model;
    };
    MarkerController.prototype.closeMarkersNavigation = function () {
        this._cleanUp();
        this._editor.focus();
    };
    MarkerController.prototype._onMarkerChanged = function (changedResources) {
        var _this = this;
        if (!changedResources.some(function (r) { return _this._editor.getModel().uri.toString() === r.toString(); })) {
            return;
        }
        this._model.setMarkers(this._getMarkers());
    };
    MarkerController.prototype._getMarkers = function () {
        return this._markerService.read({ resource: this._editor.getModel().uri });
    };
    MarkerController.ID = 'editor.contrib.markerController';
    MarkerController = __decorate([
        __param(1, IMarkerService),
        __param(2, IContextKeyService),
        __param(3, IThemeService)
    ], MarkerController);
    return MarkerController;
}());
var NextMarkerAction = /** @class */ (function (_super) {
    __extends(NextMarkerAction, _super);
    function NextMarkerAction() {
        return _super.call(this, true, {
            id: 'editor.action.marker.next',
            label: nls.localize('markerAction.next.label', "Go to Next Problem (Error, Warning, Info)"),
            alias: 'Go to Next Error or Warning',
            precondition: EditorContextKeys.writable,
            kbOpts: {
                kbExpr: EditorContextKeys.focus,
                primary: 66 /* F8 */
            }
        }) || this;
    }
    return NextMarkerAction;
}(MarkerNavigationAction));
var PrevMarkerAction = /** @class */ (function (_super) {
    __extends(PrevMarkerAction, _super);
    function PrevMarkerAction() {
        return _super.call(this, false, {
            id: 'editor.action.marker.prev',
            label: nls.localize('markerAction.previous.label', "Go to Previous Problem (Error, Warning, Info)"),
            alias: 'Go to Previous Error or Warning',
            precondition: EditorContextKeys.writable,
            kbOpts: {
                kbExpr: EditorContextKeys.focus,
                primary: 1024 /* Shift */ | 66 /* F8 */
            }
        }) || this;
    }
    return PrevMarkerAction;
}(MarkerNavigationAction));
registerEditorContribution(MarkerController);
registerEditorAction(NextMarkerAction);
registerEditorAction(PrevMarkerAction);
var CONTEXT_MARKERS_NAVIGATION_VISIBLE = new RawContextKey('markersNavigationVisible', false);
var MarkerCommand = EditorCommand.bindToContribution(MarkerController.get);
registerEditorCommand(new MarkerCommand({
    id: 'closeMarkersNavigation',
    precondition: CONTEXT_MARKERS_NAVIGATION_VISIBLE,
    handler: function (x) { return x.closeMarkersNavigation(); },
    kbOpts: {
        weight: KeybindingsRegistry.WEIGHT.editorContrib(50),
        kbExpr: EditorContextKeys.focus,
        primary: 9 /* Escape */,
        secondary: [1024 /* Shift */ | 9 /* Escape */]
    }
}));
// theming
var errorDefault = oneOf(editorErrorForeground, editorErrorBorder);
var warningDefault = oneOf(editorWarningForeground, editorWarningBorder);
var infoDefault = oneOf(editorInfoForeground, editorInfoBorder);
export var editorMarkerNavigationError = registerColor('editorMarkerNavigationError.background', { dark: errorDefault, light: errorDefault, hc: errorDefault }, nls.localize('editorMarkerNavigationError', 'Editor marker navigation widget error color.'));
export var editorMarkerNavigationWarning = registerColor('editorMarkerNavigationWarning.background', { dark: warningDefault, light: warningDefault, hc: warningDefault }, nls.localize('editorMarkerNavigationWarning', 'Editor marker navigation widget warning color.'));
export var editorMarkerNavigationInfo = registerColor('editorMarkerNavigationInfo.background', { dark: infoDefault, light: infoDefault, hc: infoDefault }, nls.localize('editorMarkerNavigationInfo', 'Editor marker navigation widget info color.'));
export var editorMarkerNavigationBackground = registerColor('editorMarkerNavigation.background', { dark: '#2D2D30', light: Color.white, hc: '#0C141F' }, nls.localize('editorMarkerNavigationBackground', 'Editor marker navigation widget background.'));
