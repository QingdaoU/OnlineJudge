/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { DefaultEndOfLine } from '../../model.js';
var TextSource = /** @class */ (function () {
    function TextSource() {
    }
    /**
     * if text source is empty or with precisely one line, returns null. No end of line is detected.
     * if text source contains more lines ending with '\r\n', returns '\r\n'.
     * Otherwise returns '\n'. More lines end with '\n'.
     */
    TextSource._getEOL = function (rawTextSource, defaultEOL) {
        var lineFeedCnt = rawTextSource.lines.length - 1;
        if (lineFeedCnt === 0) {
            // This is an empty file or a file with precisely one line
            return (defaultEOL === DefaultEndOfLine.LF ? '\n' : '\r\n');
        }
        if (rawTextSource.totalCRCount > lineFeedCnt / 2) {
            // More than half of the file contains \r\n ending lines
            return '\r\n';
        }
        // At least one line more ends in \n
        return '\n';
    };
    TextSource.fromRawTextSource = function (rawTextSource, defaultEOL) {
        return {
            lines: rawTextSource.lines,
            BOM: rawTextSource.BOM,
            EOL: TextSource._getEOL(rawTextSource, defaultEOL),
            containsRTL: rawTextSource.containsRTL,
            isBasicASCII: rawTextSource.isBasicASCII,
        };
    };
    return TextSource;
}());
export { TextSource };
