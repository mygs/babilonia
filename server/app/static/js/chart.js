/* check http://www.chartjs.org/docs/latest/ */

$('#chartNodeModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) ;// Button that triggered the modal
  var id = button.data('id');
	var name = button.data('name');
	var modal = $(this);
	modal.find('.modal-title').text('Gráfico de ' + name);

	$.ajax({
		url: '/timeseries',
		type: 'POST',
		data: {"id": id },
		contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
		success: function (response) {
				var resp = JSON.parse(response);

        var temperatureChart = new Chart($('#temperatureChart'), {
            type: 'line',
            data: {
                labels: resp[0].temperature[0].label,
                datasets: [{
                    label: 'Temperatura (Celsius)',
                    data:resp[0].temperature[0].data,
                    fill:false,
                    borderColor:"rgb(255, 0, 0)",
                    lineTension:0.5,
                    borderWidth: 1
                }]
            },
            options: {}
        });
        var humidityChart = new Chart($('#humidityChart'), {
            type: 'line',
            data: {
                labels: resp[0].humidity[0].label,
                datasets: [{
                    label: 'Umidade do ar (%)',
                    data:resp[0].humidity[0].data,
                    fill:false,
                    borderColor:"rgb(0, 0, 255)",
                    lineTension:0.5,
                    borderWidth: 1
                }]
            },
            options: {}
        });
        var moistureChart = new Chart($('#moistureChart'), {
            type: 'line',
            data: {
                labels: resp[0].moisture[0].label,
                datasets: [{
                    label: 'Umidade do solo (%)',
                    data:resp[0].moisture[0].data,
                    fill:false,
                    borderColor:"rgb(0, 255, 0)",
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
