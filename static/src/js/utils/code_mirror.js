define("code_mirror", ["_code_mirror", "code_mirror_clang"], function(CodeMirror){
    function code_mirror(selector, language){
        return CodeMirror.fromTextArea(selector,
            {
                indentUnit: 4,
                lineNumbers: true,
                matchBrackets: true,
                mode: language
            });
    }
    return code_mirror;
});