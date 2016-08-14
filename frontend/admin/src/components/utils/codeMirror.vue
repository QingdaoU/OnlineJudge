<template>
    <textarea id="{{ editorId }}"></textarea>
</template>

<script>
    import CodeMirror from "codemirror"
    import "codemirror/mode/javascript/javascript"
    import "codemirror/mode/python/python"

    export default({
        data() {
            return {
                editor: {},
                editorId: Math.random().toString(36).substr(2),
                language: "python"
            }
        },
        attached() {
            CodeMirror.fromTextArea(document.getElementById(this.editorId), {
                lineNumbers: true,
                mode: this.language,
                indentUnit: 4,
                matchBrackets: true
            });
        }
    })
</script>

<style>
    @import "../../../../static/css/CodeMirror.css";

    .CodeMirror {
        min-height: 250px;
        _height: 250px;
        height: auto;
    }

    .CodeMirror-scroll {
        overflow: auto;
        min-height: 250px;
        height: auto;
        position: relative;
        outline: none;
    }
</style>