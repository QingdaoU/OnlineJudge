<template>
    <h3>{{ $t("announcement.announcementList") }}</h3>
    <table class="table table-striped">
        <tr>
            <th>ID</th>
            <th>{{ $t("adminUtils.title") }}</th>
            <th>{{ $t("adminUtils.createTime") }}</th>
            <th>{{ $t("adminUtils.lastUpdateTime") }}</th>
            <th>{{ $t("adminUtils.createdBy") }}</th>
            <th>{{ $t("adminUtils.isVisible") }}</th>
            <th>{{ $t("adminUtils.management") }}</th>
        </tr>
        <tr v-for="announcement in announcementList">
            <td>{{ announcement.id }}</td>
            <td>{{ announcement.title }}</td>
            <td>{{ announcement.create_time }}</td>
            <td>{{ announcement.last_update_time }}</td>
            <td>{{ announcement.created_by.username }}</td>
            <td>{{ $t(announcementStatus[announcement.visible?1:0]) }}</td>
            <td>
                <button class="btn-sm btn-info" v-on:click="edit(announcement.id)">{{ $t("adminUtils.edit") }}</button>
            </td>
        </tr>
    </table>
    <pager :pagination="pagination" :callback="loadData"></pager>

    <create-announcement></create-announcement>
</template>

<script>
    import pager from "../utils/pager.vue"
    import createAnnouncement from "./createAnnouncement.vue"

    export default({
        data() {
            return {
                announcementStatus: ["adminUtils.visible", "adminUtils.invisible"],
                announcementList: [],
                pagination: {
                    currentPage: 1,
                    totalPages: 10
                }
            }
        },
        methods: {
            loadData() {
                this.request({
                    url: "/api/admin/announcement/?paging=true&page_size=2&page=" + this.pagination.currentPage,
                    method: "GET",
                    success: (data)=> {
                        this.announcementList = data.data.results;
                        this.pagination.totalPages = data.data.total_page;
                    }
                })
            },
            edit(announcementId){
                this.$router.go("/announcement/edit/" + announcementId)
            },
        },
        route: {
            data(){
                this.loadData();
            }
        },
        components: {
            pager,
            createAnnouncement
        }
    })
</script>

<style>

</style>