$(document).ready(function(){
    'use strict';

    var LESSON_USER = "";

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


    $(".rightView").on("click", function() {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });

        LESSON_USER = $(this).attr("value")
        var sendData = {
            user: LESSON_USER,
            course: $("#courseRights").attr("course"),
        };

        $.ajax({
            url: "",
            type: "post",
                data: {user: $(this).attr("value"), action: "showLessons"},
                datatype: 'json',
                success: function(data){
                    drawTable(JSON.parse(data));
                    $("#lessonRights").modal('show');;
                },
                error: function(data){
                    alert('unknown error!');
                },
        });
    });

    function drawTable(data){
        $("#lessonRightsTbody").empty();
        for (var lessonName in data) {
           if (data.hasOwnProperty(lessonName)) {
                var td_lessonName = $("<td></td>").text(lessonName);
                var td_cur_right = $("<td></td>").text(data[lessonName]);
                var td_new_right = $("<td></td>");
                td_new_right.append(createSelect(data[lessonName], lessonName));
                var tr = $("<tr></tr>");
                tr.append(td_lessonName, td_cur_right, td_new_right);
                $("#lessonRightsTbody").append(tr);
           }
        }
    }

    function createSelect(default_right, lessonName){
        var newSelect = $("#selectLesRights").clone(true);
        newSelect.removeAttr("id");
        newSelect.attr("hidden", false);
        newSelect.attr("lessonName", lessonName)
        newSelect.attr("class", "selectedLesRight")
        newSelect.children().each(function () {
            if (this.value == default_right) {
                $(this).attr("selected",true);
            }
        });
        return newSelect
    }

    $("#applyLessonBtn").on("click", function() {
        var newRight = {};

        $( ".selectedLesRight" ).each(function() {
            newRight[$(this).attr("lessonName")] = $(this).val();
        });

        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });

        var sendData = {
            "newRight" : JSON.stringify(newRight),
            action: "modifyLesson",
            course: $("#courseRights").attr("course"),
            user: LESSON_USER,
        };

        $.ajax({
            url: "",
            type: "post",
                data: sendData,
                datatype: 'json',
                success: function(data){
                    drawTable(JSON.parse(data));
                },
                error: function(data){
                    alert('unknown error!');
                },
        });
    });

    $("#applyCourseBtn").on("click", function() {
        var newRight = {};

        $( ".selectedCourseRights" ).each(function() {
            newRight[$(this).attr("user")] = $(this).val();
        });

        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("_xsrf") }
        });

        var sendData = {
            "newRight" : JSON.stringify(newRight),
            action: "modifyCourse",
            course: $("#courseRights").attr("course"),
        };

        $.ajax({
            url: "",
            type: "post",
                data: sendData,
                datatype: 'json',
                success: function(data){
                    window.location.reload();
                },
                error: function(data){
                    alert('unknown error!');
                },
        });
    });
}());