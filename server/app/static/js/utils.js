function regionCitySelector(state, selected_city){
  $.getJSON('/static/data/estados_cidades_min.json', function(data) {
      var options_cities = '';
      $.each(data, function(key, val) {
        if (val.sigla == state) {
          $.each(val.cidades, function(key_city, val_city) {
            options_cities += '<option value="' + val_city + '">' + val_city + '</option>';
          });
          return false; // breaks
        }
      });
      $("#CITY").html(options_cities);
      $("#CITY").val(selected_city);
  });
};

function regionSelector(){
  $.getJSON('/static/data/estados_cidades_min.json', function(data) {
    var items = [];
    var options = '<option value="">Choose ...</option>';
    $.each(data, function(key, val) {
      options += '<option value="' + val.sigla + '">' + val.nome + '</option>';
    });
    $("#STATE").html(options);

    $("#STATE").change(function() {
      var state = "";
      $("#STATE option:selected").each(function() {
        state += $(this).val();
      });
      regionCitySelector(state);
    }).change();

  });
};

function UUID(){
  return Math.random().toString(16).slice(2);
};

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="switch"]').bootstrapSwitch();
  $("#switch-water-tank-in").bootstrapSwitch('state', $('#switch-water-tank-in-val').val()==1);
  $("#switch-water-tank-out").bootstrapSwitch('state', $('#switch-water-tank-out-val').val()==1);
})
