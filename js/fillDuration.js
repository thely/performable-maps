/*
  Inlets: 
	1. bang to increase total
	2. input current maximum
  Outlets:
	1. print current value of total
	2. bang when maximum is reached
*/
inlets = 2;
outlets = 2;

var total = 0.0;
var maximum = 0;

function bang() {
	if (inlet == 0) {
		total += .1;
		if (total >= maximum) {
			outlet(1, bang);
		}
		else {
			outlet (0, total);
		}
	}
}

function msg_float(x) {
	if (inlet == 1) {
		maximum = x * 60;
	}
}