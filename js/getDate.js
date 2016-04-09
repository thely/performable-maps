inlets = 3; //0: bang, prev, next, or reset; 1: step_maximum; 2: path uuid
outlets = 4; //click_id out, step_id out, timestamp out

var timestamp = 0;
var click_id = 0;
var step_id = 0;
var step_max = 0;
//var uuid = "";

function msg_int(v) {
	if (inlet == 1) {
		step_max = v;
		post("new step max is " + step_max);
		post();
	}
}

function anything() {
	/*if (inlet == 2) {
		post("we got an id: " + messagename);
		uuid = messagename;
	}*/
	if (step_max == 0 && messagename != "reset") {
		post("Step maximum not set.");
		post();
	}
	else if (messagename == "prev" && step_id >= 0) {
		step_id -= 1;
		bang();
	}
	else if (messagename == "next" && step_id < step_max-1) {
		step_id += 1;
		bang();
	}
	else if (messagename == "reset") {
		post("Resetting values.");
		post();
		click_id = 0;
		step_id = 0;
		
	}
	else {
		post("Don't understand message " + messagename);
		post();
	}
}

function bang() {
	click_id += 1;
	outlet(0, click_id.toString());
	outlet(1, step_id.toString());

	var myDate = new Date();
	timestamp = myDate.getTime();
	post("current time" + timestamp);
	post();
	outlet(2, timestamp.toString());
	//outlet(3, uuid.toString());
}