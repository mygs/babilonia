function buildFirmwareProgress() {
  var source = new EventSource("/progress");
	source.onmessage = function(event) {
		$('.progress-bar').css('width', event.data+'%').attr('aria-valuenow', event.data);
		$('.progress-bar-label').text(event.data+'%');
		if(event.data == 100){
			source.close()
		}
	}
};

function firmwareAction(action, node_id, node_ip) {
  var message = {
           "NODE_ID": node_id,
           "ACTION": action
        };
  if(action == "upgrade" && node_ip != null){
    message["NODE_IP"] = node_ip;
  }
  $.ajax({
    url: '/firmware',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(message),
    success: function(response) {
      console.log(response.status);
      swal(response.status, response.message, response.status);

    },
    error: function(response) {
      swal(response.status, "XPTO!", response.status);
    }
  });
};

$(".btn-backup").on("click", function() {
  firmwareAction("backup",$(this).data('id'));
});

$(".btn-upgrade").on("click", function() {
  firmwareAction("upgrade",$(this).data('id'),$(this).data('ip'));
});

$(".btn-restore").on("click", function() {
  firmwareAction("restore",$(this).data('id'));
});

$(document).ready(function() {

  $('#firmware').on('init.dt', function() {
   $('.firware-build-btn')
     .attr('data-toggle', 'collapse')
     .attr('data-target', '#updating-node');
   });

  var table = $('#firmware').DataTable({
    "bLengthChange": false,
    "searching": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
          text: '<i class="fa fa-microchip" aria-hidden="true"></i>',
          className: 'firware-build-btn',
          titleAttr: 'Build Firmware',
          action: function(e, dt, node, config) {
              console.log("build firmware");
              buildFirmwareProgress();
          }
        }]

  });

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  });
});
