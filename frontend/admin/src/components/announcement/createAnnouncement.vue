<template>
    <h3>
        {{ $t("announcement.createAnnouncement") }}
    </h3>
    <form v-on:submit="submit">
        <div class="row">
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.title") }}</label>
                <input type="text" class="form-control">
            </div>
            <div class="form-group col-md-12">
                <label>{{ $t("adminUtils.content") }}</label>
                <simditor editorid="createAnnouncement" v-ref:editor></simditor>
            </div>
        </div>
        <div class="form-group">
            <input type="submit" class="btn btn-primary" value='{{ $t("adminUtils.submit") }}'>
        </div>
    </form>
</template>

<script>
    import simditor from "../utils/simditor.vue"

    export default({
        data() {
            return {}
        },
        methods: {
            submit() {

            }
        },
        route: {
        },
        components: {
            simditor
        }
    })
</script>