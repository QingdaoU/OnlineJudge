/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { focusBorder, inputBackground, inputForeground, selectForeground, selectBackground, selectListBackground, selectBorder, inputBorder, foreground, editorBackground, contrastBorder, inputActiveOptionBorder, listFocusBackground, listFocusForeground, listActiveSelectionBackground, listActiveSelectionForeground, listInactiveSelectionForeground, listInactiveSelectionBackground, listInactiveFocusForeground, listInactiveFocusBackground, listHoverBackground, listHoverForeground, listDropBackground, pickerGroupBorder, pickerGroupForeground, widgetShadow, inputValidationInfoBorder, inputValidationInfoBackground, inputValidationWarningBorder, inputValidationWarningBackground, inputValidationErrorBorder, inputValidationErrorBackground, activeContrastBorder, buttonForeground, buttonBackground, buttonHoverBackground, lighten, badgeBackground, badgeForeground, progressBarBackground } from './colorRegistry.js';
export function attachStyler(themeService, optionsMapping, widgetOrCallback) {
    function applyStyles(theme) {
        var styles = Object.create(null);
        for (var key in optionsMapping) {
            var value = optionsMapping[key];
            if (typeof value === 'string') {
                styles[key] = theme.getColor(value);
            }
            else if (typeof value === 'function') {
                styles[key] = value(theme);
            }
        }
        if (typeof widgetOrCallback === 'function') {
            widgetOrCallback(styles);
        }
        else {
            widgetOrCallback.style(styles);
        }
    }
    applyStyles(themeService.getTheme());
    return themeService.onThemeChange(applyStyles);
}
export function attachCheckboxStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        inputActiveOptionBorder: (style && style.inputActiveOptionBorderColor) || inputActiveOptionBorder
    }, widget);
}
export function attachBadgeStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        badgeBackground: (style && style.badgeBackground) || badgeBackground,
        badgeForeground: (style && style.badgeForeground) || badgeForeground,
        badgeBorder: contrastBorder
    }, widget);
}
export function attachInputBoxStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        inputBackground: (style && style.inputBackground) || inputBackground,
        inputForeground: (style && style.inputForeground) || inputForeground,
        inputBorder: (style && style.inputBorder) || inputBorder,
        inputValidationInfoBorder: (style && style.inputValidationInfoBorder) || inputValidationInfoBorder,
        inputValidationInfoBackground: (style && style.inputValidationInfoBackground) || inputValidationInfoBackground,
        inputValidationWarningBorder: (style && style.inputValidationWarningBorder) || inputValidationWarningBorder,
        inputValidationWarningBackground: (style && style.inputValidationWarningBackground) || inputValidationWarningBackground,
        inputValidationErrorBorder: (style && style.inputValidationErrorBorder) || inputValidationErrorBorder,
        inputValidationErrorBackground: (style && style.inputValidationErrorBackground) || inputValidationErrorBackground
    }, widget);
}
export function attachSelectBoxStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        selectBackground: (style && style.selectBackground) || selectBackground,
        selectListBackground: (style && style.selectListBackground) || selectListBackground,
        selectForeground: (style && style.selectForeground) || selectForeground,
        selectBorder: (style && style.selectBorder) || selectBorder,
        focusBorder: (style && style.focusBorder) || focusBorder,
        listFocusBackground: (style && style.listFocusBackground) || listFocusBackground,
        listFocusForeground: (style && style.listFocusForeground) || listFocusForeground,
        listFocusOutline: (style && style.listFocusOutline) || activeContrastBorder,
        listHoverBackground: (style && style.listHoverBackground) || listHoverBackground,
        listHoverForeground: (style && style.listHoverForeground) || listHoverForeground,
        listHoverOutline: (style && style.listFocusOutline) || activeContrastBorder
    }, widget);
}
export function attachFindInputBoxStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        inputBackground: (style && style.inputBackground) || inputBackground,
        inputForeground: (style && style.inputForeground) || inputForeground,
        inputBorder: (style && style.inputBorder) || inputBorder,
        inputActiveOptionBorder: (style && style.inputActiveOptionBorder) || inputActiveOptionBorder,
        inputValidationInfoBorder: (style && style.inputValidationInfoBorder) || inputValidationInfoBorder,
        inputValidationInfoBackground: (style && style.inputValidationInfoBackground) || inputValidationInfoBackground,
        inputValidationWarningBorder: (style && style.inputValidationWarningBorder) || inputValidationWarningBorder,
        inputValidationWarningBackground: (style && style.inputValidationWarningBackground) || inputValidationWarningBackground,
        inputValidationErrorBorder: (style && style.inputValidationErrorBorder) || inputValidationErrorBorder,
        inputValidationErrorBackground: (style && style.inputValidationErrorBackground) || inputValidationErrorBackground
    }, widget);
}
export function attachQuickOpenStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        foreground: (style && style.foreground) || foreground,
        background: (style && style.background) || editorBackground,
        borderColor: style && style.borderColor || contrastBorder,
        widgetShadow: style && style.widgetShadow || widgetShadow,
        progressBarBackground: style && style.progressBarBackground || progressBarBackground,
        pickerGroupForeground: style && style.pickerGroupForeground || pickerGroupForeground,
        pickerGroupBorder: style && style.pickerGroupBorder || pickerGroupBorder,
        inputBackground: (style && style.inputBackground) || inputBackground,
        inputForeground: (style && style.inputForeground) || inputForeground,
        inputBorder: (style && style.inputBorder) || inputBorder,
        inputValidationInfoBorder: (style && style.inputValidationInfoBorder) || inputValidationInfoBorder,
        inputValidationInfoBackground: (style && style.inputValidationInfoBackground) || inputValidationInfoBackground,
        inputValidationWarningBorder: (style && style.inputValidationWarningBorder) || inputValidationWarningBorder,
        inputValidationWarningBackground: (style && style.inputValidationWarningBackground) || inputValidationWarningBackground,
        inputValidationErrorBorder: (style && style.inputValidationErrorBorder) || inputValidationErrorBorder,
        inputValidationErrorBackground: (style && style.inputValidationErrorBackground) || inputValidationErrorBackground,
        listFocusBackground: (style && style.listFocusBackground) || listFocusBackground,
        listFocusForeground: (style && style.listFocusForeground) || listFocusForeground,
        listActiveSelectionBackground: (style && style.listActiveSelectionBackground) || lighten(listActiveSelectionBackground, 0.1),
        listActiveSelectionForeground: (style && style.listActiveSelectionForeground) || listActiveSelectionForeground,
        listFocusAndSelectionBackground: style && style.listFocusAndSelectionBackground || listActiveSelectionBackground,
        listFocusAndSelectionForeground: (style && style.listFocusAndSelectionForeground) || listActiveSelectionForeground,
        listInactiveSelectionBackground: (style && style.listInactiveSelectionBackground) || listInactiveSelectionBackground,
        listInactiveSelectionForeground: (style && style.listInactiveSelectionForeground) || listInactiveSelectionForeground,
        listInactiveFocusBackground: (style && style.listInactiveFocusBackground) || listInactiveFocusBackground,
        listInactiveFocusForeground: (style && style.listInactiveFocusForeground) || listInactiveFocusForeground,
        listHoverBackground: (style && style.listHoverBackground) || listHoverBackground,
        listHoverForeground: (style && style.listHoverForeground) || listHoverForeground,
        listDropBackground: (style && style.listDropBackground) || listDropBackground,
        listFocusOutline: (style && style.listFocusOutline) || activeContrastBorder,
        listSelectionOutline: (style && style.listSelectionOutline) || activeContrastBorder,
        listHoverOutline: (style && style.listHoverOutline) || activeContrastBorder
    }, widget);
}
export function attachListStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        listFocusBackground: (style && style.listFocusBackground) || listFocusBackground,
        listFocusForeground: (style && style.listFocusForeground) || listFocusForeground,
        listActiveSelectionBackground: (style && style.listActiveSelectionBackground) || lighten(listActiveSelectionBackground, 0.1),
        listActiveSelectionForeground: (style && style.listActiveSelectionForeground) || listActiveSelectionForeground,
        listFocusAndSelectionBackground: style && style.listFocusAndSelectionBackground || listActiveSelectionBackground,
        listFocusAndSelectionForeground: (style && style.listFocusAndSelectionForeground) || listActiveSelectionForeground,
        listInactiveSelectionBackground: (style && style.listInactiveSelectionBackground) || listInactiveSelectionBackground,
        listInactiveSelectionForeground: (style && style.listInactiveSelectionForeground) || listInactiveSelectionForeground,
        listInactiveFocusBackground: (style && style.listInactiveFocusBackground) || listInactiveFocusBackground,
        listInactiveFocusForeground: (style && style.listInactiveFocusForeground) || listInactiveFocusForeground,
        listHoverBackground: (style && style.listHoverBackground) || listHoverBackground,
        listHoverForeground: (style && style.listHoverForeground) || listHoverForeground,
        listDropBackground: (style && style.listDropBackground) || listDropBackground,
        listFocusOutline: (style && style.listFocusOutline) || activeContrastBorder,
        listSelectionOutline: (style && style.listSelectionOutline) || activeContrastBorder,
        listHoverOutline: (style && style.listHoverOutline) || activeContrastBorder,
        listInactiveFocusOutline: style && style.listInactiveFocusOutline // not defined by default, only opt-in
    }, widget);
}
export function attachButtonStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        buttonForeground: (style && style.buttonForeground) || buttonForeground,
        buttonBackground: (style && style.buttonBackground) || buttonBackground,
        buttonHoverBackground: (style && style.buttonHoverBackground) || buttonHoverBackground,
        buttonBorder: contrastBorder
    }, widget);
}
export function attachProgressBarStyler(widget, themeService, style) {
    return attachStyler(themeService, {
        progressBarBackground: (style && style.progressBarBackground) || progressBarBackground
    }, widget);
}
export function attachStylerCallback(themeService, colors, callback) {
    return attachStyler(themeService, colors, callback);
}
