
function managementModalReset() {
  // Supplier stuff
  $('#NAME').val("");
  $('#TYPE').val("");
  $('#PHONE').val("");
  $('#EMAIL').val("");
  $('#CITY').val("");
  $('#STATE').val("");
  $('#NOTES').val("");

  // Crop stuff
  $('#code').val("");
  $('#date').val("");
  $('#status').val("");
  $('#notes').val("");
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
    managementModalReset();
});


function cropModal(data) {
  managementModalReset();
  if (data == null){
    $("#crop-modal-title").html("Add New Production");
    $("#crop-modules-panel").hide();
    $('#savecrop').html("Save");
  }else{
    $("#crop-modal-title").html("Edit Production <font color='red'><b>"+data[0]+"</b></font>");
     $("#crop-modules-panel").show();
    $("#code").val(data[0]);
    $("#date").val(data[1]);
    $("#status").val(data[3]);
    $("#notes").val(data[4]);
    $('#savecrop').html("Update");

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
       "url" : "/management/crop-module?code="+$("#cropModalForm").find("#code").val(),
       "type": "GET",
       "dataSrc":""
      },
      "columns": [
        { "data": "CODE", "visible": false, "targets": 0  },
        { "name": "Module", "data": "MODULE", "targets": 1  },
        { "name": "Plant", "data": "PLANT", "targets": 2  },
        { "name": "Substrate", "data": "SUBSTRATE", "targets": 3  }
      ],
     "buttons": [
       {
         text: '<i class="fa fa-plus" aria-hidden="true"></i>',
         titleAttr: 'Add Production Module',
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
           location.reload();
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
          resp = JSON.parse(response.responseText);
          swal("Success", resp.message, "success");
          $("#saveplant").attr("disabled", "disabled");
           location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response.responseText);
          swal("Failed", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new plant!");
    }
  });
};


//**********************************
//*********  SUPPLIER  *************
//**********************************
function supplierModal(data) {
  managementModalReset();
  if (data == null){
    $("#supplier-modal-title").html("Add New Supplier");
    $('#saveSupplier').html("Save");
    regionSelector();
  }else{
    var shortName = data[0].length > 10 ? jQuery.trim(data[0]).substring(0, 8).trim(this) + "...": data[0];
    $("#supplier-modal-title").html("Edit Supplier <font color='red'><b>"+shortName+"</b></font>");
    $('#NAME').val(data[0]);
    $('#TYPE').val(data[1]);
    $('#PHONE').val(data[2]);
    $('#EMAIL').val(data[3]);
    $('#STATE').val(data[5]);
    regionCitySelector(data[5], data[4]);
    $('#NOTES').val(data[6]);
    $('#saveSupplier').html("Update");
  }
  $('#supplierModal').modal('show')
}

function saveSupplier() {
  swal({
    title: "Do you want to add a supplier?",
    icon: "info",
    showCancelButton: true,
    confirmButtonColor: "#DD6B55",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    closeOnConfirm: false
  }, function(isConfirm) {
    if (isConfirm) {
      var form = $('#supplierModalForm');
      var request = {
               "NAME": $('#NAME').val(),
               "TYPE": $('#TYPE').val(),
               "PHONE": $('#PHONE').val(),
               "EMAIL": $('#EMAIL').val(),
               "CITY": $('#CITY').val(),
               "STATE": $('#STATE').val(),
               "NOTES": $('#NOTES').val()
            };
      $.ajax({
        url: '/management/save-supplier',
        type: 'POST',
        data: JSON.stringify(request),
        contentType: 'application/json',
        success: function(response) {
          resp = JSON.parse(response);
          swal("Sucess", resp.message, "success");
          $("#saveSupplier").attr("disabled", "disabled");
          location.reload();
        },
        error: function(response) {
          resp = JSON.parse(response);
          swal("Error", resp.message, "error");
        }
      });
    } else {
      swal("You will not save new supplier!");
    }
  });
};

//**********************************
//******** HTML loaded *************
//**********************************
$(document).ready(function() {
  //***** CROP *****
  $('#crop').DataTable({
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
        titleAttr: 'Add Production',
        action: function(e, dt, node, config) {cropModal(null)}
      },{
        text: '<i class="fa fa-pencil-square-o" aria-hidden="true"></i>',
        className :"editButton",
        titleAttr: 'Edit Production',
        extend: "selectedSingle",
        action: function (e, dt, bt, config) {
          cropModal( dt.row( { selected: true } ).data()); }
      }]
  });
  //***** DATEPICKER *****
  $('#datapicker').datepicker({
    format: "yyyy-mm-dd",
    calendarWeeks: true,
    autoclose: true,
    todayHighlight: true
  });
  //***** SUPPLIER *****
  $('#supplier').DataTable({
    "bLengthChange": false,
    "info": false,
    "bPaginate": false, //hide pagination control
    "responsive": true,
    "dom": 'Bfrtip',
    "select": {
      style:    'os',
      selector: 'td:first-child'
    },
    "buttons": [
        {
          text: '<i class="fa fa-plus" aria-hidden="true"></i>',
          titleAttr: 'Add Supplier',
          action: function(e, dt, node, config) {supplierModal(null)}
        },{
          text: '<i class="fa fa-pencil-square-o" aria-hidden="true"></i>',
          className :"editButton",
          titleAttr: 'Edit Supplier',
          extend: "selectedSingle",
          action: function (e, dt, bt, config) {
            supplierModal( dt.row( { selected: true } ).data()); }
        }],
      "columnDefs": [
        {
          targets: [ 0,1,2,3,4,5,6 ],// ALL
          render: function ( data, type, row ) {
              var truncated = data.length > 16 ? data.substr(0, 16) + "...": data;
              return truncated;
            }
        }]
  });
  //***** GENERAL *****
  //to align btns in mobile mode
  $('div.dataTables_wrapper > div.btn-group').removeClass('dt-buttons');
  //Brazilian regions
  regionSelector();
});
