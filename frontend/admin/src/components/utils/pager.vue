<template>
    <nav v-show="visible">
        <ul class="pagination pagination-lg">
            <li class="{{ pagination.currentPage > 1 ? '' : 'disabled' }}">
                <a href="#" aria-label="Previous" @click.prevent="changePage(1)">
                    <span aria-hidden="true">上一页</span>
                </a>
            </li>
            <li class="{{ pagination.currentPage > 1 ? '' : 'disabled' }}">
                <a href="#" aria-label="Previous" @click.prevent="changePage(pagination.currentPage - 1)">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
            <li v-if="pagination.currentPage > 1 && pagination.currentPage - 1 > offset">
                <a href="#" aria-label="Next" @click.prevent="changePage(from)">
                    <span aria-hidden="true">...</span>
                </a>
            </li>
            <li v-for="num in data" :class="{'active': num == pagination.currentPage}">
                <a href="#" @click.prevent="changePage(num)">{{ num }}</a>
            </li>
            <li v-if="pagination.totalPages - pagination.currentPage > offset">
                <a href="#" aria-label="Next" @click.prevent="changePage(to)">
                    <span aria-hidden="true">...</span>
                </a>
            </li>
            <li class="{{ pagination.currentPage < pagination.totalPages ? '' : 'disabled' }}">
                <a href="#" aria-label="Next" @click.prevent="changePage(pagination.currentPage + 1)">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
            <li class="{{ pagination.currentPage < pagination.totalPages ? '' : 'disabled' }}">
                <a href="#" aria-label="Next" @click.prevent="changePage(pagination.totalPages)">
                    <span aria-hidden="true">最后一页</span>
                </a>
            </li>
        </ul>
    </nav>
</template>
<script>
    export default{
        props: {
            pagination: {
                type: Object,
                required: true
            },
            callback: {
                type: Function,
                required: true
            },
            offset: {
                type: Number,
                default: 4
            },
            visible: {
                type: Number,
                default: 1
            }
        },
        computed: {
            data: function () {
                this.visible = 1;
                var from = this.pagination.currentPage - this.offset;
                if (from < 1) {
                    from = 1;
                }
                var to = from + (this.offset * 2);
                if (to >= this.pagination.totalPages) {
                    to = this.pagination.totalPages;
                }
                this.from = from;
                this.to = to;
                var arr = [];
                while (from <= to) {
                    arr.push(from);
                    from++;
                }
                if (arr.length == 1)
                    this.visible = 0;
                return arr;
            }
        },
        methods: {
            changePage(page) {
                this.$set('pagination.currentPage', page);
                this.$router.go({name: this.$route.name, params: {page: page}});
                this.callback();
            }
        }
    };
</script>
