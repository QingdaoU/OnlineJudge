<template lang="html">
    <div class="input tags-wrap">
        <div class="tags" transition="tags" v-for="tag in tagList" track-by="$index">
            <span class="content">{{ tag }}</span><span class="del" @click="delTag($index, false)">&times;</span>
        </div>
        <input class="form-control tags-input" list="tagAutoCompleteList" type="text" placeholder="{{ $t('tag.hint') }}"
               v-model="text"
               @keyup.enter="addTag(text)" @keydown.delete="delTag(tagList.length - 1, true)">
        <datalist id="tagAutoCompleteList">
            <template v-for="item in tagAutoCompleteList">
                <option value="{{ item }}"></option>
            </template>
        </datalist>
    </div>
</template>

<script>
    export default {
        props: {
            tagList: {
                type: Array,
                default: ()=>{
                    return []
                }
            },
            tagAutoCompleteList: {
                type: Array,
                default: ()=>{
                    return []
                }
            }
        },
        data () {
            return {
                text: '',
            }
        },
        methods: {
            addTag (text) {
                if (text.trim() != '') {
                    var count = this.tagList.length;
                    this.tagList.$set(count, text);
                    this.text = ''
                }
            },
            delTag (index, way) {
                if (way) {
                    if (index >= 0 && this.text == '') {
                        this.tagList.splice(index, 1)
                    }
                } else {
                    this.tagList.splice(index, 1)
                }
            }
        }
    }
</script>

<style>
    .tags-wrap {
        width: 100% !important;
        height: 100% !important;
        outline: none;
    }

    .tags-wrap::after {
        content: "";
        display: block;
        height: 0;
        clear: both;
    }

    .tags {
        background-color: #4787ed;
    }

    .tags, .tags-input {
        position: relative;
        float: left;
        color: #fff;
        line-height: 28px;
        margin: 0 4px 4px 0;
        padding: 0 22px 0 10px;
    }

    .tags .content, .tags-input .content {
        line-height: 28px;
    }

    .tags .del, .tags-input .del {
        width: 22px;
        height: 28px;
        text-align: center;
        cursor: pointer;
        position: absolute;
        top: -1px;
        right: 0;
    }

    .tags-input {
        color: inherit;
        width: 15em;
    }

    .tags-enter, .tags-leave {
        transform: scale(0.9);
        opacity: 0;
    }

    .tags-transition {
        transition: all .3s ease;
    }
</style>