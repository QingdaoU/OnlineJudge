/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import * as nls from '../../../nls.js';
import { Emitter } from '../../../base/common/event.js';
import { Registry } from '../../registry/common/platform.js';
import * as types from '../../../base/common/types.js';
import * as strings from '../../../base/common/strings.js';
import { Extensions as JSONExtensions } from '../../jsonschemas/common/jsonContributionRegistry.js';
import { deepClone } from '../../../base/common/objects.js';
export var Extensions = {
    Configuration: 'base.contributions.configuration'
};
export var ConfigurationScope;
(function (ConfigurationScope) {
    ConfigurationScope[ConfigurationScope["WINDOW"] = 1] = "WINDOW";
    ConfigurationScope[ConfigurationScope["RESOURCE"] = 2] = "RESOURCE";
})(ConfigurationScope || (ConfigurationScope = {}));
export var settingsSchema = { properties: {}, patternProperties: {}, additionalProperties: false, errorMessage: 'Unknown configuration setting' };
export var resourceSettingsSchema = { properties: {}, patternProperties: {}, additionalProperties: false, errorMessage: 'Unknown configuration setting' };
export var editorConfigurationSchemaId = 'vscode://schemas/settings/editor';
var contributionRegistry = Registry.as(JSONExtensions.JSONContribution);
var ConfigurationRegistry = /** @class */ (function () {
    function ConfigurationRegistry() {
        this.overrideIdentifiers = [];
        this._onDidRegisterConfiguration = new Emitter();
        this.onDidRegisterConfiguration = this._onDidRegisterConfiguration.event;
        this.configurationContributors = [];
        this.editorConfigurationSchema = { properties: {}, patternProperties: {}, additionalProperties: false, errorMessage: 'Unknown editor configuration setting' };
        this.configurationProperties = {};
        this.excludedConfigurationProperties = {};
        this.computeOverridePropertyPattern();
        contributionRegistry.registerSchema(editorConfigurationSchemaId, this.editorConfigurationSchema);
    }
    ConfigurationRegistry.prototype.registerConfiguration = function (configuration, validate) {
        if (validate === void 0) { validate = true; }
        this.registerConfigurations([configuration], [], validate);
    };
    ConfigurationRegistry.prototype.registerConfigurations = function (configurations, defaultConfigurations, validate) {
        var _this = this;
        if (validate === void 0) { validate = true; }
        var configurationNode = this.toConfiguration(defaultConfigurations);
        if (configurationNode) {
            configurations.push(configurationNode);
        }
        var properties = [];
        configurations.forEach(function (configuration) {
            properties.push.apply(properties, _this.validateAndRegisterProperties(configuration, validate)); // fills in defaults
            _this.configurationContributors.push(configuration);
            _this.registerJSONConfiguration(configuration);
            _this.updateSchemaForOverrideSettingsConfiguration(configuration);
        });
        this._onDidRegisterConfiguration.fire(properties);
    };
    ConfigurationRegistry.prototype.notifyConfigurationSchemaUpdated = function (configuration) {
        contributionRegistry.notifySchemaChanged(editorConfigurationSchemaId);
    };
    ConfigurationRegistry.prototype.registerOverrideIdentifiers = function (overrideIdentifiers) {
        (_a = this.overrideIdentifiers).push.apply(_a, overrideIdentifiers);
        this.updateOverridePropertyPatternKey();
        var _a;
    };
    ConfigurationRegistry.prototype.toConfiguration = function (defaultConfigurations) {
        var configurationNode = {
            id: 'defaultOverrides',
            title: nls.localize('defaultConfigurations.title', "Default Configuration Overrides"),
            properties: {}
        };
        for (var _i = 0, defaultConfigurations_1 = defaultConfigurations; _i < defaultConfigurations_1.length; _i++) {
            var defaultConfiguration = defaultConfigurations_1[_i];
            for (var key in defaultConfiguration.defaults) {
                var defaultValue = defaultConfiguration.defaults[key];
                if (OVERRIDE_PROPERTY_PATTERN.test(key) && typeof defaultValue === 'object') {
                    configurationNode.properties[key] = {
                        type: 'object',
                        default: defaultValue,
                        description: nls.localize('overrideSettings.description', "Configure editor settings to be overridden for {0} language.", key),
                        $ref: editorConfigurationSchemaId
                    };
                }
            }
        }
        return Object.keys(configurationNode.properties).length ? configurationNode : null;
    };
    ConfigurationRegistry.prototype.validateAndRegisterProperties = function (configuration, validate, scope, overridable) {
        if (validate === void 0) { validate = true; }
        if (scope === void 0) { scope = ConfigurationScope.WINDOW; }
        if (overridable === void 0) { overridable = false; }
        scope = configuration.scope !== void 0 && configuration.scope !== null ? configuration.scope : scope;
        overridable = configuration.overridable || overridable;
        var propertyKeys = [];
        var properties = configuration.properties;
        if (properties) {
            for (var key in properties) {
                var message = void 0;
                if (validate && (message = validateProperty(key))) {
                    console.warn(message);
                    delete properties[key];
                    continue;
                }
                // fill in default values
                var property = properties[key];
                var defaultValue = property.default;
                if (types.isUndefined(defaultValue)) {
                    property.default = getDefaultValue(property.type);
                }
                // Inherit overridable property from parent
                if (overridable) {
                    property.overridable = true;
                }
                if (property.scope === void 0) {
                    property.scope = scope;
                }
                // Add to properties maps
                // Property is included by default if 'included' is unspecified
                if (properties[key].hasOwnProperty('included') && !properties[key].included) {
                    this.excludedConfigurationProperties[key] = properties[key];
                    delete properties[key];
                    continue;
                }
                else {
                    this.configurationProperties[key] = properties[key];
                }
                propertyKeys.push(key);
            }
        }
        var subNodes = configuration.allOf;
        if (subNodes) {
            for (var _i = 0, subNodes_1 = subNodes; _i < subNodes_1.length; _i++) {
                var node = subNodes_1[_i];
                propertyKeys.push.apply(propertyKeys, this.validateAndRegisterProperties(node, validate, scope, overridable));
            }
        }
        return propertyKeys;
    };
    ConfigurationRegistry.prototype.getConfigurations = function () {
        return this.configurationContributors;
    };
    ConfigurationRegistry.prototype.getConfigurationProperties = function () {
        return this.configurationProperties;
    };
    ConfigurationRegistry.prototype.getExcludedConfigurationProperties = function () {
        return this.excludedConfigurationProperties;
    };
    ConfigurationRegistry.prototype.registerJSONConfiguration = function (configuration) {
        function register(configuration) {
            var properties = configuration.properties;
            if (properties) {
                for (var key in properties) {
                    settingsSchema.properties[key] = properties[key];
                    resourceSettingsSchema.properties[key] = deepClone(properties[key]);
                    if (properties[key].scope !== ConfigurationScope.RESOURCE) {
                        resourceSettingsSchema.properties[key].doNotSuggest = true;
                    }
                }
            }
            var subNodes = configuration.allOf;
            if (subNodes) {
                subNodes.forEach(register);
            }
        }
        register(configuration);
    };
    ConfigurationRegistry.prototype.updateSchemaForOverrideSettingsConfiguration = function (configuration) {
        if (configuration.id !== SETTINGS_OVERRRIDE_NODE_ID) {
            this.update(configuration);
            contributionRegistry.registerSchema(editorConfigurationSchemaId, this.editorConfigurationSchema);
        }
    };
    ConfigurationRegistry.prototype.updateOverridePropertyPatternKey = function () {
        var patternProperties = settingsSchema.patternProperties[this.overridePropertyPattern];
        if (!patternProperties) {
            patternProperties = {
                type: 'object',
                description: nls.localize('overrideSettings.defaultDescription', "Configure editor settings to be overridden for a language."),
                errorMessage: 'Unknown Identifier. Use language identifiers',
                $ref: editorConfigurationSchemaId
            };
        }
        delete settingsSchema.patternProperties[this.overridePropertyPattern];
        this.computeOverridePropertyPattern();
        settingsSchema.patternProperties[this.overridePropertyPattern] = patternProperties;
        resourceSettingsSchema.patternProperties[this.overridePropertyPattern] = patternProperties;
    };
    ConfigurationRegistry.prototype.update = function (configuration) {
        var _this = this;
        var properties = configuration.properties;
        if (properties) {
            for (var key in properties) {
                if (properties[key].overridable) {
                    this.editorConfigurationSchema.properties[key] = this.getConfigurationProperties()[key];
                }
            }
        }
        var subNodes = configuration.allOf;
        if (subNodes) {
            subNodes.forEach(function (subNode) { return _this.update(subNode); });
        }
    };
    ConfigurationRegistry.prototype.computeOverridePropertyPattern = function () {
        this.overridePropertyPattern = this.overrideIdentifiers.length ? OVERRIDE_PATTERN_WITH_SUBSTITUTION.replace('${0}', this.overrideIdentifiers.map(function (identifier) { return strings.createRegExp(identifier, false).source; }).join('|')) : OVERRIDE_PROPERTY;
    };
    return ConfigurationRegistry;
}());
var SETTINGS_OVERRRIDE_NODE_ID = 'override';
var OVERRIDE_PROPERTY = '\\[.*\\]$';
var OVERRIDE_PATTERN_WITH_SUBSTITUTION = '\\[(${0})\\]$';
export var OVERRIDE_PROPERTY_PATTERN = new RegExp(OVERRIDE_PROPERTY);
function getDefaultValue(type) {
    var t = Array.isArray(type) ? type[0] : type;
    switch (t) {
        case 'boolean':
            return false;
        case 'integer':
        case 'number':
            return 0;
        case 'string':
            return '';
        case 'array':
            return [];
        case 'object':
            return {};
        default:
            return null;
    }
}
var configurationRegistry = new ConfigurationRegistry();
Registry.add(Extensions.Configuration, configurationRegistry);
export function validateProperty(property) {
    if (OVERRIDE_PROPERTY_PATTERN.test(property)) {
        return nls.localize('config.property.languageDefault', "Cannot register '{0}'. This matches property pattern '\\\\[.*\\\\]$' for describing language specific editor settings. Use 'configurationDefaults' contribution.", property);
    }
    if (configurationRegistry.getConfigurationProperties()[property] !== void 0) {
        return nls.localize('config.property.duplicate', "Cannot register '{0}'. This property is already registered.", property);
    }
    return null;
}
export function getScopes() {
    var scopes = {};
    var configurationProperties = configurationRegistry.getConfigurationProperties();
    for (var _i = 0, _a = Object.keys(configurationProperties); _i < _a.length; _i++) {
        var key = _a[_i];
        scopes[key] = configurationProperties[key].scope;
    }
    scopes['launch'] = ConfigurationScope.RESOURCE;
    scopes['task'] = ConfigurationScope.RESOURCE;
    return scopes;
}
