<template>
    <div>
        <div>
            <p class="sub-label">{{ $t("problem.chooseLanguage") }}</p>
            <div id="language-radio">
                <template v-for="language in languageList">
                    <span class="radio-inline">
                        <input type="radio" value="{{ language.name }}" name="language" v-model="selectedLanguage">
                        {{ language.name }} ({{ language.description }})
                    </span>
                </template>
            </div>
        </div>
        <div>
            <p class="sub-label">{{ $t("problem.submitCode") }}</p>
            <textarea id="{{ editorId }}"></textarea>
        </div>
    </div>
</template>

<script>
    import CodeMirror from "codemirror"
    import "codemirror/mode/javascript/javascript"
    import "codemirror/mode/python/python"
    import "codemirror/mode/clike/clike"
    import "codemirror/mode/meta"

    function getMime(languageName) {
        for (let item of CodeMirror.modeInfo) {
            if (item.name == languageName) {
                return item.mime;
            }
        }
        throw "Invalid language " + languageName;
    }

    export default({
        props: {
            languageList: {
                type: Array,
                required: true,
            },
            selectedLanguage: {
                type: String,
                required: true,
            }
        },
        data() {
            return {
                editor: {},
                editorId: Math.random().toString(36).substr(2),
            }
        },
        watch: {
            language(newVal, oldVal) {
                this.editor.setOption("mode", getMime(newVal.name))
            }
        },
        attached() {
            this.editor = CodeMirror.fromTextArea(document.getElementById(this.editorId), {
                lineNumbers: true,
                mode: getMime(this.selectedLanguage),
                indentUnit: 4,
                matchBrackets: true
            });
        },
        methods: {
            setLanguage(language) {
                this.selectedLanguage = languageName;
            },
            setCode(code) {
                this.editor.setValue(code);
            },
            getCode() {
                return this.editor.getValue();
            },
            getLanguage() {
                return this.selectedLanguage;
            }
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

    #language-radio {
        margin: 5px;
    }
</style>