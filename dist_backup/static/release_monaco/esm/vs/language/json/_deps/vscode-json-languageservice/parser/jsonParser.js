/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
import * as Json from '../../jsonc-parser/main.js';
import * as objects from '../utils/objects.js';
import * as nls from '../../../fillers/vscode-nls.js';
import Uri from '../../vscode-uri/index.js';
var localize = nls.loadMessageBundle();
export var ErrorCode;
(function (ErrorCode) {
    ErrorCode[ErrorCode["Undefined"] = 0] = "Undefined";
    ErrorCode[ErrorCode["EnumValueMismatch"] = 1] = "EnumValueMismatch";
    ErrorCode[ErrorCode["UnexpectedEndOfComment"] = 257] = "UnexpectedEndOfComment";
    ErrorCode[ErrorCode["UnexpectedEndOfString"] = 258] = "UnexpectedEndOfString";
    ErrorCode[ErrorCode["UnexpectedEndOfNumber"] = 259] = "UnexpectedEndOfNumber";
    ErrorCode[ErrorCode["InvalidUnicode"] = 260] = "InvalidUnicode";
    ErrorCode[ErrorCode["InvalidEscapeCharacter"] = 261] = "InvalidEscapeCharacter";
    ErrorCode[ErrorCode["InvalidCharacter"] = 262] = "InvalidCharacter";
    ErrorCode[ErrorCode["PropertyExpected"] = 513] = "PropertyExpected";
    ErrorCode[ErrorCode["CommaExpected"] = 514] = "CommaExpected";
    ErrorCode[ErrorCode["ColonExpected"] = 515] = "ColonExpected";
    ErrorCode[ErrorCode["ValueExpected"] = 516] = "ValueExpected";
    ErrorCode[ErrorCode["CommaOrCloseBacketExpected"] = 517] = "CommaOrCloseBacketExpected";
    ErrorCode[ErrorCode["CommaOrCloseBraceExpected"] = 518] = "CommaOrCloseBraceExpected";
    ErrorCode[ErrorCode["TrailingComma"] = 519] = "TrailingComma";
})(ErrorCode || (ErrorCode = {}));
var colorHexPattern = /^#([0-9A-Fa-f]{3,4}|([0-9A-Fa-f]{2}){3,4})$/;
var emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
export var ProblemSeverity;
(function (ProblemSeverity) {
    ProblemSeverity["Ignore"] = "ignore";
    ProblemSeverity["Error"] = "error";
    ProblemSeverity["Warning"] = "warning";
})(ProblemSeverity || (ProblemSeverity = {}));
var ASTNode = /** @class */ (function () {
    function ASTNode(parent, type, location, start, end) {
        this.type = type;
        this.location = location;
        this.start = start;
        this.end = end;
        this.parent = parent;
    }
    ASTNode.prototype.getPath = function () {
        var path = this.parent ? this.parent.getPath() : [];
        if (this.location !== null) {
            path.push(this.location);
        }
        return path;
    };
    ASTNode.prototype.getChildNodes = function () {
        return [];
    };
    ASTNode.prototype.getLastChild = function () {
        return null;
    };
    ASTNode.prototype.getValue = function () {
        // override in children
        return;
    };
    ASTNode.prototype.contains = function (offset, includeRightBound) {
        if (includeRightBound === void 0) { includeRightBound = false; }
        return offset >= this.start && offset < this.end || includeRightBound && offset === this.end;
    };
    ASTNode.prototype.toString = function () {
        return 'type: ' + this.type + ' (' + this.start + '/' + this.end + ')' + (this.parent ? ' parent: {' + this.parent.toString() + '}' : '');
    };
    ASTNode.prototype.visit = function (visitor) {
        return visitor(this);
    };
    ASTNode.prototype.getNodeFromOffset = function (offset) {
        var findNode = function (node) {
            if (offset >= node.start && offset < node.end) {
                var children = node.getChildNodes();
                for (var i = 0; i < children.length && children[i].start <= offset; i++) {
                    var item = findNode(children[i]);
                    if (item) {
                        return item;
                    }
                }
                return node;
            }
            return null;
        };
        return findNode(this);
    };
    ASTNode.prototype.getNodeFromOffsetEndInclusive = function (offset) {
        var findNode = function (node) {
            if (offset >= node.start && offset <= node.end) {
                var children = node.getChildNodes();
                for (var i = 0; i < children.length && children[i].start <= offset; i++) {
                    var item = findNode(children[i]);
                    if (item) {
                        return item;
                    }
                }
                return node;
            }
            return null;
        };
        return findNode(this);
    };
    ASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        var _this = this;
        if (!matchingSchemas.include(this)) {
            return;
        }
        if (Array.isArray(schema.type)) {
            if (schema.type.indexOf(this.type) === -1) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: schema.errorMessage || localize('typeArrayMismatchWarning', 'Incorrect type. Expected one of {0}.', schema.type.join(', '))
                });
            }
        }
        else if (schema.type) {
            if (this.type !== schema.type) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: schema.errorMessage || localize('typeMismatchWarning', 'Incorrect type. Expected "{0}".', schema.type)
                });
            }
        }
        if (Array.isArray(schema.allOf)) {
            schema.allOf.forEach(function (subSchemaRef) {
                _this.validate(asSchema(subSchemaRef), validationResult, matchingSchemas);
            });
        }
        var notSchema = asSchema(schema.not);
        if (notSchema) {
            var subValidationResult = new ValidationResult();
            var subMatchingSchemas = matchingSchemas.newSub();
            this.validate(notSchema, subValidationResult, subMatchingSchemas);
            if (!subValidationResult.hasProblems()) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: localize('notSchemaWarning', "Matches a schema that is not allowed.")
                });
            }
            subMatchingSchemas.schemas.forEach(function (ms) {
                ms.inverted = !ms.inverted;
                matchingSchemas.add(ms);
            });
        }
        var testAlternatives = function (alternatives, maxOneMatch) {
            var matches = [];
            // remember the best match that is used for error messages
            var bestMatch = null;
            alternatives.forEach(function (subSchemaRef) {
                var subSchema = asSchema(subSchemaRef);
                var subValidationResult = new ValidationResult();
                var subMatchingSchemas = matchingSchemas.newSub();
                _this.validate(subSchema, subValidationResult, subMatchingSchemas);
                if (!subValidationResult.hasProblems()) {
                    matches.push(subSchema);
                }
                if (!bestMatch) {
                    bestMatch = { schema: subSchema, validationResult: subValidationResult, matchingSchemas: subMatchingSchemas };
                }
                else {
                    if (!maxOneMatch && !subValidationResult.hasProblems() && !bestMatch.validationResult.hasProblems()) {
                        // no errors, both are equally good matches
                        bestMatch.matchingSchemas.merge(subMatchingSchemas);
                        bestMatch.validationResult.propertiesMatches += subValidationResult.propertiesMatches;
                        bestMatch.validationResult.propertiesValueMatches += subValidationResult.propertiesValueMatches;
                    }
                    else {
                        var compareResult = subValidationResult.compare(bestMatch.validationResult);
                        if (compareResult > 0) {
                            // our node is the best matching so far
                            bestMatch = { schema: subSchema, validationResult: subValidationResult, matchingSchemas: subMatchingSchemas };
                        }
                        else if (compareResult === 0) {
                            // there's already a best matching but we are as good
                            bestMatch.matchingSchemas.merge(subMatchingSchemas);
                            bestMatch.validationResult.mergeEnumValues(subValidationResult);
                        }
                    }
                }
            });
            if (matches.length > 1 && maxOneMatch) {
                validationResult.problems.push({
                    location: { start: _this.start, end: _this.start + 1 },
                    severity: ProblemSeverity.Warning,
                    message: localize('oneOfWarning', "Matches multiple schemas when only one must validate.")
                });
            }
            if (bestMatch !== null) {
                validationResult.merge(bestMatch.validationResult);
                validationResult.propertiesMatches += bestMatch.validationResult.propertiesMatches;
                validationResult.propertiesValueMatches += bestMatch.validationResult.propertiesValueMatches;
                matchingSchemas.merge(bestMatch.matchingSchemas);
            }
            return matches.length;
        };
        if (Array.isArray(schema.anyOf)) {
            testAlternatives(schema.anyOf, false);
        }
        if (Array.isArray(schema.oneOf)) {
            testAlternatives(schema.oneOf, true);
        }
        if (Array.isArray(schema.enum)) {
            var val = this.getValue();
            var enumValueMatch = false;
            for (var _i = 0, _a = schema.enum; _i < _a.length; _i++) {
                var e = _a[_i];
                if (objects.equals(val, e)) {
                    enumValueMatch = true;
                    break;
                }
            }
            validationResult.enumValues = schema.enum;
            validationResult.enumValueMatch = enumValueMatch;
            if (!enumValueMatch) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    code: ErrorCode.EnumValueMismatch,
                    message: schema.errorMessage || localize('enumWarning', 'Value is not accepted. Valid values: {0}.', schema.enum.map(function (v) { return JSON.stringify(v); }).join(', '))
                });
            }
        }
        if (schema.const) {
            var val = this.getValue();
            if (!objects.equals(val, schema.const)) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    code: ErrorCode.EnumValueMismatch,
                    message: schema.errorMessage || localize('constWarning', 'Value must be {0}.', JSON.stringify(schema.const))
                });
                validationResult.enumValueMatch = false;
            }
            else {
                validationResult.enumValueMatch = true;
            }
            validationResult.enumValues = [schema.const];
        }
        if (schema.deprecationMessage && this.parent) {
            validationResult.problems.push({
                location: { start: this.parent.start, end: this.parent.end },
                severity: ProblemSeverity.Warning,
                message: schema.deprecationMessage
            });
        }
        matchingSchemas.add({ node: this, schema: schema });
    };
    return ASTNode;
}());
export { ASTNode };
var NullASTNode = /** @class */ (function (_super) {
    __extends(NullASTNode, _super);
    function NullASTNode(parent, name, start, end) {
        return _super.call(this, parent, 'null', name, start, end) || this;
    }
    NullASTNode.prototype.getValue = function () {
        return null;
    };
    return NullASTNode;
}(ASTNode));
export { NullASTNode };
var BooleanASTNode = /** @class */ (function (_super) {
    __extends(BooleanASTNode, _super);
    function BooleanASTNode(parent, name, value, start, end) {
        var _this = _super.call(this, parent, 'boolean', name, start, end) || this;
        _this.value = value;
        return _this;
    }
    BooleanASTNode.prototype.getValue = function () {
        return this.value;
    };
    return BooleanASTNode;
}(ASTNode));
export { BooleanASTNode };
var ArrayASTNode = /** @class */ (function (_super) {
    __extends(ArrayASTNode, _super);
    function ArrayASTNode(parent, name, start, end) {
        var _this = _super.call(this, parent, 'array', name, start, end) || this;
        _this.items = [];
        return _this;
    }
    ArrayASTNode.prototype.getChildNodes = function () {
        return this.items;
    };
    ArrayASTNode.prototype.getLastChild = function () {
        return this.items[this.items.length - 1];
    };
    ArrayASTNode.prototype.getValue = function () {
        return this.items.map(function (v) { return v.getValue(); });
    };
    ArrayASTNode.prototype.addItem = function (item) {
        if (item) {
            this.items.push(item);
            return true;
        }
        return false;
    };
    ArrayASTNode.prototype.visit = function (visitor) {
        var ctn = visitor(this);
        for (var i = 0; i < this.items.length && ctn; i++) {
            ctn = this.items[i].visit(visitor);
        }
        return ctn;
    };
    ArrayASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        var _this = this;
        if (!matchingSchemas.include(this)) {
            return;
        }
        _super.prototype.validate.call(this, schema, validationResult, matchingSchemas);
        if (Array.isArray(schema.items)) {
            var subSchemas_1 = schema.items;
            subSchemas_1.forEach(function (subSchemaRef, index) {
                var subSchema = asSchema(subSchemaRef);
                var itemValidationResult = new ValidationResult();
                var item = _this.items[index];
                if (item) {
                    item.validate(subSchema, itemValidationResult, matchingSchemas);
                    validationResult.mergePropertyMatch(itemValidationResult);
                }
                else if (_this.items.length >= subSchemas_1.length) {
                    validationResult.propertiesValueMatches++;
                }
            });
            if (this.items.length > subSchemas_1.length) {
                if (typeof schema.additionalItems === 'object') {
                    for (var i = subSchemas_1.length; i < this.items.length; i++) {
                        var itemValidationResult = new ValidationResult();
                        this.items[i].validate(schema.additionalItems, itemValidationResult, matchingSchemas);
                        validationResult.mergePropertyMatch(itemValidationResult);
                    }
                }
                else if (schema.additionalItems === false) {
                    validationResult.problems.push({
                        location: { start: this.start, end: this.end },
                        severity: ProblemSeverity.Warning,
                        message: localize('additionalItemsWarning', 'Array has too many items according to schema. Expected {0} or fewer.', subSchemas_1.length)
                    });
                }
            }
        }
        else {
            var itemSchema_1 = asSchema(schema.items);
            if (itemSchema_1) {
                this.items.forEach(function (item) {
                    var itemValidationResult = new ValidationResult();
                    item.validate(itemSchema_1, itemValidationResult, matchingSchemas);
                    validationResult.mergePropertyMatch(itemValidationResult);
                });
            }
        }
        var containsSchema = asSchema(schema.contains);
        if (containsSchema) {
            var doesContain = this.items.some(function (item) {
                var itemValidationResult = new ValidationResult();
                item.validate(containsSchema, itemValidationResult, NoOpSchemaCollector.instance);
                return !itemValidationResult.hasProblems();
            });
            if (!doesContain) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: schema.errorMessage || localize('requiredItemMissingWarning', 'Array does not contain required item.', schema.minItems)
                });
            }
        }
        if (schema.minItems && this.items.length < schema.minItems) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('minItemsWarning', 'Array has too few items. Expected {0} or more.', schema.minItems)
            });
        }
        if (schema.maxItems && this.items.length > schema.maxItems) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('maxItemsWarning', 'Array has too many items. Expected {0} or fewer.', schema.minItems)
            });
        }
        if (schema.uniqueItems === true) {
            var values_1 = this.items.map(function (node) {
                return node.getValue();
            });
            var duplicates = values_1.some(function (value, index) {
                return index !== values_1.lastIndexOf(value);
            });
            if (duplicates) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: localize('uniqueItemsWarning', 'Array has duplicate items.')
                });
            }
        }
    };
    return ArrayASTNode;
}(ASTNode));
export { ArrayASTNode };
var NumberASTNode = /** @class */ (function (_super) {
    __extends(NumberASTNode, _super);
    function NumberASTNode(parent, name, start, end) {
        var _this = _super.call(this, parent, 'number', name, start, end) || this;
        _this.isInteger = true;
        _this.value = Number.NaN;
        return _this;
    }
    NumberASTNode.prototype.getValue = function () {
        return this.value;
    };
    NumberASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        if (!matchingSchemas.include(this)) {
            return;
        }
        // work around type validation in the base class
        var typeIsInteger = false;
        if (schema.type === 'integer' || (Array.isArray(schema.type) && schema.type.indexOf('integer') !== -1)) {
            typeIsInteger = true;
        }
        if (typeIsInteger && this.isInteger === true) {
            this.type = 'integer';
        }
        _super.prototype.validate.call(this, schema, validationResult, matchingSchemas);
        this.type = 'number';
        var val = this.getValue();
        if (typeof schema.multipleOf === 'number') {
            if (val % schema.multipleOf !== 0) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: localize('multipleOfWarning', 'Value is not divisible by {0}.', schema.multipleOf)
                });
            }
        }
        function getExclusiveLimit(limit, exclusive) {
            if (typeof exclusive === 'number') {
                return exclusive;
            }
            if (typeof exclusive === 'boolean' && exclusive) {
                return limit;
            }
            return void 0;
        }
        function getLimit(limit, exclusive) {
            if (typeof exclusive !== 'boolean' || !exclusive) {
                return limit;
            }
            return void 0;
        }
        var exclusiveMinimum = getExclusiveLimit(schema.minimum, schema.exclusiveMinimum);
        if (typeof exclusiveMinimum === 'number' && val <= exclusiveMinimum) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('exclusiveMinimumWarning', 'Value is below the exclusive minimum of {0}.', exclusiveMinimum)
            });
        }
        var exclusiveMaximum = getExclusiveLimit(schema.maximum, schema.exclusiveMaximum);
        if (typeof exclusiveMaximum === 'number' && val >= exclusiveMaximum) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('exclusiveMaximumWarning', 'Value is above the exclusive maximum of {0}.', exclusiveMaximum)
            });
        }
        var minimum = getLimit(schema.minimum, schema.exclusiveMinimum);
        if (typeof minimum === 'number' && val < minimum) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('minimumWarning', 'Value is below the minimum of {0}.', minimum)
            });
        }
        var maximum = getLimit(schema.maximum, schema.exclusiveMaximum);
        if (typeof maximum === 'number' && val > maximum) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('maximumWarning', 'Value is above the maximum of {0}.', maximum)
            });
        }
    };
    return NumberASTNode;
}(ASTNode));
export { NumberASTNode };
var StringASTNode = /** @class */ (function (_super) {
    __extends(StringASTNode, _super);
    function StringASTNode(parent, name, isKey, start, end) {
        var _this = _super.call(this, parent, 'string', name, start, end) || this;
        _this.isKey = isKey;
        _this.value = '';
        return _this;
    }
    StringASTNode.prototype.getValue = function () {
        return this.value;
    };
    StringASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        if (!matchingSchemas.include(this)) {
            return;
        }
        _super.prototype.validate.call(this, schema, validationResult, matchingSchemas);
        if (schema.minLength && this.value.length < schema.minLength) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('minLengthWarning', 'String is shorter than the minimum length of {0}.', schema.minLength)
            });
        }
        if (schema.maxLength && this.value.length > schema.maxLength) {
            validationResult.problems.push({
                location: { start: this.start, end: this.end },
                severity: ProblemSeverity.Warning,
                message: localize('maxLengthWarning', 'String is longer than the maximum length of {0}.', schema.maxLength)
            });
        }
        if (schema.pattern) {
            var regex = new RegExp(schema.pattern);
            if (!regex.test(this.value)) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: schema.patternErrorMessage || schema.errorMessage || localize('patternWarning', 'String does not match the pattern of "{0}".', schema.pattern)
                });
            }
        }
        if (schema.format) {
            switch (schema.format) {
                case 'uri':
                case 'uri-reference':
                    {
                        var errorMessage = void 0;
                        if (!this.value) {
                            errorMessage = localize('uriEmpty', 'URI expected.');
                        }
                        else {
                            try {
                                var uri = Uri.parse(this.value);
                                if (!uri.scheme && schema.format === 'uri') {
                                    errorMessage = localize('uriSchemeMissing', 'URI with a scheme is expected.');
                                }
                            }
                            catch (e) {
                                errorMessage = e.message;
                            }
                        }
                        if (errorMessage) {
                            validationResult.problems.push({
                                location: { start: this.start, end: this.end },
                                severity: ProblemSeverity.Warning,
                                message: schema.patternErrorMessage || schema.errorMessage || localize('uriFormatWarning', 'String is not a URI: {0}', errorMessage)
                            });
                        }
                    }
                    break;
                case 'email':
                    {
                        if (!this.value.match(emailPattern)) {
                            validationResult.problems.push({
                                location: { start: this.start, end: this.end },
                                severity: ProblemSeverity.Warning,
                                message: schema.patternErrorMessage || schema.errorMessage || localize('emailFormatWarning', 'String is not an e-mail address.')
                            });
                        }
                    }
                    break;
                case 'color-hex':
                    {
                        if (!this.value.match(colorHexPattern)) {
                            validationResult.problems.push({
                                location: { start: this.start, end: this.end },
                                severity: ProblemSeverity.Warning,
                                message: schema.patternErrorMessage || schema.errorMessage || localize('colorHexFormatWarning', 'Invalid color format. Use #RGB, #RGBA, #RRGGBB or #RRGGBBAA.')
                            });
                        }
                    }
                    break;
                default:
            }
        }
    };
    return StringASTNode;
}(ASTNode));
export { StringASTNode };
var PropertyASTNode = /** @class */ (function (_super) {
    __extends(PropertyASTNode, _super);
    function PropertyASTNode(parent, key) {
        var _this = _super.call(this, parent, 'property', null, key.start) || this;
        _this.key = key;
        key.parent = _this;
        key.location = key.value;
        _this.colonOffset = -1;
        return _this;
    }
    PropertyASTNode.prototype.getChildNodes = function () {
        return this.value ? [this.key, this.value] : [this.key];
    };
    PropertyASTNode.prototype.getLastChild = function () {
        return this.value;
    };
    PropertyASTNode.prototype.setValue = function (value) {
        this.value = value;
        return value !== null;
    };
    PropertyASTNode.prototype.visit = function (visitor) {
        return visitor(this) && this.key.visit(visitor) && this.value && this.value.visit(visitor);
    };
    PropertyASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        if (!matchingSchemas.include(this)) {
            return;
        }
        if (this.value) {
            this.value.validate(schema, validationResult, matchingSchemas);
        }
    };
    return PropertyASTNode;
}(ASTNode));
export { PropertyASTNode };
var ObjectASTNode = /** @class */ (function (_super) {
    __extends(ObjectASTNode, _super);
    function ObjectASTNode(parent, name, start, end) {
        var _this = _super.call(this, parent, 'object', name, start, end) || this;
        _this.properties = [];
        return _this;
    }
    ObjectASTNode.prototype.getChildNodes = function () {
        return this.properties;
    };
    ObjectASTNode.prototype.getLastChild = function () {
        return this.properties[this.properties.length - 1];
    };
    ObjectASTNode.prototype.addProperty = function (node) {
        if (!node) {
            return false;
        }
        this.properties.push(node);
        return true;
    };
    ObjectASTNode.prototype.getFirstProperty = function (key) {
        for (var i = 0; i < this.properties.length; i++) {
            if (this.properties[i].key.value === key) {
                return this.properties[i];
            }
        }
        return null;
    };
    ObjectASTNode.prototype.getKeyList = function () {
        return this.properties.map(function (p) { return p.key.getValue(); });
    };
    ObjectASTNode.prototype.getValue = function () {
        var value = Object.create(null);
        this.properties.forEach(function (p) {
            var v = p.value && p.value.getValue();
            if (typeof v !== 'undefined') {
                value[p.key.getValue()] = v;
            }
        });
        return value;
    };
    ObjectASTNode.prototype.visit = function (visitor) {
        var ctn = visitor(this);
        for (var i = 0; i < this.properties.length && ctn; i++) {
            ctn = this.properties[i].visit(visitor);
        }
        return ctn;
    };
    ObjectASTNode.prototype.validate = function (schema, validationResult, matchingSchemas) {
        var _this = this;
        if (!matchingSchemas.include(this)) {
            return;
        }
        _super.prototype.validate.call(this, schema, validationResult, matchingSchemas);
        var seenKeys = Object.create(null);
        var unprocessedProperties = [];
        this.properties.forEach(function (node) {
            var key = node.key.value;
            seenKeys[key] = node.value;
            unprocessedProperties.push(key);
        });
        if (Array.isArray(schema.required)) {
            schema.required.forEach(function (propertyName) {
                if (!seenKeys[propertyName]) {
                    var key = _this.parent && _this.parent && _this.parent.key;
                    var location = key ? { start: key.start, end: key.end } : { start: _this.start, end: _this.start + 1 };
                    validationResult.problems.push({
                        location: location,
                        severity: ProblemSeverity.Warning,
                        message: localize('MissingRequiredPropWarning', 'Missing property "{0}".', propertyName)
                    });
                }
            });
        }
        var propertyProcessed = function (prop) {
            var index = unprocessedProperties.indexOf(prop);
            while (index >= 0) {
                unprocessedProperties.splice(index, 1);
                index = unprocessedProperties.indexOf(prop);
            }
        };
        if (schema.properties) {
            Object.keys(schema.properties).forEach(function (propertyName) {
                propertyProcessed(propertyName);
                var propertySchema = schema.properties[propertyName];
                var child = seenKeys[propertyName];
                if (child) {
                    if (typeof propertySchema === 'boolean') {
                        if (!propertySchema) {
                            var propertyNode = child.parent;
                            validationResult.problems.push({
                                location: { start: propertyNode.key.start, end: propertyNode.key.end },
                                severity: ProblemSeverity.Warning,
                                message: schema.errorMessage || localize('DisallowedExtraPropWarning', 'Property {0} is not allowed.', propertyName)
                            });
                        }
                        else {
                            validationResult.propertiesMatches++;
                            validationResult.propertiesValueMatches++;
                        }
                    }
                    else {
                        var propertyValidationResult = new ValidationResult();
                        child.validate(propertySchema, propertyValidationResult, matchingSchemas);
                        validationResult.mergePropertyMatch(propertyValidationResult);
                    }
                }
            });
        }
        if (schema.patternProperties) {
            Object.keys(schema.patternProperties).forEach(function (propertyPattern) {
                var regex = new RegExp(propertyPattern);
                unprocessedProperties.slice(0).forEach(function (propertyName) {
                    if (regex.test(propertyName)) {
                        propertyProcessed(propertyName);
                        var child = seenKeys[propertyName];
                        if (child) {
                            var propertySchema = schema.patternProperties[propertyPattern];
                            if (typeof propertySchema === 'boolean') {
                                if (!propertySchema) {
                                    var propertyNode = child.parent;
                                    validationResult.problems.push({
                                        location: { start: propertyNode.key.start, end: propertyNode.key.end },
                                        severity: ProblemSeverity.Warning,
                                        message: schema.errorMessage || localize('DisallowedExtraPropWarning', 'Property {0} is not allowed.', propertyName)
                                    });
                                }
                                else {
                                    validationResult.propertiesMatches++;
                                    validationResult.propertiesValueMatches++;
                                }
                            }
                            else {
                                var propertyValidationResult = new ValidationResult();
                                child.validate(propertySchema, propertyValidationResult, matchingSchemas);
                                validationResult.mergePropertyMatch(propertyValidationResult);
                            }
                        }
                    }
                });
            });
        }
        if (typeof schema.additionalProperties === 'object') {
            unprocessedProperties.forEach(function (propertyName) {
                var child = seenKeys[propertyName];
                if (child) {
                    var propertyValidationResult = new ValidationResult();
                    child.validate(schema.additionalProperties, propertyValidationResult, matchingSchemas);
                    validationResult.mergePropertyMatch(propertyValidationResult);
                }
            });
        }
        else if (schema.additionalProperties === false) {
            if (unprocessedProperties.length > 0) {
                unprocessedProperties.forEach(function (propertyName) {
                    var child = seenKeys[propertyName];
                    if (child) {
                        var propertyNode = child.parent;
                        validationResult.problems.push({
                            location: { start: propertyNode.key.start, end: propertyNode.key.end },
                            severity: ProblemSeverity.Warning,
                            message: schema.errorMessage || localize('DisallowedExtraPropWarning', 'Property {0} is not allowed.', propertyName)
                        });
                    }
                });
            }
        }
        if (schema.maxProperties) {
            if (this.properties.length > schema.maxProperties) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: localize('MaxPropWarning', 'Object has more properties than limit of {0}.', schema.maxProperties)
                });
            }
        }
        if (schema.minProperties) {
            if (this.properties.length < schema.minProperties) {
                validationResult.problems.push({
                    location: { start: this.start, end: this.end },
                    severity: ProblemSeverity.Warning,
                    message: localize('MinPropWarning', 'Object has fewer properties than the required number of {0}', schema.minProperties)
                });
            }
        }
        if (schema.dependencies) {
            Object.keys(schema.dependencies).forEach(function (key) {
                var prop = seenKeys[key];
                if (prop) {
                    var propertyDep = schema.dependencies[key];
                    if (Array.isArray(propertyDep)) {
                        propertyDep.forEach(function (requiredProp) {
                            if (!seenKeys[requiredProp]) {
                                validationResult.problems.push({
                                    location: { start: _this.start, end: _this.end },
                                    severity: ProblemSeverity.Warning,
                                    message: localize('RequiredDependentPropWarning', 'Object is missing property {0} required by property {1}.', requiredProp, key)
                                });
                            }
                            else {
                                validationResult.propertiesValueMatches++;
                            }
                        });
                    }
                    else {
                        var propertySchema = asSchema(propertyDep);
                        if (propertySchema) {
                            var propertyValidationResult = new ValidationResult();
                            _this.validate(propertySchema, propertyValidationResult, matchingSchemas);
                            validationResult.mergePropertyMatch(propertyValidationResult);
                        }
                    }
                }
            });
        }
        var propertyNames = asSchema(schema.propertyNames);
        if (propertyNames) {
            this.properties.forEach(function (f) {
                var key = f.key;
                if (key) {
                    key.validate(propertyNames, validationResult, NoOpSchemaCollector.instance);
                }
            });
        }
    };
    return ObjectASTNode;
}(ASTNode));
export { ObjectASTNode };
//region
export function asSchema(schema) {
    if (typeof schema === 'boolean') {
        return schema ? {} : { "not": {} };
    }
    return schema;
}
export var EnumMatch;
(function (EnumMatch) {
    EnumMatch[EnumMatch["Key"] = 0] = "Key";
    EnumMatch[EnumMatch["Enum"] = 1] = "Enum";
})(EnumMatch || (EnumMatch = {}));
var SchemaCollector = /** @class */ (function () {
    function SchemaCollector(focusOffset, exclude) {
        if (focusOffset === void 0) { focusOffset = -1; }
        if (exclude === void 0) { exclude = null; }
        this.focusOffset = focusOffset;
        this.exclude = exclude;
        this.schemas = [];
    }
    SchemaCollector.prototype.add = function (schema) {
        this.schemas.push(schema);
    };
    SchemaCollector.prototype.merge = function (other) {
        (_a = this.schemas).push.apply(_a, other.schemas);
        var _a;
    };
    SchemaCollector.prototype.include = function (node) {
        return (this.focusOffset === -1 || node.contains(this.focusOffset)) && (node !== this.exclude);
    };
    SchemaCollector.prototype.newSub = function () {
        return new SchemaCollector(-1, this.exclude);
    };
    return SchemaCollector;
}());
var NoOpSchemaCollector = /** @class */ (function () {
    function NoOpSchemaCollector() {
    }
    Object.defineProperty(NoOpSchemaCollector.prototype, "schemas", {
        get: function () { return []; },
        enumerable: true,
        configurable: true
    });
    NoOpSchemaCollector.prototype.add = function (schema) { };
    NoOpSchemaCollector.prototype.merge = function (other) { };
    NoOpSchemaCollector.prototype.include = function (node) { return true; };
    NoOpSchemaCollector.prototype.newSub = function () { return this; };
    NoOpSchemaCollector.instance = new NoOpSchemaCollector();
    return NoOpSchemaCollector;
}());
var ValidationResult = /** @class */ (function () {
    function ValidationResult() {
        this.problems = [];
        this.propertiesMatches = 0;
        this.propertiesValueMatches = 0;
        this.primaryValueMatches = 0;
        this.enumValueMatch = false;
        this.enumValues = null;
    }
    ValidationResult.prototype.hasProblems = function () {
        return !!this.problems.length;
    };
    ValidationResult.prototype.mergeAll = function (validationResults) {
        var _this = this;
        validationResults.forEach(function (validationResult) {
            _this.merge(validationResult);
        });
    };
    ValidationResult.prototype.merge = function (validationResult) {
        this.problems = this.problems.concat(validationResult.problems);
    };
    ValidationResult.prototype.mergeEnumValues = function (validationResult) {
        if (!this.enumValueMatch && !validationResult.enumValueMatch && this.enumValues && validationResult.enumValues) {
            this.enumValues = this.enumValues.concat(validationResult.enumValues);
            for (var _i = 0, _a = this.problems; _i < _a.length; _i++) {
                var error = _a[_i];
                if (error.code === ErrorCode.EnumValueMismatch) {
                    error.message = localize('enumWarning', 'Value is not accepted. Valid values: {0}.', this.enumValues.map(function (v) { return JSON.stringify(v); }).join(', '));
                }
            }
        }
    };
    ValidationResult.prototype.mergePropertyMatch = function (propertyValidationResult) {
        this.merge(propertyValidationResult);
        this.propertiesMatches++;
        if (propertyValidationResult.enumValueMatch || !propertyValidationResult.hasProblems() && propertyValidationResult.propertiesMatches) {
            this.propertiesValueMatches++;
        }
        if (propertyValidationResult.enumValueMatch && propertyValidationResult.enumValues && propertyValidationResult.enumValues.length === 1) {
            this.primaryValueMatches++;
        }
    };
    ValidationResult.prototype.compare = function (other) {
        var hasProblems = this.hasProblems();
        if (hasProblems !== other.hasProblems()) {
            return hasProblems ? -1 : 1;
        }
        if (this.enumValueMatch !== other.enumValueMatch) {
            return other.enumValueMatch ? -1 : 1;
        }
        if (this.primaryValueMatches !== other.primaryValueMatches) {
            return this.primaryValueMatches - other.primaryValueMatches;
        }
        if (this.propertiesValueMatches !== other.propertiesValueMatches) {
            return this.propertiesValueMatches - other.propertiesValueMatches;
        }
        return this.propertiesMatches - other.propertiesMatches;
    };
    return ValidationResult;
}());
export { ValidationResult };
var JSONDocument = /** @class */ (function () {
    function JSONDocument(root, syntaxErrors, comments) {
        if (syntaxErrors === void 0) { syntaxErrors = []; }
        if (comments === void 0) { comments = []; }
        this.root = root;
        this.syntaxErrors = syntaxErrors;
        this.comments = comments;
    }
    JSONDocument.prototype.getNodeFromOffset = function (offset) {
        return this.root && this.root.getNodeFromOffset(offset);
    };
    JSONDocument.prototype.getNodeFromOffsetEndInclusive = function (offset) {
        return this.root && this.root.getNodeFromOffsetEndInclusive(offset);
    };
    JSONDocument.prototype.visit = function (visitor) {
        if (this.root) {
            this.root.visit(visitor);
        }
    };
    JSONDocument.prototype.validate = function (schema) {
        if (this.root && schema) {
            var validationResult = new ValidationResult();
            this.root.validate(schema, validationResult, NoOpSchemaCollector.instance);
            return validationResult.problems;
        }
        return null;
    };
    JSONDocument.prototype.getMatchingSchemas = function (schema, focusOffset, exclude) {
        if (focusOffset === void 0) { focusOffset = -1; }
        if (exclude === void 0) { exclude = null; }
        var matchingSchemas = new SchemaCollector(focusOffset, exclude);
        if (this.root && schema) {
            this.root.validate(schema, new ValidationResult(), matchingSchemas);
        }
        return matchingSchemas.schemas;
    };
    return JSONDocument;
}());
export { JSONDocument };
export function parse(textDocument, config) {
    var problems = [];
    var text = textDocument.getText();
    var scanner = Json.createScanner(text, false);
    var comments = config && config.collectComments ? [] : void 0;
    function _scanNext() {
        while (true) {
            var token_1 = scanner.scan();
            _checkScanError();
            switch (token_1) {
                case 12 /* LineCommentTrivia */:
                case 13 /* BlockCommentTrivia */:
                    if (Array.isArray(comments)) {
                        comments.push({ start: scanner.getTokenOffset(), end: scanner.getTokenOffset() + scanner.getTokenLength() });
                    }
                    break;
                case 15 /* Trivia */:
                case 14 /* LineBreakTrivia */:
                    break;
                default:
                    return token_1;
            }
        }
    }
    function _accept(token) {
        if (scanner.getToken() === token) {
            _scanNext();
            return true;
        }
        return false;
    }
    function _errorAtRange(message, code, location) {
        if (problems.length === 0 || problems[problems.length - 1].location.start !== location.start) {
            problems.push({ message: message, location: location, code: code, severity: ProblemSeverity.Error });
        }
    }
    function _error(message, code, node, skipUntilAfter, skipUntil) {
        if (node === void 0) { node = null; }
        if (skipUntilAfter === void 0) { skipUntilAfter = []; }
        if (skipUntil === void 0) { skipUntil = []; }
        var start = scanner.getTokenOffset();
        var end = scanner.getTokenOffset() + scanner.getTokenLength();
        if (start === end && start > 0) {
            start--;
            while (start > 0 && /\s/.test(text.charAt(start))) {
                start--;
            }
            end = start + 1;
        }
        _errorAtRange(message, code, { start: start, end: end });
        if (node) {
            _finalize(node, false);
        }
        if (skipUntilAfter.length + skipUntil.length > 0) {
            var token_2 = scanner.getToken();
            while (token_2 !== 17 /* EOF */) {
                if (skipUntilAfter.indexOf(token_2) !== -1) {
                    _scanNext();
                    break;
                }
                else if (skipUntil.indexOf(token_2) !== -1) {
                    break;
                }
                token_2 = _scanNext();
            }
        }
        return node;
    }
    function _checkScanError() {
        switch (scanner.getTokenError()) {
            case 4 /* InvalidUnicode */:
                _error(localize('InvalidUnicode', 'Invalid unicode sequence in string.'), ErrorCode.InvalidUnicode);
                return true;
            case 5 /* InvalidEscapeCharacter */:
                _error(localize('InvalidEscapeCharacter', 'Invalid escape character in string.'), ErrorCode.InvalidEscapeCharacter);
                return true;
            case 3 /* UnexpectedEndOfNumber */:
                _error(localize('UnexpectedEndOfNumber', 'Unexpected end of number.'), ErrorCode.UnexpectedEndOfNumber);
                return true;
            case 1 /* UnexpectedEndOfComment */:
                _error(localize('UnexpectedEndOfComment', 'Unexpected end of comment.'), ErrorCode.UnexpectedEndOfComment);
                return true;
            case 2 /* UnexpectedEndOfString */:
                _error(localize('UnexpectedEndOfString', 'Unexpected end of string.'), ErrorCode.UnexpectedEndOfString);
                return true;
            case 6 /* InvalidCharacter */:
                _error(localize('InvalidCharacter', 'Invalid characters in string. Control characters must be escaped.'), ErrorCode.InvalidCharacter);
                return true;
        }
        return false;
    }
    function _finalize(node, scanNext) {
        node.end = scanner.getTokenOffset() + scanner.getTokenLength();
        if (scanNext) {
            _scanNext();
        }
        return node;
    }
    function _parseArray(parent, name) {
        if (scanner.getToken() !== 3 /* OpenBracketToken */) {
            return null;
        }
        var node = new ArrayASTNode(parent, name, scanner.getTokenOffset());
        _scanNext(); // consume OpenBracketToken
        var count = 0;
        var needsComma = false;
        while (scanner.getToken() !== 4 /* CloseBracketToken */ && scanner.getToken() !== 17 /* EOF */) {
            if (scanner.getToken() === 5 /* CommaToken */) {
                if (!needsComma) {
                    _error(localize('ValueExpected', 'Value expected'), ErrorCode.ValueExpected);
                }
                var commaOffset = scanner.getTokenOffset();
                _scanNext(); // consume comma
                if (scanner.getToken() === 4 /* CloseBracketToken */) {
                    if (needsComma) {
                        _errorAtRange(localize('TrailingComma', 'Trailing comma'), ErrorCode.TrailingComma, { start: commaOffset, end: commaOffset + 1 });
                    }
                    continue;
                }
            }
            else if (needsComma) {
                _error(localize('ExpectedComma', 'Expected comma'), ErrorCode.CommaExpected);
            }
            if (!node.addItem(_parseValue(node, count++))) {
                _error(localize('PropertyExpected', 'Value expected'), ErrorCode.ValueExpected, null, [], [4 /* CloseBracketToken */, 5 /* CommaToken */]);
            }
            needsComma = true;
        }
        if (scanner.getToken() !== 4 /* CloseBracketToken */) {
            return _error(localize('ExpectedCloseBracket', 'Expected comma or closing bracket'), ErrorCode.CommaOrCloseBacketExpected, node);
        }
        return _finalize(node, true);
    }
    function _parseProperty(parent, keysSeen) {
        var key = _parseString(null, null, true);
        if (!key) {
            if (scanner.getToken() === 16 /* Unknown */) {
                // give a more helpful error message
                _error(localize('DoubleQuotesExpected', 'Property keys must be doublequoted'), ErrorCode.Undefined);
                key = new StringASTNode(null, null, true, scanner.getTokenOffset(), scanner.getTokenOffset() + scanner.getTokenLength());
                key.value = scanner.getTokenValue();
                _scanNext(); // consume Unknown
            }
            else {
                return null;
            }
        }
        var node = new PropertyASTNode(parent, key);
        var seen = keysSeen[key.value];
        if (seen) {
            problems.push({ location: { start: node.key.start, end: node.key.end }, message: localize('DuplicateKeyWarning', "Duplicate object key"), code: ErrorCode.Undefined, severity: ProblemSeverity.Warning });
            if (seen instanceof PropertyASTNode) {
                problems.push({ location: { start: seen.key.start, end: seen.key.end }, message: localize('DuplicateKeyWarning', "Duplicate object key"), code: ErrorCode.Undefined, severity: ProblemSeverity.Warning });
            }
            keysSeen[key.value] = true; // if the same key is duplicate again, avoid duplicate error reporting
        }
        else {
            keysSeen[key.value] = node;
        }
        if (scanner.getToken() === 6 /* ColonToken */) {
            node.colonOffset = scanner.getTokenOffset();
            _scanNext(); // consume ColonToken
        }
        else {
            _error(localize('ColonExpected', 'Colon expected'), ErrorCode.ColonExpected);
            if (scanner.getToken() === 10 /* StringLiteral */ && textDocument.positionAt(key.end).line < textDocument.positionAt(scanner.getTokenOffset()).line) {
                node.end = key.end;
                return node;
            }
        }
        if (!node.setValue(_parseValue(node, key.value))) {
            return _error(localize('ValueExpected', 'Value expected'), ErrorCode.ValueExpected, node, [], [2 /* CloseBraceToken */, 5 /* CommaToken */]);
        }
        node.end = node.value.end;
        return node;
    }
    function _parseObject(parent, name) {
        if (scanner.getToken() !== 1 /* OpenBraceToken */) {
            return null;
        }
        var node = new ObjectASTNode(parent, name, scanner.getTokenOffset());
        var keysSeen = Object.create(null);
        _scanNext(); // consume OpenBraceToken
        var needsComma = false;
        while (scanner.getToken() !== 2 /* CloseBraceToken */ && scanner.getToken() !== 17 /* EOF */) {
            if (scanner.getToken() === 5 /* CommaToken */) {
                if (!needsComma) {
                    _error(localize('PropertyExpected', 'Property expected'), ErrorCode.PropertyExpected);
                }
                var commaOffset = scanner.getTokenOffset();
                _scanNext(); // consume comma
                if (scanner.getToken() === 2 /* CloseBraceToken */) {
                    if (needsComma) {
                        _errorAtRange(localize('TrailingComma', 'Trailing comma'), ErrorCode.TrailingComma, { start: commaOffset, end: commaOffset + 1 });
                    }
                    continue;
                }
            }
            else if (needsComma) {
                _error(localize('ExpectedComma', 'Expected comma'), ErrorCode.CommaExpected);
            }
            if (!node.addProperty(_parseProperty(node, keysSeen))) {
                _error(localize('PropertyExpected', 'Property expected'), ErrorCode.PropertyExpected, null, [], [2 /* CloseBraceToken */, 5 /* CommaToken */]);
            }
            needsComma = true;
        }
        if (scanner.getToken() !== 2 /* CloseBraceToken */) {
            return _error(localize('ExpectedCloseBrace', 'Expected comma or closing brace'), ErrorCode.CommaOrCloseBraceExpected, node);
        }
        return _finalize(node, true);
    }
    function _parseString(parent, name, isKey) {
        if (scanner.getToken() !== 10 /* StringLiteral */) {
            return null;
        }
        var node = new StringASTNode(parent, name, isKey, scanner.getTokenOffset());
        node.value = scanner.getTokenValue();
        return _finalize(node, true);
    }
    function _parseNumber(parent, name) {
        if (scanner.getToken() !== 11 /* NumericLiteral */) {
            return null;
        }
        var node = new NumberASTNode(parent, name, scanner.getTokenOffset());
        if (scanner.getTokenError() === 0 /* None */) {
            var tokenValue = scanner.getTokenValue();
            try {
                var numberValue = JSON.parse(tokenValue);
                if (typeof numberValue !== 'number') {
                    return _error(localize('InvalidNumberFormat', 'Invalid number format.'), ErrorCode.Undefined, node);
                }
                node.value = numberValue;
            }
            catch (e) {
                return _error(localize('InvalidNumberFormat', 'Invalid number format.'), ErrorCode.Undefined, node);
            }
            node.isInteger = tokenValue.indexOf('.') === -1;
        }
        return _finalize(node, true);
    }
    function _parseLiteral(parent, name) {
        var node;
        switch (scanner.getToken()) {
            case 7 /* NullKeyword */:
                node = new NullASTNode(parent, name, scanner.getTokenOffset());
                break;
            case 8 /* TrueKeyword */:
                node = new BooleanASTNode(parent, name, true, scanner.getTokenOffset());
                break;
            case 9 /* FalseKeyword */:
                node = new BooleanASTNode(parent, name, false, scanner.getTokenOffset());
                break;
            default:
                return null;
        }
        return _finalize(node, true);
    }
    function _parseValue(parent, name) {
        return _parseArray(parent, name) || _parseObject(parent, name) || _parseString(parent, name, false) || _parseNumber(parent, name) || _parseLiteral(parent, name);
    }
    var _root = null;
    var token = _scanNext();
    if (token !== 17 /* EOF */) {
        _root = _parseValue(null, null);
        if (!_root) {
            _error(localize('Invalid symbol', 'Expected a JSON object, array or literal.'), ErrorCode.Undefined);
        }
        else if (scanner.getToken() !== 17 /* EOF */) {
            _error(localize('End of file expected', 'End of file expected.'), ErrorCode.Undefined);
        }
    }
    return new JSONDocument(_root, problems, comments);
}
//# sourceMappingURL=jsonParser.js.map