define("csrf",function(){
    function get_cookie(cookie_name) {
        var name = cookie_name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1);
            if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
        }
        return "";
    }
    function csrfHeader(xhr){
         xhr.setRequestHeader("X-CSRFToken", get_cookie("csrftoken"));
    }
    return csrfHeader;
});
