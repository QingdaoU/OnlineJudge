<template>
    <div id="browser-unsupported" style="display: none">{{{ $t("adminUtils.unsupportedBrowserWarningMsg") }}}
    </div>
</template>
<script>
    export default{
        attached() {
            if (navigator.userAgent.indexOf("MSIE") > -1) {
                document.getElementById("browser-unsupported").removeAttribute("style");
            }
        }
    }
</script>