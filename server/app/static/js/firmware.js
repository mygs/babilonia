$(document).ready(function() {
  var table = $('#firmware').DataTable({
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
}
