import Vue from 'vue'
import App from './App'
import VueRouter from "vue-router"
import VueI18n from "vue-i18n"

import "expose?$!expose?jQuery!jquery"
import "bootstrap"
import bootbox from "bootbox"

import locale from "./locales"
import getCookie from "./utils/cookie"

import userList from "./components/account/userList.vue"
import editUser from "./components/account/editUser.vue"

import announcementList from "./components/announcement/announcementList.vue"
import editAnnouncement from "./components/announcement/editAnnouncement.vue"

import createProblem from "./components/problem/createProblem.vue"
import problemList from "./components/problem/problemList.vue"


// i18n settings
Vue.use(VueI18n);

// todo: strore lang config in localstorage
var lang = "zh-cn";
Vue.config.lang = lang;

Object.keys(locale).forEach(function (lang) {
    Vue.locale(lang, locale[lang])
});

/////////

// custom ajax
Vue.use({
    install: function (Vue, options) {
        Vue.prototype.request = function (option) {
            var request = new XMLHttpRequest();
            request.open(option.method, option.url, true);
            request.onerror = function () {
                if (option.error) {
                    option.error(request)
                }
                else {
                    alert(locale[lang].request.error);
                }
            };
            request.onload = function () {
                if (request.status >= 200 && request.status < 400) {
                    try {
                        var data = JSON.parse(request.responseText);
                        if (data.code == 1 && data.data) {
                            alert(data.data);
                            return;
                        }
                    }
                    catch (err) {
                        request.onerror();
                    }
                    if(option.success) {
                        option.success(data);
                    }
                    else {
                        alert(locale[lang].request.succeeded);
                    }
                }
                else {
                    request.onerror();
                }
            };
            request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            if (option.method.toLowerCase() != 'get') {
                request.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
                request.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                request.send(JSON.stringify(option.data));
            }
            else {
                request.send();
            }
        }
    }
});
///////


Vue.use(VueRouter);
var router = new VueRouter({linkActiveClass: "active"});

router.map({
    "/user/:page": {
        component: userList
    },
    "/user/edit/:userId": {
        component: editUser
    },
    "/problem/create": {
        component: createProblem
    },
    "/problem/:page": {
        component: problemList
    },
    "/announcement/:page": {
        component: announcementList
    },
    "/announcement/edit/:announcementId": {
        component: editAnnouncement
    }
});

// override window.alert
window.alert = function bootboxAlert(content) {
    bootbox.dialog({
        message: content,
        title: locale[lang].alert.alert,
        buttons: {
            main: {
                label: locale[lang].alert.OK,
                className: "btn-primary"
            }
        }
    })
};

// override window.confirm
window.confirm = function bootboxConfirm(content, okCallback, cancelCallback) {
    var config = {
        message: content,
        title: locale[lang].alert.confirm,
        buttons: {
            cancel: {
                label: locale[lang].alert.cancel,
                className: "btn-success"
            },
            main: {
                label: locale[lang].alert.OK,
                className: "btn-warning",
                callback: okCallback
            }
        }
    };
    if (cancelCallback) {
        config.buttons.cancel.callback = cancelCallback;
    }
    bootbox.dialog (config)
};

router.redirect({"/user": "/user/1"});
router.redirect({"/announcement": "/announcement/1"});
router.redirect({"/problem": "problem/1"});

// hide loading
document.getElementById("loading").style.display = "none";
router.start(App, '#app');
