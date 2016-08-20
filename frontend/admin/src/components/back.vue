<template id="back">
    <nav onclick="history.back()">
        <ul class="pager">
            <li class="previous">
                <span aria-hidden="true">&larr; {{ $t("adminUtils.back") }}</span>
            </li>
        </ul>
    </nav>
</template>