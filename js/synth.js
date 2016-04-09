SYNTH = {};
SYNTH.keepPath = { "distance": 0, "steps": [] };
SYNTH.sendPath = new FormData();
SYNTH.nextLine = 0;
SYNTH.voices = $(".voice");
SYNTH.init = function() {
	$("button.talkerbutton").click(SYNTH.talkToMe);
	$("button.mapbutton").click(SYNTH.generateMap);
	$("button.clickbutton").click(SYNTH.poller);
	$("button.directionlist").click(SYNTH.getDirections);
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
					url: "http://localhost:8080?obj=maps&type=paths",
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
SYNTH.currentVoice;
SYNTH.message = new SpeechSynthesisUtterance();
SYNTH.talkToMe = function(txt, voiceType) {
	console.log("Trying to say " + txt);
	if (speechSynthesis in window) {
		console.log("Theoretically, I should talk.");
	}
	else {
		console.log("No talking will be had.");
	}

	//msg.text = SYNTH.keepPath['steps'][SYNTH.nextLine]['text'];
	SYNTH.message.text = txt;
	if (SYNTH.currentVoice == null || SYNTH.currentVoice.name != voiceType) {
		SYNTH.currentVoice = speechSynthesis.getVoices().filter(function(voice) {
			return voice.name == voiceType;
		})[0];
	}
	SYNTH.message.voice = SYNTH.currentVoice;
	console.log(SYNTH.currentVoice);
	window.speechSynthesis.speak(SYNTH.message);

	//if (SYNTH.nextLine + 1 >= SYNTH.keepPath['steps'].length) {
	//	SYNTH.nextLine = 0;
	//}
	//else SYNTH.nextLine++;
}

SYNTH.message.onend = function(event) {
	console.log("Done saying " + SYNTH.message.text);	
}

SYNTH.loadVoices = function() {
	var voices = speechSynthesis.getVoices();
	var allVoices = new FormData();

	voices.forEach(function(voice, i) {
		//console.log(voice);
		var option = document.createElement('option');
    
		option.value = voice.name;
		option.innerHTML = voice.name;
		allVoices.append(i, voice.name);
		  
    // Add the option to the voice selector.
		$(".voice")
			.append($("<option></option>")
			.attr("value", voice.name)
			.text(voice.name));
	});

	return allVoices;
}

// Execute loadVoices.
SYNTH.loadVoices();

SYNTH.allVoicesLoaded = 0;
// Chrome loads voices asynchronously.
window.speechSynthesis.onvoiceschanged = function(e) {
	if (SYNTH.allVoicesLoaded == 0) {
		allVoices = SYNTH.loadVoices();

		$.ajax({
			url: "http://localhost:8080?obj=voice&type=voicelist",
			method: "POST",
			contentType: false,
			processData: false,
			data: allVoices,
		}).done(function(data){
			console.log("All voices sent.");
		});
	}
};

SYNTH.fakeClick = 0;
SYNTH.fakeClickTest = function() {
	clickData = new FormData();
	clickData.append("click_id", SYNTH.fakeClick);
	clickData.append("step_id", 3);
	clickData.append("timestamp", Date.now());
	clickData.append("checked", 0);

	//clickData = { "click_id": 0, "index": 3, "timestamp": 1457400687, "checked": 0};
	$.ajax({
		url: "http://localhost:8080?obj=voice&type=triggers&action=utter",
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

SYNTH.getPathsList = function() {
	$.ajax({
		url: "http://localhost:8080?obj=maps&type=paths",
		method: "GET",
		contentType: false,
		processData: false,
		dataType: "json"
	}).done(function(data){
		console.log(data);
		console.log("WE DID IT");
		$(".testland").append(JSON.stringify(data));
	});	
}

SYNTH.pollCount = 0;
SYNTH.lastTimestamp = "none";
SYNTH.poller = function() {
	(function poll() {
		setTimeout(function() {
			console.log("Polling attempt #" + SYNTH.pollCount);
			SYNTH.pollCount++;
			$.ajax({ 
				url: "http://localhost:8080?obj=voice&type=triggers&action=utter",
				method: "GET",
				dataType: "json",
				success: function(data) {
					$(".testland").append(JSON.stringify(data));
					//console.log(data['timestamp']);
					if ("error_name" in data) {
						console.log("I ain't talkin. You can't make me.");
					}
					else {
						SYNTH.talkToMe(data['text'], data['voice_type']);
						console.log("Done talkin' for now");
					}
					//SYNTH.lastTimestamp = data['timestamp'];
				},
				complete: poll
			});
		}, 3000);
	})();
}

$(document).ready(SYNTH.init);