/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import './menu.css';
import { $ } from '../../builder.js';
import { ActionBar, ActionsOrientation } from '../actionbar/actionbar.js';
var Menu = /** @class */ (function () {
    function Menu(container, actions, options) {
        if (options === void 0) { options = {}; }
        $(container).addClass('monaco-menu-container');
        var $menu = $('.monaco-menu').appendTo(container);
        this.actionBar = new ActionBar($menu, {
            orientation: ActionsOrientation.VERTICAL,
            actionItemProvider: options.actionItemProvider,
            context: options.context,
            actionRunner: options.actionRunner,
            isMenu: true
        });
        this.actionBar.push(actions, { icon: true, label: true });
    }
    Object.defineProperty(Menu.prototype, "onDidCancel", {
        get: function () {
            return this.actionBar.onDidCancel;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Menu.prototype, "onDidBlur", {
        get: function () {
            return this.actionBar.onDidBlur;
        },
        enumerable: true,
        configurable: true
    });
    Menu.prototype.focus = function () {
        this.actionBar.focus(true);
    };
    Menu.prototype.dispose = function () {
        if (this.actionBar) {
            this.actionBar.dispose();
            this.actionBar = null;
        }
        if (this.listener) {
            this.listener.dispose();
            this.listener = null;
        }
    };
    return Menu;
}());
export { Menu };
