function btnStatusChange(node_id, status) {
  if(status != null){
    if(status == 0){
      $('#btn-water_' + node_id).removeClass('btn-danger');
      $('#btn-water_' + node_id).addClass('btn-primary');
      $('#box_' + node_id).removeClass('irrigation');

    }else{
      $('#btn-water_' + node_id).removeClass('btn-primary');
      $('#btn-water_' + node_id).addClass('btn-danger');
      $('#box_' + node_id).addClass('irrigation');
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
          var level = capacitivemoisture['MUX'+idx];
          if(level <= sma.MUX_PORT_THRESHOLD_OFFLINE){
              field.css('color', 'rgb(128,128,128)');
          } else if(level > sma.MUX_PORT_THRESHOLD_OFFLINE && level < sma.MUX_PORT_THRESHOLD_NOSOIL){
              var dry_level = Math.round(255 * (level-sma.MUX_PORT_THRESHOLD_OFFLINE)/sma.MUX_PORT_THRESHOLD_SCALE);
              var wet_level = 255 - dry_level;
              field.css('color', 'rgb('+dry_level+',0,'+wet_level+')');
          } else if(level >= sma.MUX_PORT_THRESHOLD_NOSOIL){
              field.css('color', 'rgb(0,0,0)');
          }
          $('#mux_value_'+idx+'_'+node_id).html(level);
        }
      }

      btnStatusChange(node_id, data['DATA']['WATER']);

    }

    if(data['COMMAND'] != null){
      btnStatusChange(node_id, data['COMMAND']['WATER']);
    }
    console.log(data);
  });



  socket.on('ws-oasis-heartbeat', function(data) {
    var hb = $('#heartbeat_'+data['NODE_ID']);
    hb.replaceWith(hb.clone(true));
  });

  socket.on('ws-server-monitor', function(data) {
    if (data['irrigation'] != null && data['irrigation']["status"] != null && data["irrigation"]["status"] == "finished"){
      $(".btn-irrigation-standard").removeAttr('disabled');
      Cookies.set('WATER_ALL', '0');
    }
    console.log(data);
  });

});
