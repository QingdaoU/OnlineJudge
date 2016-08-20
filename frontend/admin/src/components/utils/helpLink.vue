<template>
    <a href="{{ link }}" target="_blank"><span class="glyphicon glyphicon-link"></span></a>
</template>

<script>
    export default ({
        props: {
            link: {
                type: String,
                required: true
            }
        }
    })
</script>