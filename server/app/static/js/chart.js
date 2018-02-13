/* check http://www.chartjs.org/docs/latest/ */

$('#chartNodeModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) ;// Button that triggered the modal
  var id = button.data('id');
	var name = button.data('name');
	var modal = $(this);
	modal.find('.modal-title').text('Charts of ' + name);

	var timeseries = {
		"temperature":{
			"label": ["JAN", "FEV", "MAR", "ABR", "MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"],
			"data": [	{x:1,y:33},{x:2,y:34},{x:3,y:29},{x:4,y:27},{x:5,y:28},{x:6,y:25},
								{x:7,y:22},{x:8,y:21},{x:9,y:21},{x:10,y:23},{x:11,y:25},{x:12,y:29}],
		}
	}

	var myChart = new Chart($('#temperatureChart'), {
	    type: 'line',
	    data: {
	        labels: timeseries["temperature"]["label"],
	        datasets: [{
	            label: 'Temperature',
	            data:timeseries["temperature"]["data"],
							fill:false,
							borderColor:"rgb(75, 192, 192)",
							lineTension:0.5,
	            borderWidth: 1
	        }]
	    },
	    options: {}
	});
	/*
	$.ajax({
		url: '/timseries',
		type: 'POST',
		data: {"id": id },
		contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		success: function (response) {
				var resp = JSON.parse(response);

				$("#ID").val(id);
				$("#NAME").val(resp.NAME);
		},
		error: function (response) {
		}
	});
*/
});
