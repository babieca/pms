$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    wss.start();
    
    $("#searchButton").on("click", function(e) {
    	var message = $.trim($('#message').val());
    	if ( message.length != 0) {
    		sendMessage(message);
    		$('#searchInput').val("").focus();
    	}
        return false;
    });
    $("#searchInput").on("keypress", function(e) {
        if (e.keyCode == 13) {
        	var message = $.trim($('#searchInput').val());
        	if ( message.length != 0) {
        		sendMessage(message);
        		$('#searchInput').val("").focus();
        	}
            return false;
        }
    });

    $('#searchInput').val("").focus()

    
});

function sendMessage(message) {
	var data = new Object();
	data.path = window.location.pathname;
	data.message = message;
	wss.socket.send(JSON.stringify(data));
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

var wss = {
    socket: null,

    start: function() {
    	
        var url = "wss://" + location.host + "/wss";
        wss.socket = new WebSocket(url);
        
        wss.socket.onmessage = function(event) {
        	
        	var recv = JSON.parse(event.data);
        	console.log(event.data);
        	if(recv.hasOwnProperty('path') && 
        		recv.hasOwnProperty('message')){
        		
	        	if (recv['path'] == '/twitter'){
	        		wss.tweetMessage(recv['message']);
	        		
	        	}else if (recv['path'] == '/gutenberg'){
	        		var book = document.getElementById("parent");
	        		
	        		var obj = recv["message"];
	        		var content = obj[Object.keys(obj)[0]];
	        		console.log('----')
	        		console.log(content)
	        		console.log('====')
	        		book.innerHTML = gutenberg_node(content).trim();
	        		book.style.width="100%";
	        		turn.init('book');
	        	    feather.replace();
	        		
	        	}else{
	        		wss.showMessage(JSON.stringify(recv));
	        	}
        	}
        }
    },

    showMessage: function(message) {
    	console.log('received: ' + message)
    },
    
    tweetMessage: function(message){
		var data = [date_format(message['created_at']), 
					message['keyword'],
					message['tweet'],
					message['user_name'],
					message['user_followers_count'],
					message['user_location']]

	    table
	    	.row.add(data)
	    	.draw();
    	
    }
};

// Helper functions -----------------------------

function filter() {
	var input, filter, table, tr, td, i, coltweet;
	coltweet = 3;
	input = document.getElementById("srchfilter");
	filter = input.value.toUpperCase();
	table = document.getElementById("tweetstable");
	tr = table.getElementsByTagName("tr");
	for (i = 0; i < tr.length; i++) {
		td = tr[i].getElementsByTagName("td")[coltweet];
		if (td) {
			if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
				tr[i].style.display = "";
			} else {
				tr[i].style.display = "none";
			}
		}       
	}
}

function date_format(dateString)
{
	var date = new Date(dateString),
	
    year = date.getFullYear()
    
    month = (date.getMonth() + 1).toString()
    formatedMonth = (month.length === 1) ? ("0" + month) : month 
    
    day = date.getDate().toString()
    formatedDay = (day.length === 1) ? ("0" + day) : day
    
    hour = date.getHours().toString(),
    formatedHour = (hour.length === 1) ? ("0" + hour) : hour
    
    minute = date.getMinutes().toString()
    formatedMinute = (minute.length === 1) ? ("0" + minute) : minute
    
    second = date.getSeconds().toString()
    formatedSecond = (second.length === 1) ? ("0" + second) : second;
    
    return formatedDay + "-" + formatedMonth + "-" + year + " " + formatedHour + ':' + formatedMinute + ':' + formatedSecond;
}

function gutenberg_node(data){
	var pages = data["pages"];
	var img = ''
	var node = 
'<div class="card">' +
	'<div class="card-header">' +
		'<nav class="navbar navbar-light bg-light justify-content-between">' +
			'<ul class="pagination justify-content-end my-2">' +
				'<li class="page-item disabled"><a class="page-link" href="#" tabindex="-1">Previous</a></li>' +
				'<li class="page-item"><a class="page-link" href="#">Next</a></li>' +
			'</ul>' +
			'<div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">' + 
				'<div class="btn-group mr-2" role="group" aria-label="First group">' +
					'<button class="btn btn-sm btn-outline-dark" type="button">' + 
						'<i data-feather="monitor"></i> Read Online' +
					'</button>' +
				'</div>' +
				'<div class="btn-group" role="group" aria-label="Second group">' +
					'<button class="btn btn-sm btn-outline-dark" type="button">' +
						'<i data-feather="download"></i> Download' + 
					'</button>' +
				'</div>' +
			'</div>' +
		'</nav>' +
	'</div>' +
	'<div class="card-body">' +
		'<fieldset disabled="">' +
			'<div class="form-group row">' +
				'<label class="col-sm-1 col-form-label">Author</label>' +
				'<label class="col-sm-3 col-form-label" style="background-color:#ccc">' + data["author"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Title</label>' +
				'<label class="col-sm-3 col-form-label" style="background-color:#ccc">' + data["title"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Num. Pages</label>' +
				'<label class="col-sm-1 col-form-label" style="background-color:#ccc">' + data["numpages"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Created</label>' +
				'<label class="col-sm-1 col-form-label" style="background-color:#ccc">' + data["created"] + '</label>' +
			'</div>' +
			'<div class="jumbotron jumbotron-fluid p-3">' +
				'<p class="lead">' + data['summary'] + '</p>' +
			'</div>' +
		'</fieldset>' +
		'<div class="book-wrapper">' +
			'<div class="book-container">' +
				'<div class="book" id="book">'
					for (var i = 0; i < pages.length; i++) {
						img +='<div class="page"><img src="' +pages[i] +'" alt=""/></div>'
					}
				node += img
				node +=
				'</div>' +
			'</div>' +
		'</div>' +
	'</div>' +
'</div>';
	return node
}