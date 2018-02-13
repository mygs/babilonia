/* check http://www.chartjs.org/docs/latest/ */

$('#chartNodeModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) ;// Button that triggered the modal
  var id = button.data('id');
	var name = button.data('name');
	var modal = $(this);
	modal.find('.modal-title').text('Charts of ' + name);

	/*var timeseries = {
		"temperature":{
			"label": ["JAN", "FEV", "MAR", "ABR", "MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"],
			"data": [	{x:"JAN",y:33},{x:"FEV",y:34},{x:"MAR",y:29},{x:"ABR",y:27},{x:"MAI",y:28},{x:"JUN",y:25},
								{x:"JUL",y:22},{x:"AGO",y:21},{x:"SET",y:21},{x:"OUT",y:23},{x:"NOV",y:25},{x:"DEZ",y:29}],
		}
	}
*/

	$.ajax({
		url: '/timeseries',
		type: 'POST',
		data: {"id": id },
		contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		success: function (response) {
				var resp = JSON.parse(response);

        var myChart = new Chart($('#temperatureChart'), {
            type: 'line',
            data: {
                labels: resp[0].temperature[0].label,
                datasets: [{
                    label: 'Temperature',
                    data:resp[0].temperature[0].data,
                    fill:false,
                    borderColor:"rgb(75, 192, 192)",
                    lineTension:0.5,
                    borderWidth: 1
                }]
            },
            options: {}
        });
		},
		error: function (response) {
		}
	});

});
