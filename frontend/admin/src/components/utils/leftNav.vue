<template>
    <div id="left-nav">
        <ul class="list-group">
            <template v-for="item in adminNav">
                <li class="list-group-header">{{ $t(item.groupName) }}</li>
                <li class="list-group-item" v-link-active v-for="child in item.children">
                    <a v-link="{path: child.link}">{{ $t(child.name) }}</a>
                </li>
            </template>
        </ul>
    </div>
</template>
<script>
    export default {
        data() {
            return {
                adminNav: [
                    {
                        groupName: "nav.general",
                        children: [
                            {name: "nav.userManagement", link: "/user/1"},
                            {name: "nav.announcementManagement", link: "/announcement/1"}
                        ]
                    },
                    {
                        groupName: "nav.problemManagement",
                        children: [
                            {name: "nav.createProblem", link: "/problem/create"},
                            {name: "problem.problemList", link: "/problem/1"}]
                    }
                ]
            }
        }
    }
</script>