SYNTH = {};
SYNTH.keepPath = { "distance": 0, "steps": [] };
SYNTH.sendPath = new FormData();
SYNTH.nextLine = 0;
SYNTH.init = function() {
	$("button.talkerbutton").click(SYNTH.talkToMe);
	$("button.mapbutton").click(SYNTH.generateMap);
	$("button.clickbutton").click(SYNTH.fakeClickTest);
}

/*******************************************
*** Get map data from Google if available
********************************************/
SYNTH.generateMap = function() {
	var origin = "San Fransisco, CA";
	var destination = "Oakland, CA";
	//provided code for getting the DirectionsService together
	var directionsService = new google.maps.DirectionsService;
	var directionsRequest = {
		origin: origin,
		destination: destination,
		travelMode: google.maps.DirectionsTravelMode.DRIVING,
		provideRouteAlternatives: false //multiple routes means a longer response time
	}
	directionsService.route(
		directionsRequest,
		function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				
				var steps = response['routes'][0]['legs'][0]['steps'];
				SYNTH.keepPath['distance'] = response['routes'][0]['legs'][0]['distance']['value'];
				SYNTH.keepPath['num_steps'] = steps.length;
				SYNTH.sendPath.append("distance", response['routes'][0]['legs'][0]['distance']['value']);
				SYNTH.sendPath.append("num_steps", steps.length);
				SYNTH.sendPath.append("start", origin);
				SYNTH.sendPath.append("end", destination);
				
				//Sanitize huge dictionary to only have text instructions & distance
				$.each(steps, function(key, value) {
					var temp = {};
					temp['text'] = value['instructions'].replace(/(<([^>]+)>)/ig,"");
					temp['dist'] = value['distance']['value'];
					SYNTH.keepPath['steps'].push(temp);
					//if (key < 10) key = "0" + key;
					SYNTH.sendPath.append(key+"-text", value['instructions'].replace(/(<([^>]+)>)/ig,""));
					SYNTH.sendPath.append(key+"-dist", value['distance']['value']);
				});
				
				//Throw it in the test div
				$(".testland").append(JSON.stringify(SYNTH.keepPath));
				console.log(SYNTH.sendPath);

				//Send back to the server to be saved in Sqlite3
				$.ajax({
					url: "http://localhost:8080?type=directions",
					method: "POST",
					contentType: false,
					processData: false,
					data: SYNTH.sendPath,
					//dataType: "json"
				}).done(function(data){
					console.log(data);
					console.log("WE DID IT");
				});
			}
			else {
				$(".testland").append("Unable to retrieve your route.");
			}
		})
}

/*******************************************
*** Read one line at a time from the provided text
********************************************/
SYNTH.talkToMe = function() {
	if (speechSynthesis in window) {
		console.log("Theoretically, I should talk.");
	}
	else {
		console.log("No talking will be had.");
	}

	var msg = new SpeechSynthesisUtterance();
	msg.text = SYNTH.keepPath['steps'][SYNTH.nextLine]['text'];
	msg.voiceURI = 'native';
	msg.lang = 'en-US';
	window.speechSynthesis.speak(msg);	

	if (SYNTH.nextLine + 1 >= SYNTH.keepPath['steps'].length) {
		SYNTH.nextLine = 0;
	}
	else SYNTH.nextLine++;
}

SYNTH.fakeClick = 0;
SYNTH.fakeClickTest = function() {
	clickData = new FormData();
	clickData.append("click_id", SYNTH.fakeClick);
	clickData.append("step_id", 3);
	clickData.append("timestamp", Date.now());
	clickData.append("checked", 0);

	//clickData = { "click_id": 0, "index": 3, "timestamp": 1457400687, "checked": 0};
	$.ajax({
		url: "http://localhost:8080?type=clicks",
		method: "POST",
		contentType: false,
		processData: false,
		data: clickData,
		//dataType: "json"
	}).done(function(data){
		console.log(data);
		console.log("WE DID IT");
	});
}

SYNTH.poller = function() {
	(function poll() {
		setTimeout(function() {
			$.ajax({ 
				url: "http://localhost:8080",
				method: "GET",
				dataType: "json",
				success: function(data) {
					console.log(data);
				},
				complete: poll
			});
		}, 3000);
	})();
}

$(document).ready(SYNTH.init);