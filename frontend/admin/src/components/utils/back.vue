<template id="back">
    <nav>
        <ul class="pager">
            <li class="previous">
                <a href="#" v-link="url">
                    <span aria-hidden="true">&larr;</span>
                    {{ $t("adminUtils.back") }}
                </a>
            </li>
        </ul>
    </nav>
</template>
<script>
    export default{
        props: ["url"]
    }
</script>