function regionCitySelector(state, selected_city){
  $.getJSON('/static/data/estados_cidades.json', function(data) {
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
  $.getJSON('/static/data/estados_cidades.json', function(data) {
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
