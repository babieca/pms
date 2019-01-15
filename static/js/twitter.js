table = $('#dynamic_table1').DataTable( {
    "order": [[ 0, "desc" ], [ 1, 'asc' ]],
    "columnDefs": [
        { "width": "15%"},
        { targets: '_all', visible: true }
    ]
} );