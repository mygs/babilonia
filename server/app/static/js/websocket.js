function btnStatusChange(btnId, status) {
  if(status != null){
    if(status == 0){
      $(btnId).removeClass('btn-danger');
      $(btnId).addClass('btn-primary');
    }else{
      $(btnId).removeClass('btn-primary');
      $(btnId).addClass('btn-danger');
    }
  }
};

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
    if (data['DATA'] != null) {

      var capacitivemoisture = data['DATA']['CAPACITIVEMOISTURE'];

      if(capacitivemoisture != null){
        var sma = Cookies.get();
        for(var idx = 0 ; idx < 8 ; idx++){
          var field = $('#mux_field_'+idx+'_'+node_id);
          field.removeClass(function (index, css) {
            return (css.match (/\bmoisture-\S+/g) || []).join(' ');
          });
          var level = capacitivemoisture['MUX'+idx];
          if(level <= sma.MUX_PORT_THRESHOLD_OFFLINE){
              field.addClass('moisture-offline');
          } else if(level > sma.MUX_PORT_THRESHOLD_OFFLINE && level <= sma.MUX_PORT_THRESHOLD_WET){
              field.addClass('moisture-wet');
          } else if(level > sma.MUX_PORT_THRESHOLD_WET && level < sma.MUX_PORT_THRESHOLD_NOSOIL){
              field.addClass('moisture-dry');
          } else if(level >= sma.MUX_PORT_THRESHOLD_NOSOIL){
              field.addClass('moisture-nosoil');
          }
          $('#mux_value_'+idx+'_'+node_id).html(level);
        }
      }

      btnStatusChange('#btn-water_' + node_id, data['DATA']['WATER']);

    }

    if(data['COMMAND'] != null){
      btnStatusChange('#btn-water_' + node_id, data['COMMAND']['WATER']);
    }
    console.log(data);
  });



  socket.on('ws-oasis-heartbeat', function(data) {
    var hb = $('#heartbeat_'+data['NODE_ID']);
    hb.replaceWith(hb.clone(true));
  });

});
