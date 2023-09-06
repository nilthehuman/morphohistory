# Known issues and bugs:
* When FF is hit but the termination conditions already met, keep popup window open to explain the situation to the user
* Load core.agr, remove top left speaker, hit Reset -> biases shift
* Bugfix: looks like the progress bar graphic starts out in the negative range or something
* Fix crash when one speaker alone is simulated
* Pressing return/enter in popups should be equivalent to clicking confirm button
* Use a single global NameTag for all SpeakerDots

# Housekeeping and maintenance
* Make smoke tests work on both Linux and Windows
* Add GitHub Action to install and run tests after every push
* Write smoke tests for saving/loading
* Regression tests to ensure that base class objects and derived GUI objects are Liskov substitutable
* Basic performance tests

# Development tasks:
* Implement convolution-based learning model
* Figure out pylint license compatibility issue (GPL vs MIT)
* Duplicate same Confirm/Discard user logic on Tuning tab as on the other tabs?
* Upon double click show the speaker's bias in all paradigm cells
* Show unusual settings on special warning label in the agora's bottom right corner
* Undo/redo stack
* Allow iteration total to be shown as reasonably calculated "elapsed time", more intuitive
* Allow non-complete-graph speaker communities
* Increase dot size logarithmically to reflect experience (make this optional)
* Multithreading for performance
* If the app is about to be closed without saving, ask the user to save or discard changes
* Keep SpeakerDots inside their AgoraWidget
* Gently snap SpeakerDots to grid when dragging
* Speaker weight to account for social influence
* Speaker labels to differentiate age cohorts, social groups etc.
* Extend simulation to verb paradigms
* Speakers should be mortal and new ones should be born
* Creative on-line form production: sum of biases in a cell may be less than one, rely on surface analogy with other lexemes to produce "missing" form
