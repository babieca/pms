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
    	}
        return false;
    });
    $("#messageform").on("keypress", function(e) {
        if (e.keyCode == 13) {
        	var message = $.trim($('#message').val());
        	if ( message.length != 0) {
        		sendMessage(message);
        	}
            return false;
        }
    });

    $('#message').val("").focus()

    updater.start();
});


function sendMessage(message) {
	updater.socket.send(message);
	$('#message').val("").focus();
}

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function() {
        var url = "wss://" + location.host + "/wss";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
    	console.log('message back!: ' + JSON.stringify(message))
    	/*
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
        */
    }
};