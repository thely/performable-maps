# performable-maps

## Python API "endpoints"

These are internal endpoints meant to interact with data saved in a Sqlite3 database. They aren't "true" endpoints because the server is implemented using SimpleHttpServer, and I felt better about taking the cheap route with query strings than trying to reinvent Flask. All data is returned as JSON.

### ?obj=maps&type=paths

Paths is a list of each set of directions saved in the database.

**Variables**

* id
* timestamp: date path was generated
* start: origin point of the path
* end: destination point of the path
* distance: total distance of this path
* num_steps: number of steps in this path

**Methods**

* GET: Get a list of all paths currently saved.
* POST: Add a new path to the list. Adding a path also means adding its steps; POSTing to paths and steps are essentially the same action.

### ?obj=maps&type=steps&path-id=uuid

Steps are the individual instructions in a path.

**Variables**

* path_id: id of the step's parent path
* step_id: which step this is in the overall path
* text: direction text for this step, i.e. "Turn left at Main St"
* distance: distance traveled after this step

**Methods**

* GET: Gets all the steps of a given path based on the path's UUID.

### ?obj=voice&type=triggers&action=utter

The Web Speech API is not accessible via jweb, Max's Chromium-based embedded browser. We have to trick an actual browser window (optimally, Chrome) into auto-triggering button presses by polling for "clicks" from the server, which are sent to the server by Max.

**Variables**

* click_id: the id of this click
* step_id: which step instruction this click intends to trigger
* timestamp: when this click was sent from Max
* voice_type: the SpeechSynthesisVoice to be used for this click; usually set before any clicks are triggered, but present in case changes are desired.
* checked: whether or not the browser has found this click while polling yet.

**Methods**

* GET: From the browser, check for any unchecked clicks that Max has sent.
* POST: From Max, send a new click.

### ?obj=voice&type=triggers&action=[onstart,onend]

SpeechSynthesisUtterances have .onstart() and .onend() to signify when the audio of an utterance starts and ends. Max can poll for these values, to trigger a record~ object on/off. Getting these values with enough time to be useful means polling at incredibly small time intervals (200 ms seems to work), but if we toggle off polling once `onend` is received, the server takes a bit less of a hit.

**Variables**

* type: whether the trigger is an onstart or onend event
* time: a UNIX timestamp of when the event occurred
* checked: whether or not Max has seen this event yet

**Methods**

* GET: Max asks for any available speech triggers
* POST: Browser sends onstart/onend when utterances start/end

### ?obj=voice&type=voicelist

To make life easier on the performer, some of the mostly-browser actions are in Max. `voicelist` is the list of SpeechSynthesisVoices, stored/sent for Max's benefit.

**Variables**

* id: just a number, so that the voices are in order in the Max menu
* text: name of this voice

**Methods**

* GET: From Max, get the list of voices available to the browser.
* POST: Once all voices are loaded in the browser, send the list to the server, to be polled for in Max. This should happen only once per pageload.

## TODO

* Make distance ratios based on mileage in directions
* Make Maps requests from inside Max
* Figure out a good UI for this mess
* ~~Record to files~~
* Clear buffer between texts, load from files

Eventually:

* Make sure the browser-opener code works with this
* See if jython/py objects will play nice and run the server inside Max

Done: 

* ~~Start recording resulting speech~~
* ~~Notify Max of onstart/onend~~
* ~~Fix timestamp production in patch~~ (fixed itself?)
* ~~Send clicks with timestamp~~
* ~~Poll for clicks from inside browser~~
* ~~Start sending clicks!!~~
* ~~Add voice selection/detection~~
* ~~Get directions from server in Max - done!~~
* ~~Adjust database structure - Path table and Steps table - done!~~
* ~~Make umenu out of paths dict - done~~
* ~~Get steps based on path uuid - done~~