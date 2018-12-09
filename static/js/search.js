//alert(1)
//console.log(title)

/* test.js */
var test = ""

function set_test(val)
{
    test=val
}

function show_test()
{
    alert(test);
}

$("#srchfilter").on("keypress", function(e) {
    if (e.keyCode == 13) {
        newMessage($(this));
        return false;
    }
});
$("#srchfilter").on("keypress", function(e) {
    if (e.keyCode == 13) {
        newMessage($(this));
        return false;
    }
});

/*
$(document).ready(function(e){
	
	function start(){
		var msg = document.getElementById("search").value;
		console.log(msg)
		wss.send(JSON.stringify(msg));
		return false;
	}
	
	var subm = document.getElementById("submitButton").value;
	subm.addEventListener("click", start, false);

});
*/

/*

var wsUri = "wss://echo.websocket.org/";
var output;

function init()
{
  output = document.getElementById("output");
  testWebSocket();
}

function testWebSocket()
{
  websocket = new WebSocket(wsUri);
  websocket.onopen = function(evt) { onOpen(evt) };
  websocket.onclose = function(evt) { onClose(evt) };
  websocket.onmessage = function(evt) { onMessage(evt) };
  websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt)
{
  writeToScreen("CONNECTED");
  doSend("WebSocket rocks");
}

function onClose(evt)
{
  writeToScreen("DISCONNECTED");
}

function onMessage(evt)
{
  writeToScreen('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
  websocket.close();
}

function onError(evt)
{
  writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function doSend(message)
{
  writeToScreen("SENT: " + message);
  websocket.send(message);
}

function writeToScreen(message)
{
  var pre = document.createElement("p");
  pre.style.wordWrap = "break-word";
  pre.innerHTML = message;
  output.appendChild(pre);
}

window.addEventListener("load", init, false);
*/

