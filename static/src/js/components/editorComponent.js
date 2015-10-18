define("editorComponent", ["jquery", "avalon", "editor"], function ($, avalon, editor) {
    avalon.component("ms:editor", {
        $template: "<textarea ms-attr-id='{{ editorId }}' ms-duplex='content' ms-attr-placeholder='placeholder'></textarea>",
        editorId: "editorId",
        content: "",
        placeholder: "",
        $editor: {},
        $ready: function (vm, el) {
            el.msRetain = true;
            vm.$editor = editor($("#" + vm.editorId));
            vm.$watch("content", function (oldValue, newValue) {
                vm.$editor.setValue(oldValue);
            })
        }
    })
});
