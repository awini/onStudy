(function(){
    var start_socket = function(after_restart) {
        var host = window.location.hostname;
        var url = "ws://"+host+":8888/ws/update/main/";
        console.log("Соединение с " + url);
        var socket = new WebSocket(url);
        start_socket.socket = socket;

        socket.onopen = function() {
            console.log("Соединение установлено.");
            if (after_restart) {
                location.reload();
            }
            start_socket.check("some check text..."); // FIXME only for display how it works...
        };

        socket.onclose = function(event) {
          if (event.wasClean) {
            console.log('Соединение закрыто чисто');
          } else {
            console.log('Обрыв соединения'); // например, "убит" процесс сервера
          }
          console.log('Код: ' + event.code + ' причина: ' + event.reason);
          console.log('Reconnecting in 1 sec...');
          setTimeout(function(){start_socket(true);}, 1000);
        };

        socket.onmessage = function(event) {
            var d = JSON.parse(event.data);
            console.log("Получены данные " + event.data);
        };

        socket.onerror = function(error) {
            console.log("Ошибка " + error.message);
        };
    };

    start_socket.check = function(text) {
        start_socket.socket.send('{"check":"'+text+'"}');
    }

    start_socket();
})();