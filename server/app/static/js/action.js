$(".btn-refresh-all").on("click", function() {
  var status = {
           "NODE_ID": "ALL",
        "MESSAGE_ID": UUID(),
            "STATUS": ["NODE", "SOIL", "DHT", "LIGHT", "FAN", "WATER", "CAPACITIVEMOISTURE"]
        };

  $.ajax({
    url: '/status',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      console.log(response.status);
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});

$(".btn-irrigation-standard").on("click", function() {
  $.ajax({
    url: '/irrigation',
    type: 'GET',
    success: function(response) {
      console.log(response.status);
      //Cookies.set('WATER_ALL', (Cookies.get('WATER_ALL') == "1") ? "0" : "1" )
      Cookies.set('WATER_ALL', '1')
      $(".btn-irrigation-standard").attr("disabled", "disabled");
    },
    error: function(response) {
      swal(response.status, "irrigation", "error");
    }
  });
});

/**
 * @deprecated  btn-irrigation-standard
 */
$(".btn-water-all").on("click", function() {
  if(Cookies.get('WATER_ALL') == null)
    Cookies.set('WATER_ALL', '0')
  var status = {
            "NODE_ID": "ALL",
         "MESSAGE_ID": UUID(),
            "COMMAND": {"WATER": (Cookies.get('WATER_ALL') == "1") ? false : true /* invert! */}
        };

  $.ajax({
    url: '/status',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      console.log(response.status);
      Cookies.set('WATER_ALL', (Cookies.get('WATER_ALL') == "1") ? "0" : "1" )
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});


$("#switch-water-tank-in").on("switchChange.bootstrapSwitch", function() {
  action = $("#switch-water-tank-in").bootstrapSwitch('state');
  $("#switch-water-tank-in-val").val(action? 1:0);
  var message = {
           "DIRECTION": "IN",
          "MESSAGE_ID": UUID(),
              "ACTION": action
    };

  $.ajax({
    url: '/water-tank',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(message),
    success: function(response) {
      console.log(response.status);
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});

$("#switch-water-tank-out").on("switchChange.bootstrapSwitch", function() {
  action = $("#switch-water-tank-out").bootstrapSwitch('state');
  $("#switch-water-tank-out-val").val(action? 1:0);
  var message = {
           "DIRECTION": "OUT",
          "MESSAGE_ID": UUID(),
              "ACTION": action
    };

  $.ajax({
    url: '/water-tank',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(message),
    success: function(response) {
      console.log(response.status);
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});


/* BUTTON STUFF */
function callbackend(command, img, title, text) {
  swal({
    title: title,
    text: text,
    imageUrl: img,
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    closeOnConfirm: true
  }, function(isConfirm) {
    if (!isConfirm) return;
    $.ajax({
      url: '/command',
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify(command),
      success: function(response) {
        console.log(response.status);
        swal(response.status, "It was succesfully!", "success");
      },
      error: function(response) {
        console.log(response.status);
        swal(response.status, "XPTO!", "error");
      }
    });
  });
};

$(".btn-light").on("click", function() {
  var id = $("#NODE_ID").val()
  var light = $('#light_status').val();
  var status = {
           "NODE_ID": id,
        "MESSAGE_ID": UUID(),
           "COMMAND": {"LIGHT": (light == "1") ? false : true /* invert! */}
        };

  $.ajax({
    url: '/command',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      console.log(response.status);
      var newValue = (light == "1" ? "0" : "1");
      $('#light_status').val(newValue);
      if(newValue == "0"){
        $('.btn-light').removeClass('btn-danger');
        $('.btn-light').removeClass('btn-secondary');
        $('.btn-light').addClass('btn-primary');
      }else{
        $('.btn-light').removeClass('btn-primary');
        $('.btn-light').removeClass('btn-secondary');
        $('.btn-light').addClass('btn-danger');
      }

    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });


});

$(".btn-fan").on("click", function() {
  var id = $(this).data('id');
  var param = ($('#fan_' + id).html() == "1") ? False : True; /* invert! */
  var command = {
           "NODE_ID": id,
        "MESSAGE_ID": UUID(),
            "COMMAND": {"FAN": param}
        };
  var img = '/static/img/fan.png';
  var title = "Turn " + (param == True ? "ON" : "OFF") + " the fan for " + id + "?";
  var text = name + " schedule might overwrite your current action";
  //callbackend(id, mode, param, img, title, text)
});


$(".btn-water").on("click", function() {
  var id = $(this).data('id');
  var water = $('#irrigation_' + id).val();
  var status = {
           "NODE_ID": id,
        "MESSAGE_ID": UUID(),
           "COMMAND": {"WATER": (water == "1") ? false : true /* invert! */}
        };

  $.ajax({
    url: '/command',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      console.log(response.status);
      var newValue = (water == "1" ? "0" : "1");
      $('#irrigation_' + id).val(newValue);
      if(newValue == "0"){
        $('#btn-water_' + id).removeClass('btn-danger');
        $('#btn-water_' + id).addClass('btn-primary');
      }else{
        $('#btn-water_' + id).removeClass('btn-primary');
        $('#btn-water_' + id).addClass('btn-danger');
      }

    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});

$(".btn-restart").on("click", function() {
  var id = $("#NODE_ID").val()
  var command = {
           "NODE_ID": id,
        "MESSAGE_ID": UUID(),
            "COMMAND": {"REBOOT": true}
        };
  var img = '/static/img/restart.png';
  var title = "Reboot " + id + "?";
  var text = "This might take a while";
  callbackend(command, img, title, text);
});


$(".btn-refresh").on("click", function() {
  var status = {
           "NODE_ID": $(this).data('id'),
        "MESSAGE_ID": UUID(),
            "STATUS": ["NODE", "SOIL", "DHT", "LIGHT", "FAN", "WATER", "CAPACITIVEMOISTURE"]
        };

  $.ajax({
    url: '/status',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      console.log(response.status);
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
});
