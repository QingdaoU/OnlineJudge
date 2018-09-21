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
import URI from '../../../base/common/uri.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { ITextModelService } from '../../common/services/resolverService.js';
import { IFileService, FileChangeType } from '../../../platform/files/common/files.js';
import { EditOperation } from '../../common/core/editOperation.js';
import { Range } from '../../common/core/range.js';
import { Selection } from '../../common/core/selection.js';
import { emptyProgressRunner } from '../../../platform/progress/common/progress.js';
import { optional } from '../../../platform/instantiation/common/instantiation.js';
import { isResourceFileEdit, isResourceTextEdit } from '../../common/modes.js';
import { getPathLabel } from '../../../base/common/labels.js';
var IRecording = /** @class */ (function () {
    function IRecording() {
    }
    IRecording.start = function (fileService) {
        var _changes = new Set();
        var stop;
        if (fileService) {
            // watch only when there is a fileservice available
            stop = fileService.onFileChanges(function (event) {
                for (var _i = 0, _a = event.changes; _i < _a.length; _i++) {
                    var change = _a[_i];
                    if (change.type === FileChangeType.UPDATED) {
                        _changes.add(change.resource.toString());
                    }
                }
            });
        }
        return {
            stop: function () { return dispose(stop); },
            hasChanged: function (resource) { return _changes.has(resource.toString()); }
        };
    };
    return IRecording;
}());
var EditTask = /** @class */ (function () {
    function EditTask(modelReference) {
        this._endCursorSelection = null;
        this._modelReference = modelReference;
        this._edits = [];
    }
    Object.defineProperty(EditTask.prototype, "_model", {
        get: function () { return this._modelReference.object.textEditorModel; },
        enumerable: true,
        configurable: true
    });
    EditTask.prototype.dispose = function () {
        if (this._model) {
            this._modelReference.dispose();
            this._modelReference = null;
        }
    };
    EditTask.prototype.addEdit = function (resourceEdit) {
        for (var _i = 0, _a = resourceEdit.edits; _i < _a.length; _i++) {
            var edit = _a[_i];
            if (typeof edit.eol === 'number') {
                // honor eol-change
                this._newEol = edit.eol;
            }
            if (edit.range || edit.text) {
                // create edit operation
                var range = void 0;
                if (!edit.range) {
                    range = this._model.getFullModelRange();
                }
                else {
                    range = Range.lift(edit.range);
                }
                this._edits.push(EditOperation.replaceMove(range, edit.text));
            }
        }
    };
    EditTask.prototype.apply = function () {
        var _this = this;
        if (this._edits.length > 0) {
            this._edits = this._edits.map(function (value, index) { return ({ value: value, index: index }); }).sort(function (a, b) {
                var ret = Range.compareRangesUsingStarts(a.value.range, b.value.range);
                if (ret === 0) {
                    ret = a.index - b.index;
                }
                return ret;
            }).map(function (element) { return element.value; });
            this._initialSelections = this._getInitialSelections();
            this._model.pushStackElement();
            this._model.pushEditOperations(this._initialSelections, this._edits, function (edits) { return _this._getEndCursorSelections(edits); });
            this._model.pushStackElement();
        }
        if (this._newEol !== undefined) {
            this._model.pushStackElement();
            this._model.setEOL(this._newEol);
            this._model.pushStackElement();
        }
    };
    EditTask.prototype._getInitialSelections = function () {
        var firstRange = this._edits[0].range;
        var initialSelection = new Selection(firstRange.startLineNumber, firstRange.startColumn, firstRange.endLineNumber, firstRange.endColumn);
        return [initialSelection];
    };
    EditTask.prototype._getEndCursorSelections = function (inverseEditOperations) {
        var relevantEditIndex = 0;
        for (var i = 0; i < inverseEditOperations.length; i++) {
            var editRange = inverseEditOperations[i].range;
            for (var j = 0; j < this._initialSelections.length; j++) {
                var selectionRange = this._initialSelections[j];
                if (Range.areIntersectingOrTouching(editRange, selectionRange)) {
                    relevantEditIndex = i;
                    break;
                }
            }
        }
        var srcRange = inverseEditOperations[relevantEditIndex].range;
        this._endCursorSelection = new Selection(srcRange.endLineNumber, srcRange.endColumn, srcRange.endLineNumber, srcRange.endColumn);
        return [this._endCursorSelection];
    };
    EditTask.prototype.getEndCursorSelection = function () {
        return this._endCursorSelection;
    };
    return EditTask;
}());
var SourceModelEditTask = /** @class */ (function (_super) {
    __extends(SourceModelEditTask, _super);
    function SourceModelEditTask(modelReference, initialSelections) {
        var _this = _super.call(this, modelReference) || this;
        _this._knownInitialSelections = initialSelections;
        return _this;
    }
    SourceModelEditTask.prototype._getInitialSelections = function () {
        return this._knownInitialSelections;
    };
    return SourceModelEditTask;
}(EditTask));
var BulkEditModel = /** @class */ (function () {
    function BulkEditModel(textModelResolverService, editor, edits, progress) {
        this._edits = new Map();
        this._textModelResolverService = textModelResolverService;
        this._sourceModel = editor ? editor.getModel().uri : undefined;
        this._sourceSelections = editor ? editor.getSelections() : undefined;
        this._sourceModelTask = undefined;
        this._progress = progress;
        edits.forEach(this.addEdit, this);
    }
    BulkEditModel.prototype.dispose = function () {
        this._tasks = dispose(this._tasks);
    };
    BulkEditModel.prototype.addEdit = function (edit) {
        var array = this._edits.get(edit.resource.toString());
        if (!array) {
            array = [];
            this._edits.set(edit.resource.toString(), array);
        }
        array.push(edit);
    };
    BulkEditModel.prototype.prepare = function () {
        return __awaiter(this, void 0, TPromise, function () {
            var _this = this;
            var promises;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (this._tasks) {
                            throw new Error('illegal state - already prepared');
                        }
                        this._tasks = [];
                        promises = [];
                        this._edits.forEach(function (value, key) {
                            var promise = _this._textModelResolverService.createModelReference(URI.parse(key)).then(function (ref) {
                                var model = ref.object;
                                if (!model || !model.textEditorModel) {
                                    throw new Error("Cannot load file " + key);
                                }
                                var task;
                                if (_this._sourceModel && model.textEditorModel.uri.toString() === _this._sourceModel.toString()) {
                                    _this._sourceModelTask = new SourceModelEditTask(ref, _this._sourceSelections);
                                    task = _this._sourceModelTask;
                                }
                                else {
                                    task = new EditTask(ref);
                                }
                                value.forEach(function (edit) { return task.addEdit(edit); });
                                _this._tasks.push(task);
                                _this._progress.report(undefined);
                            });
                            promises.push(promise);
                        });
                        return [4 /*yield*/, TPromise.join(promises)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/, this];
                }
            });
        });
    };
    BulkEditModel.prototype.apply = function () {
        for (var _i = 0, _a = this._tasks; _i < _a.length; _i++) {
            var task = _a[_i];
            task.apply();
            this._progress.report(undefined);
        }
        return this._sourceModelTask
            ? this._sourceModelTask.getEndCursorSelection()
            : undefined;
    };
    return BulkEditModel;
}());
var BulkEdit = /** @class */ (function () {
    function BulkEdit(editor, progress, _textModelService, _fileService) {
        this._textModelService = _textModelService;
        this._fileService = _fileService;
        this._edits = [];
        this._editor = editor;
        this._progress = progress || emptyProgressRunner;
    }
    BulkEdit.perform = function (edits, textModelService, fileService, editor) {
        var edit = new BulkEdit(editor, null, textModelService, fileService);
        edit.add(edits);
        return edit.perform();
    };
    BulkEdit.prototype.add = function (edits) {
        if (Array.isArray(edits)) {
            (_a = this._edits).push.apply(_a, edits);
        }
        else {
            this._edits.push(edits);
        }
        var _a;
    };
    BulkEdit.prototype.ariaMessage = function () {
        var editCount = this._edits.reduce(function (prev, cur) { return isResourceFileEdit(cur) ? prev : prev + cur.edits.length; }, 0);
        var resourceCount = this._edits.length;
        if (editCount === 0) {
            return nls.localize('summary.0', "Made no edits");
        }
        else if (editCount > 1 && resourceCount > 1) {
            return nls.localize('summary.nm', "Made {0} text edits in {1} files", editCount, resourceCount);
        }
        else {
            return nls.localize('summary.n0', "Made {0} text edits in one file", editCount, resourceCount);
        }
    };
    BulkEdit.prototype.perform = function () {
        return __awaiter(this, void 0, TPromise, function () {
            var _this = this;
            var seen, total, groups, group, _i, _a, edit, progress, res, _b, groups_1, group_1;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        seen = new Set();
                        total = 0;
                        groups = [];
                        for (_i = 0, _a = this._edits; _i < _a.length; _i++) {
                            edit = _a[_i];
                            if (!group
                                || (isResourceFileEdit(group[0]) && !isResourceFileEdit(edit))
                                || (isResourceTextEdit(group[0]) && !isResourceTextEdit(edit))) {
                                group = [];
                                groups.push(group);
                            }
                            group.push(edit);
                            if (isResourceFileEdit(edit)) {
                                total += 1;
                            }
                            else if (!seen.has(edit.resource.toString())) {
                                seen.add(edit.resource.toString());
                                total += 2;
                            }
                        }
                        // define total work and progress callback
                        // for child operations
                        this._progress.total(total);
                        progress = { report: function (_) { return _this._progress.worked(1); } };
                        res = undefined;
                        _b = 0, groups_1 = groups;
                        _c.label = 1;
                    case 1:
                        if (!(_b < groups_1.length)) return [3 /*break*/, 6];
                        group_1 = groups_1[_b];
                        if (!isResourceFileEdit(group_1[0])) return [3 /*break*/, 3];
                        return [4 /*yield*/, this._performFileEdits(group_1, progress)];
                    case 2:
                        _c.sent();
                        return [3 /*break*/, 5];
                    case 3: return [4 /*yield*/, this._performTextEdits(group_1, progress)];
                    case 4:
                        res = (_c.sent()) || res;
                        _c.label = 5;
                    case 5:
                        _b++;
                        return [3 /*break*/, 1];
                    case 6: return [2 /*return*/, res];
                }
            });
        });
    };
    BulkEdit.prototype._performFileEdits = function (edits, progress) {
        return __awaiter(this, void 0, void 0, function () {
            var _i, edits_1, edit;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _i = 0, edits_1 = edits;
                        _a.label = 1;
                    case 1:
                        if (!(_i < edits_1.length)) return [3 /*break*/, 8];
                        edit = edits_1[_i];
                        progress.report(undefined);
                        if (!(edit.newUri && edit.oldUri)) return [3 /*break*/, 3];
                        return [4 /*yield*/, this._fileService.moveFile(edit.oldUri, edit.newUri, false)];
                    case 2:
                        _a.sent();
                        return [3 /*break*/, 7];
                    case 3:
                        if (!(!edit.newUri && edit.oldUri)) return [3 /*break*/, 5];
                        return [4 /*yield*/, this._fileService.del(edit.oldUri, true)];
                    case 4:
                        _a.sent();
                        return [3 /*break*/, 7];
                    case 5:
                        if (!(edit.newUri && !edit.oldUri)) return [3 /*break*/, 7];
                        return [4 /*yield*/, this._fileService.createFile(edit.newUri, undefined, { overwrite: false })];
                    case 6:
                        _a.sent();
                        _a.label = 7;
                    case 7:
                        _i++;
                        return [3 /*break*/, 1];
                    case 8: return [2 /*return*/];
                }
            });
        });
    };
    BulkEdit.prototype._performTextEdits = function (edits, progress) {
        return __awaiter(this, void 0, TPromise, function () {
            var recording, model, conflicts, selection;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        recording = IRecording.start(this._fileService);
                        model = new BulkEditModel(this._textModelService, this._editor, edits, progress);
                        return [4 /*yield*/, model.prepare()];
                    case 1:
                        _a.sent();
                        conflicts = edits
                            .filter(function (edit) { return recording.hasChanged(edit.resource); })
                            .map(function (edit) { return getPathLabel(edit.resource); });
                        recording.stop();
                        if (conflicts.length > 0) {
                            model.dispose();
                            throw new Error(nls.localize('conflict', "These files have changed in the meantime: {0}", conflicts.join(', ')));
                        }
                        return [4 /*yield*/, model.apply()];
                    case 2:
                        selection = _a.sent();
                        model.dispose();
                        return [2 /*return*/, selection];
                }
            });
        });
    };
    BulkEdit = __decorate([
        __param(2, ITextModelService),
        __param(3, optional(IFileService))
    ], BulkEdit);
    return BulkEdit;
}());
export { BulkEdit };
