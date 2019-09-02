/* Websocket connection to update NODE Status */
$(document).ready(function() {

  var socket = io.connect();
  socket.on('ws-oasis-data', function(data) {
    console.log(data);
  });

  socket.on('ws-oasis-heartbeat', function(data) {
    console.log(data);
    var hb = $("#heartbeat_"+data["NODE_ID"]);
    hb.replaceWith(hb.clone(true));
  });

});
