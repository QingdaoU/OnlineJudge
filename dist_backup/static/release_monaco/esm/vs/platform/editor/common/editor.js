/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
 *  Licensed under the MIT License. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
'use strict';
import { createDecorator } from '../../instantiation/common/instantiation.js';
export var IEditorService = createDecorator('editorService');
/**
 * Possible locations for opening an editor.
 */
export var Position;
(function (Position) {
    /** Opens the editor in the first position replacing the input currently showing */
    Position[Position["ONE"] = 0] = "ONE";
    /** Opens the editor in the second position replacing the input currently showing */
    Position[Position["TWO"] = 1] = "TWO";
    /** Opens the editor in the third most position replacing the input currently showing */
    Position[Position["THREE"] = 2] = "THREE";
})(Position || (Position = {}));
export var POSITIONS = [Position.ONE, Position.TWO, Position.THREE];
export var Direction;
(function (Direction) {
    Direction[Direction["LEFT"] = 0] = "LEFT";
    Direction[Direction["RIGHT"] = 1] = "RIGHT";
})(Direction || (Direction = {}));
export var Verbosity;
(function (Verbosity) {
    Verbosity[Verbosity["SHORT"] = 0] = "SHORT";
    Verbosity[Verbosity["MEDIUM"] = 1] = "MEDIUM";
    Verbosity[Verbosity["LONG"] = 2] = "LONG";
})(Verbosity || (Verbosity = {}));
