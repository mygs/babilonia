/* GRID STUFF */
$(function() {
  $("#sortable").sortable();
  $("#sortable").disableSelection();
});
$('#sortable li').addClass('ui-state-default col-md-3 col-sm-4 col-xs-12');


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
      $("#ID_TRAINING_BTN").val(id);
      $("#ID_PARAMS_FORM").val(id);
      $("#ID_PIN_FORM").val(id);
      $("#SENSOR_COLLECT_DATA_PERIOD").val(resp.SENSOR_COLLECT_DATA_PERIOD);
      $("#RETRY_WIFI_CONN_DELAY").val(resp.RETRY_WIFI_CONN_DELAY);
      $("#SERIAL_BAUDRATE").val(resp.SERIAL_BAUDRATE);
      $("#OTA_PORT").val(resp.OTA_PORT);
      $("#MODAL_TITLE").text(id);
      for( idx = 0 ; idx < 9 ; idx++){
        $("#PIN"+idx).val(resp.PIN[idx]);
      }
      console.log(resp);

    },
    error: function(response) {
      $("#alert").html("ERROR");
      $("#alert").removeClass('alert alert-success alert-danger').addClass("alert alert-danger");
      $(".alert").delay(5000).fadeOut(1000);
    }
  });
});

function updateNodeConfiguration() {
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
                     "NODE_ID": $("#ID_TRAINING_BTN")[0].value,
                  "MESSAGE_ID": "a12dc89b",
         "IRRIGATION_FEEDBACK": status
        };

  $.ajax({
    url: '/feedback',
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
