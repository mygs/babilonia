function cropModalReset() {
  //$('#nome').val("");
}

function cropModal() {
  cropModalReset();
  $('#cropModal').modal('show');
  regionSelector();
}


function savecrop() {
  swal({
    title: "Are you want to save new Crop?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/save-crop',
        type: 'POST',
        data: $('#cropModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Success", resp.message, "success");
          $("#savecrop").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Failed", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new crop!");
    }
  });
};


$(document).ready(function() {


  $('#crop').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
      text: '<i class="fa fa-plus" aria-hidden="true"></i>',
      titleAttr: 'Adicionar Produção',
      action: function(e, dt, node, config) {
          cropModal()
      }
    }]
  });

  $('#datapicker').datepicker({
    format: "yyyy-mm-dd",
    calendarWeeks: true,
    autoclose: true,
    todayHighlight: true
  });
});
