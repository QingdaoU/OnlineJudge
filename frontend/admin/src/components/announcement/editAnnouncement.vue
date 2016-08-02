<template>
    <back></back>
    <h3>
        {{ $t("announcement.editAnnouncement") }}
    </h3>
    <form v-on:submit="submit">
        <div class="row">
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.title") }}</label>
                <input type="text" class="form-control" v-model="announcement.title" required>
            </div>
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.content") }}</label>
                <simditor editorid="editAnnouncement" v-ref:editor></simditor>
            </div>
        </div>
        <div class="form-group">
            <label>{{ $t("adminUtils.isVisible") }}</label>
            <input type="checkbox" class="form-control" v-model="announcement.visible">
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
                announcement: {}
            }
        },
        methods: {
            submit() {
                this.request({
                    url: "/api/admin/announcement/",
                    method: "put",
                    data: {
                        id: this.$route.params.announcementId,
                        title: this.announcement.title,
                        content: this.$refs.editor.getContent(),
                        visible: this.announcement.visible
                    }
                })
            }
        },
        route: {
            data() {
                this.request({
                    url: "/api/admin/announcement/?announcement_id=" + this.$route.params.announcementId,
                    method: "get",
                    success: (data)=> {
                        this.announcement = data.data;
                        this.$refs.editor.setContent(data.data.content);
                    }
                })
            }
        },
        components: {
            simditor,
            back
        }
    })
</script>