inlets = 1;
outlets = 1;

var t = 0;

function bang() {
	var myDate = new Date();
	t = myDate.getTime();
	post("current time" + t);
	post();
	outlet(0, t); // will send out the unix time in milliseconds when receiving a bang
}