$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    wss.start();
});

var wss = {
    socket: null,

    start: function() {
    	
        var url = "wss://" + location.host + "/bcst";
        wss.socket = new WebSocket(url);
        
        wss.socket.onmessage = function(event) {
        	
        	var recv = JSON.parse(event.data);

        	wss.tweetMessage(recv);
        } // wss.socket.onmessage
    }, // start
    
    tweetMessage: function(message){

		var data = [date_format(
			message['created_at']), 
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
