$(document).ready(function(){
    'use strict';

    $(".addStudyOpenBtn").click(function(event) {
        event.preventDefault();
        if (!confirm("Are you sure?")){
            return
        }
        var sendData = {
            courseName: $(this).val(),
            courseType: 'Open',
        };
        sendAjax(sendData);
    });

    $(".addStudyCloseBtn").click(function(event) {
        event.preventDefault();
        if (!confirm("Are you sure?")){
            return
        }
        var sendData = {
            courseName: $(this).val(),
            courseType: 'Close',
        };
        sendAjax(sendData);
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sendAjax(sendData){
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });
        $.ajax({
              url: "",
              type: "post",
              data: sendData,
              datatype: 'json',
              success: function(data){
                    alert('Success!');
                    window.location.reload();
              },
              error: function(){
                  alert('Ошибка! Какая-нибудь...');
              },
        });
    }

});