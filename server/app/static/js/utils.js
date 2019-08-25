/* GRID STUFF */
$(function() {
  $("#sortable").sortable();
  $("#sortable").disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');



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
  var mode = 'light';
  var param = ($('#light_' + id).html() == "on") ? 0 : 1; /* invert! */
  var img = '/static/img/light.png';
  var title = "Turn " + (param == 1 ? "ON" : "OFF") + " the light for " + id + "?";
  var text = name + " schedule might overwrite your current action";
  //callbackend(id, mode, param, img, title, text)
});

$(".btn-fan").on("click", function() {
  var id = $(this).data('id');
  var param = ($('#fan_' + id).html() == "1") ? False : True; /* invert! */
  var command = {
           "NODE_ID": id,
        "MESSAGE_ID": "a12dc89b",
            "COMMAND": {"FAN": param}
        };
  var img = '/static/img/fan.png';
  var title = "Turn " + (param == True ? "ON" : "OFF") + " the fan for " + id + "?";
  var text = name + " schedule might overwrite your current action";
  //callbackend(id, mode, param, img, title, text)
});

$(".btn-water").on("click", function() {
  var id = $(this).data('id');
  var param = ($('#irrigation_' + id).html() == "1") ? False : True; /* invert! */
  var command = {
           "NODE_ID": id,
        "MESSAGE_ID": "a12dc89b",
            "COMMAND": {"WATER": param}
        };
  var img = '/static/img/tap.png';
  var title = "Irrigate?";
  var text = "Do not forget to turn it OFF";
  callbackend(command, img, title, text);
});


$(".btn-restart").on("click", function() {
  var id = $(this).data('id')
  var command = {
           "NODE_ID": id,
        "MESSAGE_ID": "a12dc89b",
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
        "MESSAGE_ID": "a12dc89b",
            "STATUS": ["NODE", "SOIL", "DHT", "LIGHT", "FAN", "WATER"]
        };

  $.ajax({
    url: '/status',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(status),
    success: function(response) {
      resp = JSON.parse(response);
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
      //$("#ID").val(id);
      console.log(resp);

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
