<template>
    <div id="left-nav">
        <ul class="list-group">
            <li class="list-group-header">name</li>
            <li class="list-group-item" v-link-active>
                <a v-link="{path: '/user'}">{{ $t("nav.userManagement") }}</a>
            </li>
            <li class="list-group-item" v-link-active>
                <a v-link="{path: '/announcement'}">{{ $t("nav.announcementManagement") }}</a>
            </li>
        </ul>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                adminNav: [{}, {}]
            }
        }
    }
</script>