define("editor", ["simditor"], function(Simditor){
    function editor(selector){
        return new Simditor({
            textarea: $(selector),
            toolbar: [
                "bold", "color", "ol", "ul", "code", "link", "image"
            ],
            toolbarFloat: false,
            defaultImage: null,
            upload: {
                url: "/api/admin/upload_image/",
                params: null,
                fileKey: "image",
                connectionCount: 3,
                leaveConfirm: "正在上传文件，如果离开上传会自动取消"
            },
            pasteImage: true,
            imageButton: ["upload"]
        });
    }
    return editor;
});