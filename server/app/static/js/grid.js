$(function() {
	$( "#sortable" ).sortable();
	$( "#sortable" ).disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');
$('.nostatus h4').prepend('<i class="fa fa-circle-o"></i>');
$('.danger h4').prepend('<i class="fa fa-exclamation-circle"></i>');
$('.good h4').prepend('<i class="fa fa-check"></i>');
$('.excellent h4').prepend('<i class="fa fa-star"></i>');
