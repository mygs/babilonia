/* GRID STUFF */
$(function() {
  $("#sortable").sortable();
  $("#sortable").disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');
$('.nostatus h4').prepend('<i class="fa fa-circle-o"></i>');
$('.danger h4').prepend('<i class="fa fa-exclamation-circle"></i>');
$('.good h4').prepend('<i class="fa fa-check"></i>');
$('.excellent h4').prepend('<i class="fa fa-star"></i>');
/* AJAX STUFF */


function callbackend(id, mode, param, img, title, text) {
  swal({
    title: title,
    text: text,
    imageUrl: img,
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
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

      modal.find('.modal-title').text('Configuration for ' + resp.NAME);
      $("#ID").val(id);
      $("#NAME").val(resp.NAME);
      $("#TEMPERATURE_THRESHOLD").val(resp.TEMPERATURE_THRESHOLD);
      $("#MOISTURE_THRESHOLD").val(resp.MOISTURE_THRESHOLD);
      $("#MASK_CRON_CTRL").val(resp.MASK_CRON_CTRL);
      $("#MASK_CRON_LIGHT_ON").val(resp.MASK_CRON_LIGHT_ON);
      $("#MASK_CRON_LIGHT_OFF").val(resp.MASK_CRON_LIGHT_OFF);
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
    confirmButtonText: "Confirm",
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
      var str = "";

      $("#estado option:selected").each(function() {
        str += $(this).text();
      });

      $.each(data, function(key, val) {
        if (val.nome == str) {
          $.each(val.cidades, function(key_city, val_city) {
            options_cidades += '<option value="' + val_city + '">' + val_city + '</option>';
          });
        }
      });
      $("#cidade").html(options_cidades);

    }).change();

  });
}

function supplierModal() {
  $('#plantSupplierModal').modal('show')
  regionSelector();
}


function savesupplier() {
  swal({
    title: "Are you want to save new Supplier?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
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
          swal("Success", resp.message, "success");
          $("#savesupplier").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Failed", resp.message, "error");
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
    confirmButtonText: "Confirm",
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

  var socket = io.connect('http://192.168.1.60:8080');
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
    if (data.mm != null) {
      $('#moist_' + id).html(data.mm + '%');
    }
    if (data.mh != null) {
      $('#humid_' + id).html(data.mh + '%');
    }
    if (data.sf != null) {
      $('#fan_' + id).html((data.sf == 1) ? 'on' : 'off');
    }
    if (data.sl != null) {
      $('#light_' + id).html((data.sl == 1) ? 'on' : 'off');
    }

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
