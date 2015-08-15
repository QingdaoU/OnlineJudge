define("codeMirror", ["_codeMirror", "codeMirrorClang"], function(CodeMirror){
    function codeMirror(selector, language){
        return CodeMirror.fromTextArea(selector,
            {
                indentUnit: 4,
                lineNumbers: true,
                matchBrackets: true,
                mode: language
            });
    }
    return codeMirror;
});