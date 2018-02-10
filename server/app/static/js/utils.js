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
function light(id, status){
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
        alert(resp.status);
    },
    error: function () {
        alert("error");
    }
});
}
