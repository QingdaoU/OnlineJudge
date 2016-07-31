<template>
    <div>
        <simditor editorid="problem_detail"></simditor>

        <uploader uploaderid="uploader"></uploader>
    </div>
</template>

<script>
    import simditor from "../utils/simditor.vue"
    import uploader from "../utils/uploader.vue"

    export default({
        components: {
            simditor,
            uploader
        }
    })
</script>