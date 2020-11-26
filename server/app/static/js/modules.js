/* GRID STUFF */
$(function() {
  $("#sortable").sortable();
  $("#sortable").disableSelection();

});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');


$(document).ready(function() {
  $(".ui-sortable-handle").dblclick(function(){
    var node_id = $(this).attr("id");
    window.location = '/module?id=' + node_id;
   });
});

/* MODAL STUFF */
$('#updateNodeModal').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var id = button.data('id'); // Extract info from data-* attributes
  var modal = $(this);
  $('.panel-collapse').removeClass('in');
  $.ajax({
    url: '/configuration',
    type: 'POST',
    data: {
      "id": id
    },
    contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
    success: function(response) {
      var resp = JSON.parse(response);
      $("#NODE_ID").val(id);
      $("#SENSOR_COLLECT_DATA_PERIOD").val(resp.SENSOR_COLLECT_DATA_PERIOD);
      $("#RETRY_WIFI_CONN_DELAY").val(resp.RETRY_WIFI_CONN_DELAY);
      $("#SERIAL_BAUDRATE").val(resp.SERIAL_BAUDRATE);
      $("#OTA_PORT").val(resp.OTA_PORT);
      $("#MODAL_TITLE").text(id);
      for( idx = 0 ; idx <= 8 ; idx++){
        $("#PIN"+idx).val(resp.PIN[idx]);
      }
      idx = "A";
      $("#PIN"+idx).val(resp.PIN[idx]);

      console.log(resp);

    },
    error: function(response) {
      $("#alert").html("ERROR");
      $("#alert").removeClass('alert alert-success alert-danger').addClass("alert alert-danger");
      $(".alert").delay(5000).fadeOut(1000);
    }
  });
});

function updatePinNodeConfiguration() {

  var config = {
            "NODE_ID": $("#NODE_ID").val(),
         "MESSAGE_ID": "man00gui",
             "CONFIG": {
               "PIN":{
                 "A": $("#PINA").val(),
                 "0": $("#PIN0").val(),
                 "1": $("#PIN1").val(),
                 "2": $("#PIN2").val(),
                 "3": $("#PIN3").val(),
                 "4": $("#PIN4").val(),
                 "5": $("#PIN5").val(),
                 "6": $("#PIN6").val(),
                 "7": $("#PIN7").val(),
                 "8": $("#PIN8").val()
               }
             }
        };
  swal({
    title: "Are you sure?",
    text: "Node should be rebooted in order to apply new configuration",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/updatecfg',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(config),
        success: function(response) {
          console.log(response.status);
          swal("Success", response.message, "success");
          $("#saveconfig").attr("disabled", "disabled");
        },
        error: function(response) {
          swal("Failed", response.message, "error");
        }
      });
    } else {
      swal("You not apply nor save new configuration!");
    }
  });
};

function trainOasis(status) {
  var feedback = {
                     "NODE_ID": $("#NODE_ID").val(),
                  "MESSAGE_ID": "a12dc89b",
         "IRRIGATION_FEEDBACK": status
        };

  $.ajax({
    url: '/training',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: JSON.stringify(feedback),
    success: function(response) {
      console.log(response.status);
      $("#updateNodeModal").modal('hide');
    },
    error: function(response) {
      swal(response.status, "XPTO!", "error");
    }
  });
};

function removeOasis() {
  swal({
    title: "Are you sure?",
    text: "Node will be removed and all data will be erased",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    closeOnConfirm: true
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/remove',
        type: 'POST',
        data: $("#NODE_ID").serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          console.log(response.status);
          swal("Success", response.message, "success");
          $("#updateNodeModal").modal('hide');
          location.reload();
        },
        error: function(response) {
          swal("Failed", response.message, "error");
        }
      });
    } else {
      swal("You not removed Oasis!");
    }
  });
};


function resetNodeConfiguration() {

  var reset = {
           "NODE_ID": $("#NODE_ID").val(),
        "MESSAGE_ID": "man00gui",
           "COMMAND": {"RESET": true}
        };
  swal({
    title: "Are you sure?",
    text: "All node configuration will be reseted",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    closeOnConfirm: true
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/reset',
        type: 'POST',
        data: JSON.stringify(reset),
        dataType: 'json',
        contentType: 'application/json',
        success: function(response) {
          console.log(response.status);
          swal("Success", response.message, "success");
          $("#updateNodeModal").modal('hide');
        },
        error: function(response) {
          swal("Failed", response.message, "error");
        }
      });
    } else {
      swal("You not reseted the Node!");
    }
  });
};
