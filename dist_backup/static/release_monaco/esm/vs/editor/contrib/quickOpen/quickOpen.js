/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { illegalArgument, onUnexpectedExternalError } from '../../../base/common/errors.js';
import URI from '../../../base/common/uri.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { Range } from '../../common/core/range.js';
import { registerLanguageCommand } from '../../browser/editorExtensions.js';
import { DocumentSymbolProviderRegistry } from '../../common/modes.js';
import { IModelService } from '../../common/services/modelService.js';
import { asWinJsPromise } from '../../../base/common/async.js';
export function getDocumentSymbols(model) {
    var entries = [];
    var promises = DocumentSymbolProviderRegistry.all(model).map(function (support) {
        return asWinJsPromise(function (token) {
            return support.provideDocumentSymbols(model, token);
        }).then(function (result) {
            if (Array.isArray(result)) {
                entries.push.apply(entries, result);
            }
        }, function (err) {
            onUnexpectedExternalError(err);
        });
    });
    return TPromise.join(promises).then(function () {
        var flatEntries = [];
        flatten(flatEntries, entries, '');
        flatEntries.sort(compareEntriesUsingStart);
        return {
            entries: flatEntries,
        };
    });
}
function compareEntriesUsingStart(a, b) {
    return Range.compareRangesUsingStarts(Range.lift(a.location.range), Range.lift(b.location.range));
}
function flatten(bucket, entries, overrideContainerLabel) {
    for (var _i = 0, entries_1 = entries; _i < entries_1.length; _i++) {
        var entry = entries_1[_i];
        bucket.push({
            kind: entry.kind,
            location: entry.location,
            name: entry.name,
            containerName: entry.containerName || overrideContainerLabel
        });
    }
}
registerLanguageCommand('_executeDocumentSymbolProvider', function (accessor, args) {
    var resource = args.resource;
    if (!(resource instanceof URI)) {
        throw illegalArgument('resource');
    }
    var model = accessor.get(IModelService).getModel(resource);
    if (!model) {
        throw illegalArgument('resource');
    }
    return getDocumentSymbols(model);
});
