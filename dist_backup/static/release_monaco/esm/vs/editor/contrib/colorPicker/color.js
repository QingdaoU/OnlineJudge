/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
import { TPromise } from '../../../base/common/winjs.base.js';
import { ColorProviderRegistry } from '../../common/modes.js';
import { asWinJsPromise } from '../../../base/common/async.js';
export function getColors(model) {
    var colors = [];
    var providers = ColorProviderRegistry.ordered(model).reverse();
    var promises = providers.map(function (provider) { return asWinJsPromise(function (token) { return provider.provideDocumentColors(model, token); }).then(function (result) {
        if (Array.isArray(result)) {
            for (var _i = 0, result_1 = result; _i < result_1.length; _i++) {
                var colorInfo = result_1[_i];
                colors.push({ colorInfo: colorInfo, provider: provider });
            }
        }
    }); });
    return TPromise.join(promises).then(function () { return colors; });
}
export function getColorPresentations(model, colorInfo, provider) {
    return asWinJsPromise(function (token) { return provider.provideColorPresentations(model, colorInfo, token); });
}
