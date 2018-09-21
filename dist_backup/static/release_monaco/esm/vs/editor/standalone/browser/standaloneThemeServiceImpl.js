/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { TokenTheme, generateTokensCSSForColorMap } from '../../common/modes/supports/tokenization.js';
import { vs, vs_dark, hc_black } from '../common/themes.js';
import * as dom from '../../../base/browser/dom.js';
import { TokenizationRegistry } from '../../common/modes.js';
import { Color } from '../../../base/common/color.js';
import { Extensions } from '../../../platform/theme/common/colorRegistry.js';
import { Extensions as ThemingExtensions } from '../../../platform/theme/common/themeService.js';
import { Registry } from '../../../platform/registry/common/platform.js';
import { Emitter } from '../../../base/common/event.js';
var VS_THEME_NAME = 'vs';
var VS_DARK_THEME_NAME = 'vs-dark';
var HC_BLACK_THEME_NAME = 'hc-black';
var colorRegistry = Registry.as(Extensions.ColorContribution);
var themingRegistry = Registry.as(ThemingExtensions.ThemingContribution);
var StandaloneTheme = /** @class */ (function () {
    function StandaloneTheme(base, name, colors, rules) {
        if (name.length > 0) {
            this.id = base + ' ' + name;
            this.themeName = name;
        }
        else {
            this.id = base;
            this.themeName = base;
        }
        this.base = base;
        this.rules = rules;
        this.colors = {};
        for (var id in colors) {
            this.colors[id] = Color.fromHex(colors[id]);
        }
        this.defaultColors = {};
    }
    StandaloneTheme.prototype.getColor = function (colorId, useDefault) {
        if (this.colors.hasOwnProperty(colorId)) {
            return this.colors[colorId];
        }
        if (useDefault !== false) {
            return this.getDefault(colorId);
        }
        return null;
    };
    StandaloneTheme.prototype.getDefault = function (colorId) {
        if (this.defaultColors.hasOwnProperty(colorId)) {
            return this.defaultColors[colorId];
        }
        var color = colorRegistry.resolveDefaultColor(colorId, this);
        this.defaultColors[colorId] = color;
        return color;
    };
    StandaloneTheme.prototype.defines = function (colorId) {
        return this.colors.hasOwnProperty(colorId);
    };
    Object.defineProperty(StandaloneTheme.prototype, "type", {
        get: function () {
            switch (this.base) {
                case VS_THEME_NAME: return 'light';
                case HC_BLACK_THEME_NAME: return 'hc';
                default: return 'dark';
            }
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(StandaloneTheme.prototype, "tokenTheme", {
        get: function () {
            if (!this._tokenTheme) {
                this._tokenTheme = TokenTheme.createFromRawTokenTheme(this.rules);
            }
            return this._tokenTheme;
        },
        enumerable: true,
        configurable: true
    });
    return StandaloneTheme;
}());
function isBuiltinTheme(themeName) {
    return (themeName === VS_THEME_NAME
        || themeName === VS_DARK_THEME_NAME
        || themeName === HC_BLACK_THEME_NAME);
}
function getBuiltinRules(builtinTheme) {
    switch (builtinTheme) {
        case VS_THEME_NAME:
            return vs;
        case VS_DARK_THEME_NAME:
            return vs_dark;
        case HC_BLACK_THEME_NAME:
            return hc_black;
    }
}
function newBuiltInTheme(builtinTheme) {
    var themeData = getBuiltinRules(builtinTheme);
    return new StandaloneTheme(builtinTheme, '', themeData.colors, themeData.rules);
}
var StandaloneThemeServiceImpl = /** @class */ (function () {
    function StandaloneThemeServiceImpl() {
        this._onThemeChange = new Emitter();
        this._knownThemes = new Map();
        this._knownThemes.set(VS_THEME_NAME, newBuiltInTheme(VS_THEME_NAME));
        this._knownThemes.set(VS_DARK_THEME_NAME, newBuiltInTheme(VS_DARK_THEME_NAME));
        this._knownThemes.set(HC_BLACK_THEME_NAME, newBuiltInTheme(HC_BLACK_THEME_NAME));
        this._styleElement = dom.createStyleSheet();
        this._styleElement.className = 'monaco-colors';
        this.setTheme(VS_THEME_NAME);
    }
    Object.defineProperty(StandaloneThemeServiceImpl.prototype, "onThemeChange", {
        get: function () {
            return this._onThemeChange.event;
        },
        enumerable: true,
        configurable: true
    });
    StandaloneThemeServiceImpl.prototype.defineTheme = function (themeName, themeData) {
        if (!/^[a-z0-9\-]+$/i.test(themeName) || isBuiltinTheme(themeName)) {
            throw new Error('Illegal theme name!');
        }
        if (!isBuiltinTheme(themeData.base)) {
            throw new Error('Illegal theme base!');
        }
        var rules = [];
        var colors = {};
        if (themeData.inherit) {
            var baseData = getBuiltinRules(themeData.base);
            rules = rules.concat(baseData.rules);
            for (var id in baseData.colors) {
                colors[id] = baseData.colors[id];
            }
        }
        rules = rules.concat(themeData.rules);
        for (var id in themeData.colors) {
            colors[id] = themeData.colors[id];
        }
        this._knownThemes.set(themeName, new StandaloneTheme(themeData.base, themeName, colors, rules));
    };
    StandaloneThemeServiceImpl.prototype.getTheme = function () {
        return this._theme;
    };
    StandaloneThemeServiceImpl.prototype.setTheme = function (themeName) {
        var theme;
        if (this._knownThemes.has(themeName)) {
            theme = this._knownThemes.get(themeName);
        }
        else {
            theme = this._knownThemes.get(VS_THEME_NAME);
        }
        this._theme = theme;
        var cssRules = [];
        var hasRule = {};
        var ruleCollector = {
            addRule: function (rule) {
                if (!hasRule[rule]) {
                    cssRules.push(rule);
                    hasRule[rule] = true;
                }
            }
        };
        themingRegistry.getThemingParticipants().forEach(function (p) { return p(theme, ruleCollector); });
        var tokenTheme = theme.tokenTheme;
        var colorMap = tokenTheme.getColorMap();
        ruleCollector.addRule(generateTokensCSSForColorMap(colorMap));
        this._styleElement.innerHTML = cssRules.join('\n');
        TokenizationRegistry.setColorMap(colorMap);
        this._onThemeChange.fire(theme);
        return theme.id;
    };
    return StandaloneThemeServiceImpl;
}());
export { StandaloneThemeServiceImpl };
