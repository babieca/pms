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
    $("#gutenbergButton").on("click", function(e) {
    	var message = $.trim($('#gutenbergInput').val());
    	if ( message.length != 0) {
    		sendMessage(message);
    		$('#gutenbergButton').val("").focus();
    	}
        return false;
    });
    $("#gutenbergInput").on("keypress", function(e) {
        if (e.keyCode == 13) {
        	var message = $.trim($('#gutenbergInput').val());
        	if ( message.length != 0) {
        		sendMessage(message);
        		$('#gutenbergInput').val("").focus();
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

        	if(recv.hasOwnProperty('path') && 
        		recv.hasOwnProperty('message')){
        		
	        	if (recv['path'] == '/gutenberg'){
	        		var container = document.getElementById("gutenberg_container")
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
		        			child.innerHTML = gutenberg_node(pagenum, content).trim();
		        			container.appendChild(child);
		        			container.style.width="100%";
		        			//turn.init(key);
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
	        		$( "#gutenberg_container" ).show()
	        		$( "#gutenberg_blank" ).hide();
	        	}else{
	        		wss.showMessage(JSON.stringify(recv));
	        	}
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

function gutenberg_node(pagenum, data){
	var pages = data["pages"];
	var img = ''
	var node =  
'<div class="card page" id="page' + pagenum + '">' +
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
	'</div>' +
'</div>'
	return node
}

//Returns an array of maxLength (or less) page numbers
//where a 0 in the returned array denotes a gap in the series.
//Parameters:
//totalPages:     total number of pages
//page:           current page
//maxLength:      maximum size of returned array
function getPageList(totalPages, page, maxLength) {
	if (maxLength < 5) throw "maxLength must be at least 5";
	
	function range(start, end) {
		return Array.from(Array(end - start + 1), (_, i) => i + start);
	}

	var sideWidth = maxLength < 9 ? 1 : 2;
	var leftWidth = (maxLength - sideWidth * 2 - 3) >> 1;
	var rightWidth = (maxLength - sideWidth * 2 - 2) >> 1;
	if (totalPages <= maxLength) {
		// no breaks in list
		return range(1, totalPages);
	}
	if (page <= maxLength - sideWidth - 1 - rightWidth) {
	 // no break on left of page
		return range(1, maxLength - sideWidth - 1)
	  	.concat([0])
	  	.concat(range(totalPages - sideWidth + 1, totalPages));
	}
	if (page >= totalPages - sideWidth - 1 - rightWidth) {
		// no break on right of page
		return range(1, sideWidth)
		.concat([0])
		.concat(
			range(totalPages - sideWidth - 1 - rightWidth - leftWidth, totalPages)
		);
	}
	// Breaks on both sides
	return range(1, sideWidth)
		.concat([0])
		.concat(range(page - leftWidth, page + rightWidth))
		.concat([0])
		.concat(range(totalPages - sideWidth + 1, totalPages));
}
	
$(function() {
	// Number of items and limits the number of items per page
	var numberOfItems = $("#contaner .content").length;
	var limitPerPage = 2;
	// Total pages rounded upwards
	var totalPages = Math.ceil(numberOfItems / limitPerPage);
	// Number of buttons at the top, not counting prev/next,
	// but including the dotted buttons.
	// Must be at least 5:
	var paginationSize = 7;
	var currentPage;

	function showPage(whichPage) {
		if (whichPage < 1 || whichPage > totalPages) return false;
		currentPage = whichPage;
		$("#container .content")
		.hide()
		.slice((currentPage - 1) * limitPerPage, currentPage * limitPerPage)
		.show();
		// Replace the navigation items (not prev/next):
		$(".pagination li").slice(1, -1).remove();
		getPageList(totalPages, currentPage, paginationSize).forEach(item => {
			$("<li>")
			.addClass(
				"page-item " +
				(item ? "current-page " : "") +
				(item === currentPage ? "active " : "")
			)
			.append(
				$("<a>")
				.addClass("page-link")
				.attr({
					href: "javascript:void(0)"
				})
				.text(item || "...")
			)
			.insertBefore("#next-page");
		});
	return true;
	}

	// Include the prev/next buttons:
	$(".pagination").append(
		$("<li>").addClass("page-item").attr({ id: "previous-page" }).append(
			$("<a>")
			.addClass("page-link")
			.attr({
				href: "javascript:void(0)"
			})
			.text("Prev")
		),
		$("<li>").addClass("page-item").attr({ id: "next-page" }).append(
			$("<a>")
			.addClass("page-link")
			.attr({
				href: "javascript:void(0)"
			})
			.text("Next")
		)
	);
	
	// Show the page links
	$("#container").show();
	showPage(1);
	
	// Use event delegation, as these items are recreated later
	$(
		document
	).on("click", ".pagination li.current-page:not(.active)", function() {
		return showPage(+$(this).text());
	});
	$("#next-page").on("click", function() {
		return showPage(currentPage + 1);
	});
	
	$("#previous-page").on("click", function() {
		return showPage(currentPage - 1);
	});
	$(".pagination").on("click", function() {
		$("html,body").animate({ scrollTop: 0 }, 0);
	});
});