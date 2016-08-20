<template>
    <div>
        <top-nav></top-nav>
        <div class="container">
            <div class="row">
                <div>
                    <div class="col-md-2">
                        <left-nav></left-nav>
                    </div>
                    <div class="col-md-10">
                        <router-view></router-view>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer">
            <p class="text-muted text-center">Copyright © 2016</p>
        </div>
    </div>
</template>

<style>

    @import "../../static/css/bootstrap.css";
    @import "../../static/css/todc-bootstrap.css";

    label {
        font-size: 16px;
    }

    .sub-label {
        font-size: 12px;
        display: inline-block;
        max-width: 100%;
        margin-bottom: 5px;
        font-weight: bold;
    }

</style>

<script>
    import topNav from "./views/nav/topNav.vue"
    import leftNav from "./views/nav/leftNav.vue"

    export default({
        components: {
            topNav,
            leftNav
        }
    })
</script>