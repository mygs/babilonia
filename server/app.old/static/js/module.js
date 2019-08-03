function moduleModalReset() {
  $('#nome').val("");
  $('#tipo').val("");
  $('#oasis').val("");
  $('#data').val("");
}

function moduleModal() {
  moduleModalReset();
  $('#moduleModal').modal('show');
}


function savemodule() {
  swal({
    title: "Você deseja salvar um novo módulo?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
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
          swal("Sucesso", resp.message, "success");
          $("#savemodule").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Falhou", resp.message, "error");
        }
      });
    } else {
      swal("Você não salvou o módulo!");
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
