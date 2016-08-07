<template>
    <div id="{{ uploaderId }}">
        <div class="btns">
            <div id="picker">{{ $t("adminUtils.chooseFile") }}</div>
        </div>
    </div>
</template>


<script>
    import WebUploader from "webuploader"
    import getCookie from "../../utils/cookie"

    export default ({
        props: {
            uploaderId: {
                required: true,
            },
            uploadPath: {
                required: true,
            },
            accept: {
                required: true,
            },
            uploadSuccess: {
                required: true
            },
            uploadProgress: {
                required: true
            },
            uploadError: {
                required: true
            }
        },
        attached() {
            var self = this;
            var uploader = WebUploader.create({
                dnd: '#' + self.uploaderId,
                runtimeOrder: "html5",
                server: self.uploadpath,
                pick: '#' + self.uploaderId,
                resize: false,
                auto: true,
                accept: self.accept
            });
            uploader.on("uploadBeforeSend", (obj, data, headers)=> {
                headers["X-CSRFToken"] = getCookie("csrftoken");
            });
            uploader.on("uploadProgress", (f, percentage)=> {
                this.uploadProgress = Math.round(percentage * 100);
            });
            uploader.on("uploadError", this.uploadError);
            uploader.on("uploadSuccess", this.uploadSuccess);
        }
    })
</script>

<style>

</style>