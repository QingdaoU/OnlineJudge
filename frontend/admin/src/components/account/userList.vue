<template>
    <div>
        <div class="right">
            <form class="form-inline" onsubmit="return false;">
                <div class="form-group-sm">
                    <label>{{ $t("adminUtils.search") }}</label>
                    <input name="keyword" class="form-control" placeholder='{{ $t("adminUtils.inputKeyword") }}'
                           v-model="keyword">
                    <button type="button" class="btn btn-primary" v-on:click="search">{{ $t("adminUtils.search") }}
                    </button>
                </div>
            </form>
            <br>
        </div>
        <table class="table table-striped">
            <tr>
                <th>ID</th>
                <th>{{ $t("user.username") }}</th>
                <th>{{ $t("user.createTime") }}</th>
                <th>{{ $t("user.realName") }}</th>
                <th>{{ $t("user.email") }}</th>
                <th>{{ $t("user.adminType") }}</th>
                <th>{{ $t("user.management") }}</th>
            </tr>
            <tr v-for="user in userList">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.create_time }}</td>
                <td>{{ user.real_name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ $t(adminType[user.admin_type]) }}</td>
                <td>
                    <button class="btn-sm btn-info" v-on:click="edit(user.id)">{{ $t("user.edit") }}</button>
                    <a target="_blank" href="/submissions/?user_id={{ user.id }}">
                        {{ $t("user.submission") }}
                    </a>
                </td>
            </tr>
        </table>
        <input type="checkbox" v-model="showAdminOnly"> {{ $t("user.showAdminOnly") }}

        <pager :pagination="pagination" :callback="loadData"></pager>
    </div>
</template>
<script>
    import Vue from 'vue'
    import Router from 'vue-router'
    import pager from '../utils/pager.vue'

    //import editUser from './editUser.vue'

    export default {
        data: function () {
            return {
                keyword: "",
                userList: [],
                adminType: ["adminUtils.regularUser", "adminUtils.admin", "adminUtils.superAdmin"],
                showAdminOnly: false,

                pagination: {
                    currentPage: 1,
                    totalPages: 10
                }
            }
        },
        route: {
            data(){
                this.$watch('showAdminOnly', function (val) {
                    sessionStorage.showAdminOnly = JSON.stringify(val);
                    this.$router.go({path: "/user/1", query: {_: (new Date()).getTime()}});
                });

                this.pagination.currentPage = this.$route.params.page;

                if (sessionStorage.showAdminOnly) {
                    this.showAdminOnly = JSON.parse(sessionStorage.showAdminOnly);
                }
                if (sessionStorage.userListSearchKeyword) {
                    this.keyword = sessionStorage.userListSearchKeyword;
                }
                this.loadData();
            }
        },
        methods: {
            loadData() {
                var url = "/api/admin/user/?paging=true&page_size=2&page=" + this.pagination.currentPage;
                if (this.keyword) {
                    url += ("&keyword=" + this.keyword)
                }
                else if (this.showAdminOnly) {
                    url += "&admin_type=1";
                }
                this.request({
                    url: url,
                    method: "GET",
                    success: (data)=> {
                        this.userList = data.data.results;
                        this.pagination.totalPages = data.data.total_page;
                    }
                })
            },
            search() {
                sessionStorage.userListSearchKeyword = this.keyword;
                this.$router.go({path: "/user/1", query: {_: (new Date()).getTime()}});
                // pager goto page 1
                // url -> /user/1
            },
            edit(userId) {
                this.$router.go("/user/edit/" + userId)
            }
        },
        components: {
            pager
        }
    }
</script>