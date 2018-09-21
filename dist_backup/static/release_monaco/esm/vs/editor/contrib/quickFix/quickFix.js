/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import URI from '../../../base/common/uri.js';
import { Range } from '../../common/core/range.js';
import { CodeActionProviderRegistry } from '../../common/modes.js';
import { asWinJsPromise } from '../../../base/common/async.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { onUnexpectedExternalError, illegalArgument } from '../../../base/common/errors.js';
import { IModelService } from '../../common/services/modelService.js';
import { registerLanguageCommand } from '../../browser/editorExtensions.js';
import { isFalsyOrEmpty, mergeSort } from '../../../base/common/arrays.js';
export function getCodeActions(model, range, scope) {
    var allResults = [];
    var promises = CodeActionProviderRegistry.all(model).map(function (support) {
        return asWinJsPromise(function (token) { return support.provideCodeActions(model, range, { only: scope ? scope.value : undefined }, token); }).then(function (result) {
            if (Array.isArray(result)) {
                for (var _i = 0, result_1 = result; _i < result_1.length; _i++) {
                    var quickFix = result_1[_i];
                    if (quickFix) {
                        if (!scope || (quickFix.kind && scope.contains(quickFix.kind))) {
                            allResults.push(quickFix);
                        }
                    }
                }
            }
        }, function (err) {
            onUnexpectedExternalError(err);
        });
    });
    return TPromise.join(promises).then(function () { return mergeSort(allResults, codeActionsComparator); });
}
function codeActionsComparator(a, b) {
    var aHasDiags = !isFalsyOrEmpty(a.diagnostics);
    var bHasDiags = !isFalsyOrEmpty(b.diagnostics);
    if (aHasDiags) {
        if (bHasDiags) {
            return a.diagnostics[0].message.localeCompare(b.diagnostics[0].message);
        }
        else {
            return -1;
        }
    }
    else if (bHasDiags) {
        return 1;
    }
    else {
        return 0; // both have no diagnostics
    }
}
registerLanguageCommand('_executeCodeActionProvider', function (accessor, args) {
    var resource = args.resource, range = args.range;
    if (!(resource instanceof URI) || !Range.isIRange(range)) {
        throw illegalArgument();
    }
    var model = accessor.get(IModelService).getModel(resource);
    if (!model) {
        throw illegalArgument();
    }
    return getCodeActions(model, model.validateRange(range));
});
