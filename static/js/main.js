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
        	
        	var recv = JSON.parse(event.data)
        	
        	if(recv.hasOwnProperty('path') && 
        		recv.hasOwnProperty('message')){
        		
	        	if (recv['path'] == '/twitter'){
	        		wss.tweetMessage(recv['message']);
	        		
	        	}else if (recv['path'] == '/gutenberg'){
	        		var book = document.getElementById("parent");
	        		book.innerHTML = gutenberg_node(recv["message"]).trim()
	        		book.style.width="100%"
	        		turn.init('book');
	        		
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

function gutenberg_node(recv){
	var pages = recv["pages"];
	var img = ''
	var node = 
'<div class="card">' +
	'<div class="card-header">' +
		'<nav class="navbar navbar-light bg-light justify-content-between">' +
			'<ul class="pagination justify-content-end my-2">' +
				'<li class="page-item disabled"><a class="page-link" href="#" tabindex="-1">Previous</a></li>' +
				'<li class="page-item"><a class="page-link" href="#">Next</a></li>' +
			'</ul>' +
			'<form class="form-inline">' +
				'<button class="btn btn-sm btn-outline-dark" type="submit">Read Online</button>' +
				'<button class="btn btn-sm btn-outline-dark" type="submit">Download</button>' +
			'</form>' +
		'</nav>' +
	'</div>' +
	'<div class="card-body">' +
		'<fieldset disabled="">' +
			'<div class="form-group row">' +
				'<label class="col-sm-1 col-form-label">Author</label>' +
				'<label class="col-sm-2 col-form-label" style="background-color:#ccc">' + recv["author"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Title</label>' +
				'<label class="col-sm-2 col-form-label" style="background-color:#ccc">' + recv["title"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Num. Pages</label>' +
				'<label class="col-sm-2 col-form-label" style="background-color:#ccc">' + recv["numpages"] + '</label>' +
				'<label class="col-sm-1 col-form-label">Created</label>' +
				'<label class="col-sm-2 col-form-label" style="background-color:#ccc">' + recv["created"] + '</label>' +
			'</div>' +
			'<div class="jumbotron jumbotron-fluid p-3">' +
				'<p class="lead">' +
					'Do am he horrible distance marriage so although. Afraid assure square so happen mr an before. His many same been well can high that. Forfeited did law eagerness allowance improving assurance bed. Had saw put seven joy short first. Pronounce so enjoyment my resembled in forfeited sportsman. Which vexed did began son abode short may. Interested astonished he at cultivated or me. Nor brought one invited she produce her.' +
					'Yourself off its pleasant ecstatic now law. Ye their mirth seems of songs. Prospect out bed contempt separate. Her inquietude our shy yet sentiments collecting. Cottage fat beloved himself arrived old. Grave widow hours among him ﻿no you led. Power had these met least nor young. Yet match drift wrong his our.' +
					'Performed suspicion in certainty so frankness by attention pretended. Newspaper or in tolerably education enjoyment. Extremity excellent certainty discourse sincerity no he so resembled. Joy house worse arise total boy but. Elderly up chicken do at feeling is. Like seen drew no make fond at on rent. Behaviour extremely her explained situation yet september gentleman are who. Is thought or pointed hearing he.' +
					'Now eldest new tastes plenty mother called misery get. Longer excuse for county nor except met its things. Narrow enough sex moment desire are. Hold who what come that seen read age its. Contained or estimable earnestly so perceived. Imprudence he in sufficient cultivated. Delighted promotion improving acuteness an newspaper offending he. Misery in am secure theirs giving an. Design on longer thrown oppose am.' +
					'Her extensive perceived may any sincerity extremity. Indeed add rather may pretty see. Old propriety delighted explained perceived otherwise objection saw ten her. Doubt merit sir the right these alone keeps. By sometimes intention smallness he northward. Consisted we otherwise arranging commanded discovery it explained. Does cold even song like two yet been. Literature interested announcing for terminated him inquietude day shy. Himself he fertile chicken perhaps waiting if highest no it. Continued promotion has consulted fat improving not way.' +
				'</p>' +
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