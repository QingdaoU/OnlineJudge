<template>
    <span>
        <popover trigger="hover" effect="fade" placement="top" header="false"
                 v-bind:content="translate()">
            <span class="glyphicon glyphicon-question-sign"></span>
        </popover>
    </span>
</template>

<script>
    import {popover} from "vue-strap"

    export default({
        props: {
            name: ""
        },
        methods: {
            translate() {
                return this.$t("help." + this.name);
            }
        },
        components: {
            popover
        }
    })
</script>