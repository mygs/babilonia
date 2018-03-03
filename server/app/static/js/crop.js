
function cropModalReset() {
  $('#estado').val("");
  $('#cidade').val("");
  $('#data').val("");
  $("#savecrop").removeAttr("disabled");
  $('#crop-modules').DataTable().clear().draw();
}

function cropModuleModalReset() {
  $('#cropModuleModalFormId').val("");
  $('#cropDetailId').val("");
  $('#modulo').val("");
  $('#planta').val("");
  $('#substrato').val("");
  $("#savecropmodule").removeAttr("disabled");
}

$("#cropModuleModal").on("hidden.bs.modal", function () {
    $('#crop-module tr').removeClass("selected");
    $(".editButton").addClass("disabled")
    cropModuleModalReset();
});

$("#cropModal").on("hidden.bs.modal", function () {
    $('#crop tr').removeClass("selected");
    $(".editButton").addClass("disabled")
    cropModalReset();
});


function cropModal(data) {
  cropModalReset();
  if (data == null){
    $("#crop-modal-title").html("Adicionar Nova Produção");
    $("#crop-modules-panel").hide();
    $('#savecrop').html("Salvar");
  }else{
    $("#crop-modal-title").html("Editar Produção <font color='red'><b>"+data[0]+"</b></font>");
     $("#crop-modules-panel").show();
    $("#id").val(data[0]);
    $("#estado").val(data[2]);
    regionCitySelector(data[2], data[1]);
    $("#data").val(data[3]);
    $('#savecrop').html("Atualizar");

  }
    $('#cropModal').modal('show');



    $('#crop-modules').DataTable({
     "bLengthChange": false,
     "info": false,
     "order": [[1, 'asc']],
     "searching": false,
     "bPaginate": false, //hide pagination control
     "dom": 'Bfrtip',
     "select": {
       style:    'os',
       selector: 'td:first-child'
     },
     "processing": true,
     //"serverSide": true,
     "ajax": {
       "url" : "/management/crop-module?id="+$("#cropModalForm").find("#id").val(),
       "type": "GET",
       "dataSrc":""
      },
      "columns": [
        { "data": "ID", "visible": false, "targets": 0  },
        { "name": "Módulo", "data": "MODULE", "targets": 1  },
        { "name": "Planta", "data": "PLANT", "targets": 2  },
        { "name": "Substrato", "data": "SUBSTRATE", "targets": 3  }
      ],
     "buttons": [
       {
         text: '<i class="fa fa-plus" aria-hidden="true"></i>',
         titleAttr: 'Adicionar Módulo na Produção',
         action: function(e, dt, node, config) {
            cropModuleModal(null);
         }
       },
       {
         text: '<i class="fa fa-pencil-square-o" aria-hidden="true"></i>',
         titleAttr: 'Editar Módulo na Produção',
         action: function(e, dt, node, config) {
            cropModuleModal(dt.row( { selected: true } ).data());
         }
       },
       {
         text: '<i class="fa fa-trash" aria-hidden="true"></i>',
         titleAttr: 'Remover Módulo da Produção',
         className :"deleteButton",
         extend: "selectedSingle",
         action: function(e, dt, node, config) {
           deletecropmodule(dt.row( { selected: true } ).data());
         }
       }],
        "destroy" : true
     });

}


function cropModuleModal(data) {
  cropModuleModalReset();
  var id = $("#cropModalForm").find("#id").val()
  if (data == null){
    $("#crop-module-modal-title").html("Adicionar Módulo (<font color='red'><b>"+id+"</b></font>)");
    $('#savecropmodule').html("Salvar");
  }else{
    $("#crop-module-modal-title").html("Editar Módulo (<font color='red'><b>"+id+"</b></font>)");
    $("#cropDetailId").val(data.ID);
    $("#modulo").val(data.MODULE);
    $("#planta").val(data.PLANT_ID);
    $("#substrato").val(data.SUBSTRATE);
    $('#savecropmodule').html("Atualizar");
  }
    $('#cropModuleModalFormId').val(id);
    $('#cropModuleModal').modal('show');
}

function savecrop() {
  swal({
    title: "Você deseja salvar uma nova produção?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
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
          swal("Sucesso", resp.message, "success");
          $("#savecrop").attr("disabled", "disabled");
           //location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Falhou", resp.message, "error");
        }
      });
    } else {
      swal("Você não salvou a produção!");
    }
  });
};


function savecropmodule() {
  swal({
    title: "Você deseja salvar o módulo na produção?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/save-crop-module',
        type: 'POST',
        data: $('#cropModuleModalForm').serialize(),
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Sucesso", resp.message, "success");
          $("#savecropmodule").attr("disabled", "disabled");
           //location.reload();
           $('#crop-modules').DataTable().ajax.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Falhou", resp.message, "error");
        }
      });
    } else {
      swal("Você não salvou o módulo na produção!");
    }
  });
};


function deletecropmodule(data) {
  swal({
    title: "Você deseja remover o módulo dessa Produção?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirmar",
    cancelButtonText: "Cancelar",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      $.ajax({
        url: '/management/delete-crop-module',
        type: 'POST',
        data: {"id": data.ID},
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Sucesso", resp.message, "success");
           $('#crop-modules').DataTable().ajax.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Falhou", resp.message, "error");
        }
      });
    } else {
      swal("Você não removeu o módulo da produção!");
    }
  });
};

$(document).ready(function() {


  var table = $('#crop').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "dom": 'Bfrtip',
    "select": {
      style:    'os',
      selector: 'td:first-child'
    },
    "buttons": [
      {
        text: '<i class="fa fa-plus" aria-hidden="true"></i>',
        titleAttr: 'Adicionar Produção',
        action: function(e, dt, node, config) {cropModal(null)}
      },{
        text: '<i class="fa fa-pencil-square-o" aria-hidden="true"></i>',
        className :"editButton",
        extend: "selectedSingle",
        action: function (e, dt, bt, config) {
          cropModal( dt.row( { selected: true } ).data()); }
      }]
  });

  $('#crop tbody').on( 'click', 'tr', function () {
    if ( $(this).hasClass('selected') ) {
        $(this).removeClass('selected');
    }
    else {
        table.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
    }
  } );
  $('#datapicker').datepicker({
    format: "yyyy-mm-dd",
    calendarWeeks: true,
    autoclose: true,
    todayHighlight: true
  });

  regionSelector();

});
