define("bs_alert", ["jquery", "bootstrap"], function($){
     function bs_alert(content){
         $("#modal-text").html(content);
         $("#modal").modal();
     }
    return bs_alert;
});