/* GRID STUFF */
$(function() {
	$( "#sortable" ).sortable();
	$( "#sortable" ).disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');
$('.nostatus h4').prepend('<i class="fa fa-circle-o"></i>');
$('.danger h4').prepend('<i class="fa fa-exclamation-circle"></i>');
$('.good h4').prepend('<i class="fa fa-check"></i>');
$('.excellent h4').prepend('<i class="fa fa-star"></i>');
/* AJAX STUFF */


function callbackend(id, name, mode){
	status = ($('#'+mode+'_'+id).html() == "ON") ? 1 : 0;
	parm = 1 - status;/* invert status */
	swal({
			title: "Turn "+(parm == 1 ? "ON": "OFF")+" the "+mode+" for "+name+"?",
			text: name+" schedule might overwrite your current action",
			imageUrl: '/static/img/'+mode+'.png',
			showCancelButton: true,
			confirmButtonColor: "#DD6B55",
			confirmButtonText: "Confirm",
			closeOnConfirm: false
	}, function (isConfirm) {
			if (!isConfirm) return;
			$.ajax({
		    url: '/command',
		    type: 'POST',
		    data: {"id": id, "command": mode, "parm":parm},
		    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		    success: function (response) {
					resp = JSON.parse(response);
					swal(resp.status, "It was succesfully!", "success");
		    },
		    error: function (response) {
					resp = JSON.parse(response);
					swal(resp.status, "XPTO!", "error");
		    }
			});
	});
};


$(".btn-light").on("click", function() {
	var id = $(this).data('id'); // Extract info from data-* attributes
	var name = $(this).data('name'); // Extract info from data-* attributes
	callbackend(id, name, 'light')});

$(".btn-fan").on("click", function() {
	var id = $(this).data('id'); // Extract info from data-* attributes
	var name = $(this).data('name'); // Extract info from data-* attributes
	callbackend(id, name, 'fan')});


$(".btn-cmd").on("click", function() {
	var id = $(this).data('id'); // Extract info from data-* attributes
	var name = $(this).data('name'); // Extract info from data-* attributes
	$.ajax({
		url: '/command',
		type: 'POST',
		data: {"id": id, "command": "cmd", "parm":"1"},
		contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		success: function (response) {
			resp = JSON.parse(response);
			swal(resp.status, "It was succesfully!", "success");
		},
		error: function (response) {
			resp = JSON.parse(response);
			swal(resp.status, "XPTO!", "error");
		}
	});
});

/* MODAL STUFF */

$('#updateNodeModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) ;// Button that triggered the modal
  var id = button.data('id'); // Extract info from data-* attributes
	var modal = $(this);
	$.ajax({
		url: '/configuration',
		type: 'POST',
		data: {"id": id },
		contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		success: function (response) {
				var resp = JSON.parse(response);

				modal.find('.modal-title').text('Configuration for ' + resp.NAME);
				$("#ID").val(id);
				$("#NAME").val(resp.NAME);
				$("#TEMPERATURE_THRESHOLD").val(resp.TEMPERATURE_THRESHOLD);
				$("#MOISTURE_THRESHOLD").val(resp.MOISTURE_THRESHOLD);
				$("#MASK_CRON_CTRL").val(resp.MASK_CRON_CTRL);
				$("#MASK_CRON_LIGHT_ON").val(resp.MASK_CRON_LIGHT_ON);
				$("#MASK_CRON_LIGHT_OFF").val(resp.MASK_CRON_LIGHT_OFF);
		},
		error: function (response) {
				$("#alert").html("ERROR");
				$("#alert").removeClass('alert alert-success alert-danger').addClass("alert alert-danger");
				$(".alert").delay(5000).fadeOut(1000);
		}
	});
});

function updatecfg(){
	$.ajax({
    url: '/updatecfg',
    type: 'POST',
    data: $('#updateNodeModalForm').serialize(),
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function (response) {
				var resp = JSON.parse(response);
				$("#alertModal").html(resp.message);
				$("#alertModal").removeClass('alert alert-success alert-danger').addClass("alert alert-success");
			 	$(".alertModal").delay(2000).fadeOut(1000);
    },
    error: function (response) {
				$("#alertModal").html(resp.message);
				$("#alertModal").removeClass('alert alert-success alert-danger').addClass("alert alert-danger");
			 	$(".alertModal").delay(2000).fadeOut(1000);
    }
});
};


/* Websocket connection to update NODE Status */
$(document).ready(function(){
	var socket = io.connect('http://localhost:5000');
    socket.on('mqtt_message', function(data) {
			console.log(data);
			var id = data.id;
			$('#time_'+id).html(moment.unix(data.timestamp).format('DD-MM-YY HH:mm'));
			$('#temp_'+id).html(data.mt);
			$('#moist_'+id).html(data.mm);
			$('#humid_'+id).html(data.mh);
			$('#fan_'+id).html((data.sf == 1) ? "ON": "OFF");
			$('#light_'+id).html((data.sl == 1) ? "ON": "OFF");

    });
});
