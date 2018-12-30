if (typeof(window.SharedWorker) === 'undefined') {
  throw("Your browser does not support SharedWorkers")
}
var worker = new SharedWorker("/static/js/shared.js");

worker.port.onmessage = function(evt){
	console.log(evt.data);
};

worker.port.start();
worker.port.postMessage("start");
