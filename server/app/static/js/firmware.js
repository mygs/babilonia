$(document).ready(function() {
  var table = $('#firmware').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
          text: '<i class="fa fa-plus" aria-hidden="true"></i>',
          titleAttr: 'Build Firmware',
          action: function(e, dt, node, config) {
              console.log("build firware");
          }
        }]
  });
}
