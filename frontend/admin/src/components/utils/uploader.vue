<template>
    <div id="{{ uploaderid }}">
        <div class="btns">
            <div id="picker"> picker</div>
        </div>
    </div>

</template>


<script>
    import WebUploader from "webuploader"

    export default ({
        props: {
            uploaderid: {
                required: true
            },
            uploadpath: {
                required: false,
                default: "/server"
            },
            accept: {
                required: false,
                default(){
                    return {
                        title: 'Images',
                        extensions: 'gif,jpg,jpeg,bmp,png',
                        mimeTypes: 'image/*'
                    }
                }
            }

        },
        attached() {
            var self = this;
            var uploader = WebUploader.create({
                dnd: '#' + self.uploaderid,
                runtimeOrder: "html5",
                server: self.uploadpath,
                pick: '#' + self.uploaderid,
                resize: false,
                auto: true,
                accept: self.accept
            });
        }
    })
</script>

<style>

</style>