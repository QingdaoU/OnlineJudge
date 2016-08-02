<template>
    <back></back>
    <h3>
        {{ $t("announcement.editAnnouncement") }}
    </h3>
    <form v-on:submit="submit">
        <div class="row">
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.title") }}</label>
                <input type="text" class="form-control">
            </div>
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.content") }}</label>
                <simditor editorid="editAnnouncement" :content="content" v-ref:editor></simditor>
            </div>
        </div>
        <div class="form-group">
            <input type="submit" class="btn btn-success" value='{{ $t("adminUtils.saveChanges") }}'>
        </div>
    </form>
</template>

<script>
    import simditor from "../utils/simditor.vue"
    import back from "../utils/back.vue"

    export default({
        data() {
            return {
                announcement: {},
                content: ""
            }
        },
        methods: {
            submit() {

            }
        },
        components: {
            simditor,
            back
        }
    })
</script>