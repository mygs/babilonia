/* Websocket connection to update NODE Status */
$(document).ready(function() {

  var socket = io.connect();
  socket.on('ws-oasis-data', function(oasisData) {
    var timestamp = oasisData['TIMESTAMP'];
    var node_id = oasisData['NODE_ID'];
    var data = oasisData['DATA'];
    var node_ip = data['NODE_IP'];
    var firware_version = data['FIRMWARE_VERSION'];

    if (timestamp != null) {
      $('#time_' + node_id).html(moment.unix(timestamp).format('DD/MM/YYYY HH:mm:ss'));
    }
    if (node_ip != null) {
      $('#ip_' + node_id).html(node_ip);
    }
    if (firware_version != null) {
      $('#sw_ver_' + node_id).html(firware_version);
    }
    console.log(data);
  });

  socket.on('ws-oasis-heartbeat', function(data) {
    var hb = $('#heartbeat_'+data['NODE_ID']);
    hb.replaceWith(hb.clone(true));
  });

});
