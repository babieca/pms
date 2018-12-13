$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $('#dynamic_table').DataTable({
    	"order": [[ 0, "asc" ], [ 1, 'asc' ]],
    	"columnDefs": [
    		{ "width": "15%"},
    		{ targets: '_all', visible: true }
    	]
    });
    
    $("#submitButton").on("click", function(e) {
    	var message = $.trim($('#message').val());
    	if ( message.length != 0) {
    		sendMessage(message);
    		$('#message').val("").focus();
    	}
        return false;
    });
    $("#messageform").on("keypress", function(e) {
        if (e.keyCode == 13) {
        	var message = $.trim($('#message').val());
        	if ( message.length != 0) {
        		sendMessage(message);
        		$('#message').val("").focus();
        	}
            return false;
        }
    });

    $('#message').val("").focus()
    
});
