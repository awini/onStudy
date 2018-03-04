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

    function sendAjax(sendData){
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });
        $.ajax({
              url: "lesson",
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
    }

    $("#addLesson").click(function(event) {
        event.preventDefault();
        $('#addLessonModal').modal('show');
    });

    $(".removeBtn").click(function(event) {
        event.preventDefault();
        if (!confirm("Are you sure?")){
            return
        }
        var sendData = {
            action: "remove",
            courseName: $("#addLessonCursename").val(),
            lessonName: $(this).val(),
        };
        sendAjax(sendData);
    });

    $("#addLessonForm").submit(function(event) {
        event.preventDefault();
        var formData = {
            action: "add",
            lessonName: $("#addLessonName").val(),
            lessonDescription: $("#addLessonDescription").val(),
            lessonStartTime: $("#addLessonStartTime").val(),
            lessonDuration: $("#addLessonDuration").val(),
            courseName: $("#addLessonCursename").val(),
        };
        sendAjax(formData);
    });
});