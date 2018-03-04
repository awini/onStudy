$(document).ready(function(){
    'use strict';

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

    $("#courseAction").click(function(event) {
        event.preventDefault();
        if (!confirm("Are you sure?")){
            return
        }
        var sendData = {
            courseName: $("#addLessonCursename").val(),
            action: $(this).val(),
        }

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
              error: function(data){
                  alert(data['responseText']);
              },
        });
    });

    $("#inviteAction").click(function(event) {
        event.preventDefault();
        var userToInvite = prompt("Please enter user name to invite");
        var sendData = {
            courseName: $("#addLessonCursename").val(),
            userToInvite: userToInvite,
            action: $(this).val(),
        }

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
              },
              error: function(data){
                  alert(data['responseText']);
              },
        });
    });

});