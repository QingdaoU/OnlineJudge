define("bsAlert", ["jquery", "bootstrap"], function($){
     function bsAlert(content){
         if(!$("#alert-modal").length) {
             var html = '<div class="modal fade" id="alert-modal" tabindex="-1" role="dialog"> ' +
                 '<div class="modal-dialog modal-sm"> <div class="modal-content"> <div class="modal-header"> ' +
                 '<button type="button" class="close" data-dismiss="modal" aria-label="Close">' +
                 '<spanaria-hidden="true">&times;</span></button> <h4 class="modal-title">提示</h4> ' +
                 '</div> <div class="modal-body"> <p id="modal-text"></p> </div> <div class="modal-footer"> ' +
                 '<button type="button" class="btn btn-default" data-dismiss="modal">关闭</button> </div> ' +
                 '</div> </div> </div>';
             $("body").append(html);
         }
         $("#modal-text").html(content);
         $("#alert-modal").modal();
     }
    return bsAlert;
});