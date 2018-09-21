/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { onUnexpectedExternalError } from '../../../base/common/errors.js';
import { registerDefaultLanguageCommand } from '../../browser/editorExtensions.js';
import { SignatureHelpProviderRegistry } from '../../common/modes.js';
import { asWinJsPromise, sequence } from '../../../base/common/async.js';
import { RawContextKey } from '../../../platform/contextkey/common/contextkey.js';
export var Context = {
    Visible: new RawContextKey('parameterHintsVisible', false),
    MultipleSignatures: new RawContextKey('parameterHintsMultipleSignatures', false),
};
export function provideSignatureHelp(model, position) {
    var supports = SignatureHelpProviderRegistry.ordered(model);
    var result;
    return sequence(supports.map(function (support) { return function () {
        if (result) {
            // stop when there is a result
            return undefined;
        }
        return asWinJsPromise(function (token) { return support.provideSignatureHelp(model, position, token); }).then(function (thisResult) {
            result = thisResult;
        }, onUnexpectedExternalError);
    }; })).then(function () { return result; });
}
registerDefaultLanguageCommand('_executeSignatureHelpProvider', provideSignatureHelp);
