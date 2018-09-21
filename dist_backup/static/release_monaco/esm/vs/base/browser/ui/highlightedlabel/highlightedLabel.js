/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as dom from '../../dom.js';
import * as objects from '../../../common/objects.js';
import { render as renderOcticons } from '../octiconLabel/octiconLabel.js';
var HighlightedLabel = /** @class */ (function () {
    function HighlightedLabel(container) {
        this.domNode = document.createElement('span');
        this.domNode.className = 'monaco-highlighted-label';
        this.didEverRender = false;
        container.appendChild(this.domNode);
    }
    Object.defineProperty(HighlightedLabel.prototype, "element", {
        get: function () {
            return this.domNode;
        },
        enumerable: true,
        configurable: true
    });
    HighlightedLabel.prototype.set = function (text, highlights) {
        if (highlights === void 0) { highlights = []; }
        if (!text) {
            text = '';
        }
        if (this.didEverRender && this.text === text && objects.equals(this.highlights, highlights)) {
            return;
        }
        if (!Array.isArray(highlights)) {
            highlights = [];
        }
        this.text = text;
        this.highlights = highlights;
        this.render();
    };
    HighlightedLabel.prototype.render = function () {
        dom.clearNode(this.domNode);
        var htmlContent = [], highlight, pos = 0;
        for (var i = 0; i < this.highlights.length; i++) {
            highlight = this.highlights[i];
            if (highlight.end === highlight.start) {
                continue;
            }
            if (pos < highlight.start) {
                htmlContent.push('<span>');
                htmlContent.push(renderOcticons(this.text.substring(pos, highlight.start)));
                htmlContent.push('</span>');
                pos = highlight.end;
            }
            htmlContent.push('<span class="highlight">');
            htmlContent.push(renderOcticons(this.text.substring(highlight.start, highlight.end)));
            htmlContent.push('</span>');
            pos = highlight.end;
        }
        if (pos < this.text.length) {
            htmlContent.push('<span>');
            htmlContent.push(renderOcticons(this.text.substring(pos)));
            htmlContent.push('</span>');
        }
        this.domNode.innerHTML = htmlContent.join('');
        this.didEverRender = true;
    };
    HighlightedLabel.prototype.dispose = function () {
        this.text = null;
        this.highlights = null;
    };
    return HighlightedLabel;
}());
export { HighlightedLabel };
