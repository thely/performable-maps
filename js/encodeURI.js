function anything() {
	var completeString = "";
	var a = arrayfromargs(arguments);
	for (var i = 0; i < a.length; i++) {
		if (a[i] == 0) {
			completeString += "";
		}
		else {
			completeString += a[i] + " ";
		}
	}
	/*post("received message " + a + "\n");
	post();
	post("And we made: " + completeString);*/
	//myval = a;
	outlet(0, completeString);
}