$(document).ready(function() {

  $('#firmware').on('init.dt', function() {
   $('.firware-build-btn')
     .attr('data-toggle', 'collapse')
     .attr('data-target', '#updating-node');
   });

  var table = $('#firmware').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
          text: '<i class="fa fa-microchip" aria-hidden="true"></i>',
          className: 'firware-build-btn',
          titleAttr: 'Build Firmware',
          action: function(e, dt, node, config) {
              console.log("build firware");
          }
        }]

  });
});
