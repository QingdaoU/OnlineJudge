<template>
    <h3>
        {{ $t("announcement.createAnnouncement") }}
    </h3>
    <div>
        <div class="row">
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.title") }}</label>
                <input type="text" class="form-control" v-model="title" required>
            </div>
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.content") }}</label>
                <simditor editorid="createAnnouncement" v-ref:editor></simditor>
            </div>
        </div>
        <div class="form-group">
            <input type="submit" class="btn btn-primary" v-on:click="submit" value='{{ $t("adminUtils.submit") }}'>
        </div>
    </div>
</template>

<script>
    import simditor from "../../components/simditor.vue"

    export default({
        data() {
            return {
                title: ""
            }
        },
        methods: {
            submit() {
                var content = this.$refs.editor.getContent();
                if (!content) {
                    alert(this.$t("announcement.contentCanNotBeEmpty"));
                    return;
                }
                this.request({
                    url: "/api/admin/announcement/",
                    method: "post",
                    data: {title: this.title, content: content}
                })
            }
        },
        components: {
            simditor
        }
    })
</script>