function cropModalReset() {
  $('#estado').val("");
  $('#cidade').val("");
  $('#data').val("");

}

$("#cropModal").on("hidden.bs.modal", function () {
    $('#crop tr').removeClass("selected");
    $(".editButton").addClass("disabled")
    cropModalReset();
});


function cropModal(data) {
  cropModalReset();
  if (data == null){
    $("#crop-modal-title").text("Adicionar Nova Produção");
  }else{
    $("#crop-modal-title").text("Editar Produção "+data[0]);
    $("#estado").val(data[2]);
    regionCitySelector(data[2], data[1]);
    $("#data").val(data[3]);
  }
    $('#cropModal').modal('show');
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
