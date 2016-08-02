<template>
    <textarea id="{{ editorid }}"></textarea>
</template>
<script>
    import Simditor from 'simditor'
    import SimditorMakrdown from "simditor-markdown"

    export default{
        data() {
            return {
                editor: {}
            }
        },
        props: {
            editorid: {
                required: true
            },
            content: {
                required: true
            }
        },
        methods: {
            setContent(content){
                this.editor.setValue(content);
            },
            getContent() {
                return this.editor.getValue();
            }
        },
        attached() {
            var self = this;
            self.editor = new Simditor({
                textarea: document.getElementById(self.editorid),
                upload: {url: "/", fileKey: "file"},
                toolbar: ['bold', 'italic', 'underline', 'color', 'image', 'ol', 'ul', 'markdown']
            });
        }
    }
</script>

<style scoped>
    @import "../../../../static/css/simditor.css";
    @import "../../../../static/css/simditor-markdown.css";
    @import "../../../../static/css/webuploader.css";
</style>