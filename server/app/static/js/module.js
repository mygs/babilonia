function moduleModal() {
  $('#moduleModal').modal('show');
}


function savemodule() {
  swal({
    title: "Are you want to save new Module?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/save-module',
        type: 'POST',
        data: $('#moduleModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Success", resp.message, "success");
          $("#savemodule").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Failed", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new module!");
    }
  });
};


$(document).ready(function() {


  $('#module').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "buttons": [{
      text: '<i class="fa fa-plus" aria-hidden="true"></i>',
      titleAttr: 'Adicionar Módulo',
      action: function(e, dt, node, config) {
          moduleModal()
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
