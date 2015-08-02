function _notify(notify_type, title, content){
    $.notify({
        title: title,
        message: content
    }, {
        type: notify_type,
        placement: {
            from: "top",
            align: "center"
        },
        offset: {
            y: 50
        },
        delay: 3000,
        timer: 1000
    });
}
function show_info(title, content) {
    _notify("info", title, content);
}

function show_warning(title, content) {
    _notify("warning", title, content);
}