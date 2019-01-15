$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    wss.start();
    
    $("#searchButton").on("click", function(e) {
    	var message = $.trim($('#searchInput').val());
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
    $("#homeButton").on("click", function(e) {
    	var message = get_input_values();
    	if ( message.length != 0) {
    		sendMessage(message);
    		$('#homeButton').val("").focus();
    	}
        return false;
    });
    $("#homeInput, #inclwords, #exclwords, #fromdate, #todate").on("keypress", function(e) {
        if (e.keyCode == 13) {
        	var message = get_input_values();
        	if ( message.length != 0) {
        		sendMessage(message);
        		$('#homeInput').val("").focus();
        	}
            return false;
        }
    });

    $('#homeInput').val("").focus()
    
});


function get_input_values(){
	var dict = {};
	dict["should"] = $.trim($('#homeInput').val());
	dict["must"] = $.trim($('#inclwords').val());
	dict["must_not"] = $.trim($('#exclwords').val());
	dict["from"] = $.trim($('#fromdate').val());
	dict["to"] = $.trim($('#todate').val());
	dict["sector"] = $('#sector').val();
	return dict
}


function sendMessage(message) {
	var data = new Object();
	data.path = window.location.pathname;
	data.message = message;
	wss.socket.send(JSON.stringify(data));
}

var wss = {
    socket: null,

    start: function() {
    	
        var url = "wss://" + location.host + "/wss";
        wss.socket = new WebSocket(url);
        
        wss.socket.onmessage = function(event) {
        	
        	var recv = JSON.parse(event.data);

        	if(recv.hasOwnProperty('path') && recv.hasOwnProperty('message')){
        		
        		if (recv['path'] == '/'){
        		
	        		var container = document.getElementById("home_container")
	        			//.getElementsByTagName('tbody')[0];
	        		
	        		var obj = recv["message"];
	        		var content;
	        		var pagenum = 1;
	        		for (var key in obj) {
	        		    if (obj.hasOwnProperty(key)) {
	        		    	//var newRow = container.insertRow(container.rows.length);
	        		    	//var newCell = newRow.insertCell(0);
	        		    	//newCell.appendChild(child);
	        		    	
		        			content = obj[key];
		        			var child = document.createElement("div");
		        			child.innerHTML = doc_node(pagenum, content).trim();
		        			container.appendChild(child);
		        			container.style.width="100%";
		        			feather.replace();
		        			pagenum = pagenum + 1;
	        		    }
	        		}
	        	    // ---------------------------------------
	        		$('#pagination').twbsPagination({
	        			totalPages: content["total"] || 1,
	        			// the current page that show on start
	        			startPage: 1,
	        			// maximum visible pages
	        			visiblePages: 5,
	        			initiateStartPageClick: true,
	        			// template for pagination links
	        			href: false,
	        			// variable name in href template for page number
	        			//hrefVariable: '{{number}}',
	        			// Text labels
	        			first: 'First',
	        			prev: 'Prev.',
	        			next: 'Next',
	        			last: 'Last',
	        			// carousel-style pagination
	        			loop: false,
	        			// callback function
	        			onPageClick: function (event, page) {
	        				$('.page-active').removeClass('page-active');
	        				$('#page'+page).addClass('page-active');
	        				/*
	        				if ($(".page-active")[0]){
	        					var el = document.getElementsByClassName('page-active')[0].id;
	        					console.log(el);
	        				}
	        				*/
	        			},
	        			// pagination Classes
	        			paginationClass: 'pagination',
	        			nextClass: 'next',
	        			prevClass: 'prev',
	        			lastClass: 'last',
	        			firstClass: 'first',
	        			pageClass: 'pageX',
	        			activeClass: 'active',
	        			disabledClass: 'disabled'
	        		});
	        		// ---------------------------------------
	        		$( "#home_container" ).show()
	        		$( "#home_blank" ).hide();
        		}else if (recv['path'] == '/twitter'){
        			wss.tweetMessage(JSON.stringify(recv));
        		}else{
        			wss.showMessage(JSON.stringify(recv));
        		} // recv['path']
        	} // if(recv.hasOwnProperty('path') && recv.hasOwnProperty('message')){
        } // wss.socket.onmessage
    }, // start
    
    showMessage: function(message) {
    	console.log('received: ' + message)
    },  // showMessage
    
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
    	
    } // tweetMessage
};


//Helper functions -----------------------------

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


function doc_node(pagenum, data){
	var pages = data["pages"];
	var img = ''
	var node =  
		'<div class="page" id="page' + pagenum + '">' +
			'<div class="card">' +
				'<div class="card-header">' +
					'<nav class="navbar navbar-light bg-light justify-content-between">' +
						'<div class="btn-toolbar" role="toolbar" aria-label="Toolbar with button groups">' + 
							'<div class="btn-group mr-2" role="group" aria-label="First group">' +
								'<a href=readonline/' + data["document"] + ' target="_blank">' +
									'<button class="btn btn-sm btn-outline-dark" type="button">' + 
										'<i data-feather="monitor"></i> Read Online' +
									'</button>' +
								'</a>' +
							'</div>' +
							'<div class="btn-group" role="group" aria-label="Second group">' +
								'<a href=' + data["fileurl"] + ' target="_blank">' +
									'<button class="btn btn-sm btn-outline-dark" type="button">' +
										'<i data-feather="download"></i> Download' + 
									'</button>' +
								'</a>' +
							'</div>' +
						'</div>' +
						'<div>' +
							data["tags"] +
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
					'</fieldset>' +
				'</div>' +
			'</div>' +
			'<div class="jumbotron">' +
				'<p class="lead">' + data['summary'] + '</p>' +
			'</div>' +
			'<div class="container pb-cmnt-container">' +
				'<div class="row">' +
					'<div class="col-md-6 offset-md-3">' +
						'<div class="panel panel-info">' +
							'<div class="panel-body">' +
								'<textarea class="pb-cmnt-textarea" placeholder="Write your comment here!"></textarea>' +
								'<form class="form-inline">' +
									'<div class="btn-group">' +
										'<button class="btn" type="button"><span data-feather="image"></span></button>' +
										'<button class="btn" type="button"><span data-feather="video"></span></button>' +
										'<button class="btn" type="button"><span data-feather="mic"></span></button>' +
										'<button class="btn" type="button"><span data-feather="file"></span></button>' +
									'</div>' +
									'<button class="btn btn-primary pull-right" type="button">Share</button>' +
								'</form>' +
							'</div>' +
						'</div>' +
					'</div>' +
				'</div>' +
			'</div>' +
		'</div>'
	return node
}
