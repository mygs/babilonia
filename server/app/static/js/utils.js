/* GRID STUFF */
$(function() {
  $("#sortable").sortable();
  $("#sortable").disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');

$('.indoor h4').prepend('<i class="fa fa-sign-in"></i>');
$('.outdoor h4').prepend('<i class="fa fa-sign-out"></i>');
$('.undefinedmode h4').prepend('<i class="fa fa-connectdevelop"></i>');
/* AJAX STUFF */


function callbackend(id, mode, param, img, title, text) {
  swal({
    title: title,
    text: text,
    imageUrl: img,
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (!isConfirm) return;
    $.ajax({
      url: '/command',
      type: 'POST',
      data: {
        "id": id,
        "command": mode,
        "param": param
      },
      contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
      success: function(response) {
        resp = JSON.parse(response);
        swal(resp.status, "It was succesfully!", "success");
      },
      error: function(response) {
        resp = JSON.parse(response);
        swal(resp.status, "XPTO!", "error");
      }
    });
  });
};


$(".btn-light").on("click", function() {
  var id = $(this).data('id');
  var name = $(this).data('name');
  var mode = 'light';
  var param = ($('#light_' + id).html() == "on") ? 0 : 1; /* invert! */
  var img = '/static/img/light.png';
  var title = "Turn " + (param == 1 ? "ON" : "OFF") + " the light for " + name + "?";
  var text = name + " schedule might overwrite your current action";
  callbackend(id, mode, param, img, title, text)
});

$(".btn-fan").on("click", function() {
  var id = $(this).data('id');
  var name = $(this).data('name');
  var mode = 'fan';
  var param = ($('#fan_' + id).html() == "on") ? 0 : 1; /* invert! */
  var img = '/static/img/fan.png';
  var title = "Turn " + (param == 1 ? "ON" : "OFF") + " the fan for " + name + "?";
  var text = name + " schedule might overwrite your current action";
  callbackend(id, mode, param, img, title, text)
});

$(".btn-sop").on("click", function() {
  var id = $(this).data('id');
  var mode = 'sop';
  var img = '/static/img/tap.png';
  var title = "Turn ON Pump/Solenoid for 2 secs?";
  var text = "after action, please wait";
  callbackend(id, mode, 2000000, img, title, text)
});


$(".btn-restart").on("click", function() {
  var id = $(this).data('id');
  var name = $(this).data('name');
  var mode = 'cmd';
  var param = 0; /* reboot */
  var img = '/static/img/restart.png';
  var title = "Are you want to reboot " + name + "?";
  var text = "might take a while";
  callbackend(id, mode, param, img, title, text)
});


$(".btn-refresh").on("click", function() {
  var id = $(this).data('id');
  var name = $(this).data('name');
  $.ajax({
    url: '/command',
    type: 'POST',
    data: {
      "id": id,
      "command": "cmd",
      "param": "1"
    },
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function(response) {
      resp = JSON.parse(response);
      //swal(resp.status, "It was succesfully!", "success");
    },
    error: function(response) {
      resp = JSON.parse(response);
      swal(resp.status, "XPTO!", "error");
    }
  });
});

/* MODAL STUFF */

$('#updateNodeModal').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var id = button.data('id'); // Extract info from data-* attributes
  var mode = button.data('mode'); // Extract info from data-* attributes
  var crud = button.data('crud'); // Extract info from data-* attributes
  var modal = $(this);
  $.ajax({
    url: '/configuration',
    type: 'POST',
    data: {
      "id": id
    },
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function(response) {
      var resp = JSON.parse(response);
      if (crud == "edit"){
        modal.find('.modal-title').text('Configuration for ' + resp.NAME + ' - '+mode);
      } else if(crud == "new"){
        modal.find('.modal-title').text('New Configuration for ' + id + ' - '+mode);
      }
      $("#ID").val(id);
      $("#NAME").val(resp.NAME);
      $("#SLEEP_TIME_SPRINKLE").val(resp.SLEEP_TIME_SPRINKLE);
      $("#TEMPERATURE_THRESHOLD").val(resp.TEMPERATURE_THRESHOLD);
      $("#MASK_CRON_CTRL").val(resp.MASK_CRON_CTRL);
      $("#MASK_CRON_LIGHT_ON").val(resp.MASK_CRON_LIGHT_ON);
      $("#MASK_CRON_LIGHT_OFF").val(resp.MASK_CRON_LIGHT_OFF);

      if(mode == "outdoor"){
        $("#SLEEP_TIME_SPRINKLE").attr('readonly', false);
        $("#TEMPERATURE_THRESHOLD").attr('readonly', true);
        $("#MASK_CRON_LIGHT_ON").attr('readonly', true);
        $("#MASK_CRON_LIGHT_OFF").attr('readonly', true);
      } else if(mode == "indoor"){
        $("#SLEEP_TIME_SPRINKLE").attr('readonly', true);
        $("#TEMPERATURE_THRESHOLD").attr('readonly', false);
        $("#MASK_CRON_LIGHT_ON").attr('readonly', false);
        $("#MASK_CRON_LIGHT_OFF").attr('readonly', false);
      }
    },
    error: function(response) {
      $("#alert").html("ERROR");
      $("#alert").removeClass('alert alert-success alert-danger').addClass("alert alert-danger");
      $(".alert").delay(5000).fadeOut(1000);
    }
  });
});

function updatecfg() {
  swal({
    title: "Are you sure?",
    text: "Node will be reboot in order to apply new configuration",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/updatecfg',
        type: 'POST',
        data: $('#updateNodeModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Success", resp.message, "success");
          $("#saveconfig").attr("disabled", "disabled");
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Failed", resp.message, "error");
        }
      });
    } else {
      swal("You not apply nor save new configuration!");
    }
  });
};

function regionCitySelector(state, selectedCity){
  $.getJSON('/static/data/estados_cidades.json', function(data) {
      var options_cidades = '';
      $.each(data, function(key, val) {
        if (val.sigla == state) {
          $.each(val.cidades, function(key_city, val_city) {
            options_cidades += '<option value="' + val_city + '">' + val_city + '</option>';
          });
        }
      });
      $("#cidade").html(options_cidades);
      $("#cidade").val(selectedCity);
  });
};






function regionSelector(){
  $.getJSON('/static/data/estados_cidades.json', function(data) {
    var items = [];
    var options = '<option value="">Escolha ...</option>';
    $.each(data, function(key, val) {
      options += '<option value="' + val.sigla + '">' + val.nome + '</option>';
    });
    $("#estado").html(options);

    $("#estado").change(function() {

      var options_cidades = '';
      var state = "";

      $("#estado option:selected").each(function() {
        state += $(this).val();
      });

        regionCitySelector(state);

    }).change();

  });
};

function supplierModal() {
  $('#plantSupplierModal').modal('show')
  regionSelector();
}


function savesupplier() {
  swal({
    title: "Você deseja salvar um novo fornecedor?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/save-plant-supplier',
        type: 'POST',
        data: $('#plantSupplierModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Sucesso", resp.message, "success");
          $("#savesupplier").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Falhou", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new supplier!");
    }
  });
};

function plantModal() {
  $('#plantModal').modal('show');
}


function saveplant() {
  swal({
    title: "Are you want to save new Plant?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/save-plant',
        type: 'POST',
        data: $('#plantModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Success", resp.message, "success");
          $("#saveplant").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Failed", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new plant!");
    }
  });
};


/* Websocket connection to update NODE Status */
$(document).ready(function() {

  var socket = io.connect();
  socket.on('mqtt_message', function(data) {
    console.log(data);
    var id = data.id;
    if (data.timestamp != null) {
      $('#time_' + id).html(moment.unix(data.timestamp).format('DD/MM/YYYY HH:mm:ss'));


      $( '#status_' + id ).removeClass( "excellent good nostatus danger" );
      NOW = Math.floor((new Date).getTime() / 1000);
      DELTA = NOW - data.timestamp;
      if(DELTA < 60){
          $( '#status_' + id ).addClass( "excellent" );
      }else if(DELTA < 60*3){
          $( '#status_' + id ).addClass( "good" );
      }else if(DELTA < 60*15){
        $( '#status_' + id ).addClass( "nostatus" );
      }else{
        $( '#status_' + id ).addClass( "danger" );
      }
    }
    if (data.mt != null) {
      $('#temp_' + id).html(data.mt + String.fromCharCode(176) + 'C');
    }
    if (data.mma != null) {
      if($('#mma_' + id).hasClass('indoor')){
        $('#mma_' + id).html('N/A');
      } else {
        $('#mma_' + id).html((data.mma == 1) ? 'DRY' : 'WET');
      }
    }
    if (data.mmb != null) {
      if($('#mmb_' + id).hasClass('indoor')){
        $('#mmb_' + id).html('N/A');
      } else {
        $('#mmb_' + id).html((data.mmb == 1) ? 'DRY' : 'WET');
      }
    }
    if (data.mmc != null) {
      if($('#mmc_' + id).hasClass('indoor')){
        $('#mmc_' + id).html('N/A');
      } else {
        $('#mmc_' + id).html((data.mmc == 1) ? 'DRY' : 'WET');
      }
    }
    if (data.mh != null) {
      $('#humid_' + id).html(data.mh + '%');
    }
    if (data.sf != null) {
      if($('#fan_' + id).hasClass('outdoor')){
        $('#fan_' + id).html('N/A');
      } else {
        $('#fan_' + id).html((data.sf == 1) ? 'on' : 'off');
      }
    }
    if (data.sl != null) {
      if($('#light_' + id).hasClass('outdoor')){
        $('#light_' + id).html('N/A');
      } else {
        $('#light_' + id).html((data.sl == 1) ? 'on' : 'off');
      }
    }

  });

  socket.on('alert', function(data) {
    console.log(data);

  });
  // get current URL path and assign 'active' class
  var pathname = window.location.pathname;
  var suffix = pathname.substring(0, pathname.indexOf("/", pathname.indexOf("/") + 1))
  if (suffix == "") {
    suffix = pathname;
  }
  $('.navbar-nav > li > a[href="' + suffix + '"]').parent().addClass('active');
  $('.nav-sidebar > li > a[href="' + pathname + '"]').parent().addClass('active');


  // START grids
  $('#plant').DataTable({
		"bLengthChange": false,
		"info": false,
		"bPaginate": false, //hide pagination control
		"dom": 'Bfrtip',
		"buttons": [{
			text: '<i class="fa fa-plus" aria-hidden="true"></i>',
			titleAttr: 'Adicionar Vegetal',
			action: function(e, dt, node, config) {
					plantModal()
			}
		}]
	});

  $('#supplier').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
      text: '<i class="fa fa-plus" aria-hidden="true"></i>',
      titleAttr: 'Adicionar Fornecedor',
      action: function(e, dt, node, config) {
          supplierModal()
      }
    }]
  });
  // END grids
});
