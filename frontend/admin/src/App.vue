<template>
    <div>
        <unsupported-browser-warning></unsupported-browser-warning>
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
                    <alert></alert>
                </div>
            </div>
        </div>
        <div class="footer">
            <p class="text-muted text-center">Copyright © 2016</p>
        </div>
    </div>
</template>

<style>
    @import "../../static/css/loading.css";
    @import "../../static/css/bootstrap.css";
    @import "../../static/css/todc-bootstrap.css";

</style>

<script>
    import unsupportedBrowserWarning from "./components/utils/unsupportedBrowserWarning.vue"
    import topNav from "./components/utils/topNav.vue"
    import leftNav from "./components/utils/leftNav.vue"
    import alert from "./components/utils/alert.vue"


    export default({
        components: {
            unsupportedBrowserWarning,
            topNav,
            leftNav,
            alert
        }
    })
</script>