# performable-maps

## Python API "endpoints"

These are internal endpoints meant to interact with data saved in a Sqlite3 database. They aren't "true" endpoints because the server is implemented using SimpleHttpServer, and I felt better about taking the cheap route with query strings than trying to reinvent Flask. Interacting with Google Maps is a separate action, done in a browser window. All data is returned as JSON.

### ?type=paths

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

### ?type=steps&path-id=uuid

Steps are the individual instructions in a path.

**Variables**

* path_id: id of the step's parent path
* step_id: which step this is in the overall path
* text: direction text for this step, i.e. "Turn left at Main St"
* distance: distance traveled after this step

**Methods**

* GET: Gets all the steps of a given path based on the path's UUID.

### ?type=clicks

The Web Speech API is not accessible via jweb, Max's Chromium-based embedded browser. We have to trick an actual browser window (optimally, Chrome) into auto-triggering button presses by polling for "clicks" from the server, which are sent to the server by Max.

**Variables**

* click_id: id of this click
* step_id: the step that this click is attempting to trigger
* timestamp: when this click was sent
* checked: whether or not the browser has seen this click while longpolling

**Methods**

* GET: From the browser, check if there are any new clicks.
* POST: From Max, request that the browser play the next sound.

## TODO

Short-Term:

* ~~Get directions from server in Max - done!~~
* ~~Adjust database structure - Path table and Steps table - done!~~
* ~~Make umenu out of paths dict - done~~
* ~~Get steps based on path uuid - done~~
* Make distance ratios based on mileage in directions
* ~~Start sending clicks!!~~
* Add voice selection/detection

Goals:

* ~~Fix timestamp production in patch~~ (fixed itself?)
* ~~Send clicks with timestamp~~
* ~~Poll for clicks from inside browser~~
* Start recording resulting speech
* Figure out a good UI for this mess

## Issues

There isn't currently a way to send a Google Maps request from inside the patch. I guess I could use jweb, but then this starts to get a little ridiculous.

From the browser, Max needs:
* map generation
* voice selection
* notification of onstart, onend, pending?