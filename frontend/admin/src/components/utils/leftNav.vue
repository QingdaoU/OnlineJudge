<template>
    <div id="left-nav">
        <ul class="list-group">
            <li class="list-group-header">name</li>
            <li class="list-group-item">
                <a v-link="{path: '/user'}">{{ $t("nav.UserManagement") }}</a>
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