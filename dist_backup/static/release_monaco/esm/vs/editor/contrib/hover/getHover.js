/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { coalesce } from '../../../base/common/arrays.js';
import { onUnexpectedExternalError } from '../../../base/common/errors.js';
import { TPromise } from '../../../base/common/winjs.base.js';
import { registerDefaultLanguageCommand } from '../../browser/editorExtensions.js';
import { HoverProviderRegistry } from '../../common/modes.js';
import { asWinJsPromise } from '../../../base/common/async.js';
export function getHover(model, position) {
    var supports = HoverProviderRegistry.ordered(model);
    var values = [];
    var promises = supports.map(function (support, idx) {
        return asWinJsPromise(function (token) {
            return support.provideHover(model, position, token);
        }).then(function (result) {
            if (result) {
                var hasRange = (typeof result.range !== 'undefined');
                var hasHtmlContent = typeof result.contents !== 'undefined' && result.contents && result.contents.length > 0;
                if (hasRange && hasHtmlContent) {
                    values[idx] = result;
                }
            }
        }, function (err) {
            onUnexpectedExternalError(err);
        });
    });
    return TPromise.join(promises).then(function () { return coalesce(values); });
}
registerDefaultLanguageCommand('_executeHoverProvider', getHover);
