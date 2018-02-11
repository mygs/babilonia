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
function light(id, command){
	command = 1 - status; /* invert status */
	$.ajax({
    url: '/light',
    type: 'POST',
    data: {
						"id": id ,
						"command" : command
					},
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function (response) {
				resp = JSON.parse(response);
				$("#alert").html(resp.status);
				$("#alert").addClass("alert alert-success");
			 	$(".alert").delay(5000).fadeOut(1000);
    },
    error: function () {
        $("#alert").html("ERROR");
				$("#alert").addClass("alert alert-danger");
			 	$(".alert").delay(5000).fadeOut(1000);
    }
});
}

function command(id, code){
	command = 1 - status; /* invert status */
	$.ajax({
    url: '/command',
    type: 'POST',
    data: {
						"id": id ,
						"code" : code
					},
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function (response) {
				resp = JSON.parse(response);
				$("#alert").html(resp.status);
				$("#alert").addClass("alert alert-success");
			 	$(".alert").delay(5000).fadeOut(1000);
    },
    error: function () {
        $("#alert").html("ERROR");
				$("#alert").addClass("alert alert-danger");
			 	$(".alert").delay(5000).fadeOut(1000);
    }
});
}
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
		error: function () {
				$("#alert").html("ERROR");
				$("#alert").addClass("alert alert-danger");
				$(".alert").delay(5000).fadeOut(1000);
		}
	});
})

function updatecfg(){
	$.ajax({
    url: '/updatecfg',
    type: 'POST',
    data: $('#updateNodeModalForm').serialize(),
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function (response) {
				resp = JSON.parse(response);
				$("#alert").html(resp.status);
				$("#alert").addClass("alert alert-success");
			 	$(".alert").delay(5000).fadeOut(1000);
    },
    error: function () {
        $("#alert").html("ERROR");
				$("#alert").addClass("alert alert-danger");
			 	$(".alert").delay(5000).fadeOut(1000);
    }
});
}
