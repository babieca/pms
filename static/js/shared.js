var wss = null
var url = "wss://" + location.host + "/wss"
self.addEventListener("connect", function(e) {
    var port = e.ports[0]
    port.addEventListener("message", function(e) {
        if (e.data === "start") {
            if (wss === null) {
                wss = new WebSocket(url);
                port.postMessage("started connection to " + url);
            } else {
                port.postMessage("reusing connection to " + url);
            }
        }
    }, false);
    port.start();
}, false);
wss.onmessage = function(e) {
	console.log(1);
	port.postMessage("11 ");
}
wss.onopen = function(evt) {
	console.log(2);
	port.postMessage("22 ");
};
wss.onclose = function(evt) {
	console.log(3);
	port.postMessage("33 ");
};
wss.onmessage = function(evt) {
	console.log(4);
	port.postMessage("44 ");
};
wss.onerror = function(evt) {
	console.log(5);
	port.postMessage("55 ");
};