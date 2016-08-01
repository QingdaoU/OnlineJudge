<template>
    <div>
        <back></back>
        <h3>{{ $t("user.editUser") }}</h3>
        <form v-on:submit="submit">
            <div class="row">
                <div class="form-group col-md-4"><label>ID</label>
                    <input type="number" class="form-control" v-model="user.id" readonly>
                </div>
                <div class="form-group col-md-4">
                    <label>{{ $t("user.username") }}</label>
                    <input type="text" class="form-control" v-model="user.username" maxlength="30" required>
                </div>
                <div class="form-group col-md-4">
                    <label>{{ $t("user.realName") }}</label>
                    <input type="text" class="form-control" maxlength="30" v-model="user.real_name" required>
                </div>
            </div>
            <div class="row">
                <div class="form-group col-md-4">
                    <label>{{ $t("user.newPassword") }}</label>
                    <input type="password" class="form-control"
                           placeholder='{{ $t("user.leaveBlankIfDoNotChangePassword")}}' v-model="newPassword" minlength="6">
                </div>
                <div class="form-group col-md-4">
                    <label>{{ $t("user.email") }}</label>
                    <input type="email" class="form-control" v-model="user.email" required>
                </div>
                <div class="form-group col-md-4">
                    <label>{{ $t("user.adminType") }}</label>
                    <select class="form-control" v-model="user.admin_type">
                        <option v-for="item in adminType" v-bind:value="item.value">{{ $t(item.name) }}</option>
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="form-group col-md-3">
                    <label>{{ $t("user.openAPIFunction") }}</label>
                    <input type="checkbox" class="form-control" v-model="user.open_api">
                </div>
                <div class="form-group col-md-3">
                    <label>{{ $t("user.tfaAuth") }}</label>
                    <input type="checkbox" class="form-control" v-model="user.two_factor_auth">
                </div>
                <div class="form-group col-md-3">
                    <label>{{ $t("user.isDisabled") }}</label>
                    <input type="checkbox" class="form-control" v-model="user.is_disabled">
                </div>
            </div>
            <div v-show="user.admin_type==adminType[1].value">
                <h4>{{ $t("user.adminExtraPermission") }}</h4>
                <div class="row">
                    <div class="form-group col-md-3">
                        <label>{{ $t("user.createPublicContest") }}</label>
                        <input type="checkbox" class="form-control" v-model="permission.createPublicContest">
                    </div>
                    <div class="form-group col-md-3">
                        <label>{{ $t("user.manageAllContest") }}</label>
                        <input type="checkbox" class="form-control" v-model="permission.manageAllContest">
                    </div>
                    <div class="form-group col-md-3">
                        <label>{{ $t("user.manageOwnProblem") }}</label>
                        <input type="checkbox" class="form-control" v-model="permission.manageOwnProblem">
                    </div>
                    <div class="form-group col-md-3">
                        <label>{{ $t("user.manageAllProblem") }}</label>
                        <input type="checkbox" class="form-control" v-model="permission.manageAllProblem">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <input type="submit" class="btn btn-success"
                       value='{{ $t("adminUtils.saveChanges") }}'>
            </div>
        </form>
    </div>
</template>
<script>
    import back from '../utils/back.vue'

    export default {
        data() {
            return {
                adminType: [{name: "user.regularUser", value: 0},
                    {name: "user.admin", "value": 1},
                    {name: "user.superAdmin", value: 2}],
                user: {},
                permission: {
                    manageAllContest: false, createPublicContest: false,
                    manageAllProblem: false, manageOwnProblem: false
                },
                newPassword: "",
                userPermissionNum2Str: {
                    1: "createPublicContest", 2: "manageAllContest",
                    3: "manageAllProblem", 4: "manageOwnProblem"
                },
                userPermissionStr2Num: {
                    createPublicContest: 1, manageAllContest: 2,
                    manageAllProblem: 3, manageOwnProblem: 4
                }
            }
        },
        methods: {
            submit() {
                var data = {
                    id: this.user.id,
                    username: this.user.username,
                    real_name: this.user.real_name,
                    email: this.user.email,
                    admin_type: this.user.admin_type,
                    open_api: this.user.open_api,
                    two_factor_auth: this.user.two_factor_auth,
                    is_disabled: this.user.is_disabled
                };
                if (this.newPassword) {
                    data["password"] = this.newPassword;
                }
                if (this.user.admin_type == this.adminType[1].value) {
                    data["admin_extra_permission"] = [];
                    for (var k in this.permission) {
                        if (this.permission[k]) {
                            data["admin_extra_permission"].push(this.userPermissionStr2Num[k])
                        }
                    }
                }
                this.request({
                    url: "/api/admin/user/",
                    method: "PUT",
                    data: data
                })
            }
        },
        route: {
            data() {
                this.request({
                    url: "/api/admin/user/?user_id=" + this.$route.params["userId"],
                    method: "GET",
                    success: (data)=> {
                        this.user = data.data;
                        for (var p of data.data.admin_extra_permission) {
                            if (this.userPermissionNum2Str[p]) {
                                this.permission[this.userPermissionNum2Str[p]] = true;
                            }
                        }
                    }
                });

                this.$watch('permission.manageAllProblem', function (val) {
                    if (val) {
                        this.permission.manageOwnProblem = false;
                    }
                });
                this.$watch('permission.manageOwnProblem', function (val) {
                    if (val) {
                        this.permission.manageAllProblem = false;
                    }
                });
            }
        },
        components: {
            back
        }
    }
</script>