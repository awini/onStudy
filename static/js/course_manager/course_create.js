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

    function collectData(){
        var courseName = $('#courseName').val();
        var courseMode = $('#courseMode').val();
        var courseDescription = $('#courseDescription').val();

        var courseData = {
            courseName: courseName,
            courseMode: courseMode,
            courseDescription: courseDescription,
        }

        return courseData;
    }

    $("#createCourseForm").submit(function(event) {
        event.preventDefault();
        var sendData = collectData();

        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });

        $.ajax({
              url: "",
              type: "post",
              data: sendData,
              datatype: 'json',
              success: function(data){
                    alert('Курс создан!');
                    window.location.href = '/course/manage?course=' + sendData['courseName'];
              },
              error: function(data){
                  alert(data['responseText']);
              },
        });

    });

});