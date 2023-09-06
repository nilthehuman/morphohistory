# morphohistory

This is going to be a kind of simulator to account for the dispersion and
vacillation of various inflected word forms in the Hungarian language.

**morphohistory** is in *pre-alpha* stage. If anything works properly, thank your lucky stars.

This project is MIT Licensed.

## Installation

At the current experimental stage, **morphohistory** is not distributed as a regular package in
any standard package manager. Instead you are advised to download the source code of the application
directly from GitHub and run it from the downloaded folder. I apologize for the inconvenience.

### Dependencies

Both the necessary and the recommended optional software packages used by **morphohistory** are listed below.
Detailed steps on how to satisfy the only two strictly required dependencies (**Python** and **Kivy**) are
provided in the [Installation instructions](#installation-instructions) below.

| package       | version           | description                                            | required? |
|:--------------|:------------------|:-------------------------------------------------------|:----------|
| python        | 3.11.0 or newer   | the official Python interpreter to run the application | yes       |
| kivy          | 2.0.0 or newer    | GUI library providing graphics and event services      | yes       |
| mypy          | any (?)           | static analysis tool for type correctness              | no        |
| pylint        | any (?)           | static analysis tool for software best practices       | no        |
| pytest        | any (?)           | standard Python unit testing utility                   | no        |
| pydirectinput | any (?)           | automatic mouse and keyboard input in tests (extended) | no        |
| pyautogui     | any (?)           | automatic mouse and keyboard input in tests (fallback) | no        |
| simplerandom  | any (?)           | random numbers for nondeterminism                      | no        |

### Hardware requirements

The application is designed to be used primarily on desktop devices with dedicated keyboard
and mouse peripherals, but in principle it should also work on touchscreen devices
such as tablets (although such devices have not been tested). The hardware requirements are
fairly trivial by today's standards:

| resource          | requirement                 |
|:------------------|:----------------------------|
| CPU               | Intel Core i3 or equivalent | 
| RAM               | 500 MB                      |
| Screen resolution | 800x600 or higher           |

### Installation instructions

We need to download the application and install its dependencies. The following steps
should work on both Windows and Linux (sadly the author has yet to get the application
working on macOS).

1. Make sure you have a working Internet connection.

2. The application needs be run with **Python 3**. Open a terminal window (also known as
Command Prompt on most Windows systems) and type in the following command:
```commandline
python3 --version
```
If this does not seem to work, please fall back on the following:
```commandline
python --version
```
If you get a message like the following, then you already have **Python 3** installed and
you can proceed to step 3: :heavy_check_mark:
```commandline
Python 3.11.2
```
(The first two numbers need to be no less than 3 and 11, respectively; the last one does not
matter.)

If on the other hand you get an error or a message like this one where the minimum version
requirement is not met, you still need to install **Python 3**: :x:
```commandline
Python 2.7.16
```
Please refer to the official Python website to download and install the latest version of
**Python 3** on your system: https://www.python.org/downloads/

Please run the installer and follow the directions. If you are prompted by the installer to either
allow the Python executable to be added to your ```PATH``` environment variable or not, click
*allow*. When you are done, repeat step 2. This time you should see a version 3.11.x or higher
displayed in the terminal window.

3. The application further depends on the **Kivy** graphical user interface library which also
needs to be installed. Please issue the following command in the terminal window (substituting
```python3``` for ```python``` at the beginning if you found that worked in step 2):
```commandline
python -m pip install kivy[base] kivy_examples --pre --extra-index-url https://kivy.org/downloads/simple/
```
If that command fails for any reason, please try the following instead:
```commandline
python -m pip install kivy
```
If the command finishes without errors, the installation is complete.

4. The current version of the application's source code is available on the following
webpage: https://github.com/nilthehuman/morphohistory. Please click the green *Code* button
on the right side and choose *Download ZIP*.

5. Extract the downloaded .zip file. The application itself does not install to a predefined
directory, it is designed to be run directly from the folder extracted from the .zip file, so you
can extract it anywhere you like.

6. Again in the terminal window use the ```cd``` command to enter the folder extracted from the
.zip file (your exact folder may differ):
```commandline
cd Downloads/morphohistory-main
```

7. Issue the following command in the terminal to run the application (again substitute
```python3``` for ```python``` if that worked in step 2):
```commandline
python .
```

## Main features

Once the application is running, you should see four tabs in the horizontal tab strip at the top
of the window, with the first tab currently active. You can use the tabs to navigate between
the four different panels of the application, or switch between tabs via keyboard: ```Ctrl-Tab```
for "next tab" and ```Ctrl-Shift-Tab``` for "previous tab".

### The Simulation tab

The leftmost tab panel, the one active immediately on startup is where you can see the virtual
speech community (also called an *agora*) displayed in a schematic form: each round dot on
the screen corresponds to a virtual speaker, its color corresponding to its current preference
for [+back] or [−back] variants in the paradigm overall, and its position reveals how often it
is expected to interact with the other speakers (if the *Distance metric* setting is switched
to a value other than "constant").

Individual speakers can be dragged around the screen and the simulator will automatically
consider their new positions. A speaker can be removed from the speech community at any
time by right clicking on it. Hover over any speaker to see a tooltip with a summary of its
current biases and the extent of its experience.

On the right side you should be able to see a vertical strip of control buttons labeled
according to their function: the topmost one that says *Save this agora* is for exporting the
current state of the simulated speech community to file. The one below, *Load another agora*
lets you replace the current speech community with one you have previously exported to file.

The next one labeled *Start* (or *Stop* while the simulation is running) is for starting and
continuously applying the stochastic simulation algorithm using one of the available learning
models to the speech community displayed in the main area of this panel. You can set the learning
model of your choice on the *Settings* tab panel. The *Start* button runs the simulation at a
moderate pace so it can be observed while running. The simulation will proceed indefinitely and
it will be halted no sooner than the same button is pressed again.

Below this button we find a smaller button labeled "<<" (for "rewind") which serves to reset
the speech community to its initial state, and another by its side labeled ">>" (for "fast
forward") which runs the simulation at full speed ignoring the graphical display of the speech
community, which will only be updated once the simulation halts. The halting (or termination)
conditions can be found and adjusted on the *Settings* tab panel.

The slider control below can be used to change the simulation speed when the *Start* button is
used (the fast forward function ignores it). Finally, the total count of simulated iterations so
far can be seen at the bottom.

### The Settings tab

The second tab panel is where most of the application's user adjustable options can be
configured. The options are grouped into the following three sections.

Under the *Appearance* section you can find options to select the language of the user
interface and to control the graphical aspects of the main tab panel. *Color A* and *Color B* are
used to represent preference for the alternants that appear in the left and right columns of the
table on the *Paradigm* tab panel, respectively. The *broadcaster color* is used to show that a
particular speaker addresses all other speakers and cannot be spoken to, irrespective of its
bias values. To hide the interaction arrow when the simulation is running in real time, turn the
*Show interaction* option off.

The *Simulation* section offers controls for the model parameters, i.e. the specifics of how the
simulation will work in detail. The distance metric option stands for the concept used to
calculate the distances between each pair of speakers: possible values are "constant" (all
speakers are equally distant from all others), "Manhattan" (distance is calculated by adding
the differences between speakers' X and Y coordinates) and "Euclidean" (normal diagonal
distance). The available learning models are "harmonic" (monotonically decreasing Δbias
values) and two slightly different implementations of the "Rescorla–Wagner" model. A number of
binary switches follow whose operation is rather self-explanatory: *self influence* allows
speakers to perceive the forms they themselves produce, *mutual influence* guarantees
symmetric interactions between speakers, *passive decay* gradually suppresses the weaker
surface forms in all speakers, and *reverse preference* inverts all speakers' biases when
picking a form to be used in an interaction. *Starting experience* is the number of forms every
speaker is assumed to have encountered before the simulation is started.

Lastly the *Termination* section is where the conditions for halting a fast forward simulation
can be set: *bias threshold* is the aggregate preference for either A or B forms that all speakers
must reach before halting; the *experience threshold* is the total number of forms heard from
others or themselves that all speakers must reach before halting. Fast forwarding stops when
both criteria have been met or when the number of iterations specified in the *max iterations*
entry is reached.

To apply and save your current settings click the *Apply* button at the bottom of the screen. To
discard any unapplied settings changes and reset them to their previous values press the *Discard*
button instead.

### The Paradigm tab

The *Paradigm* panel serves to provide the concrete word forms the simulated speakers use to
interact with each other. Every pair of the table's input text fields represents a paradigm cell;
every cell may have two different forms, the same form in both text fields, or it may be left
empty. It is customary to put [+back] forms in the A column and [−back] forms in the B
column, but in practice it is up to the user's preference.

When the *Use a single cell only, okay? Thanks* checkbox is active, only the entries in the very
first cell are considered in the simulation; if it is inactive, the simulator uses all non-empty
cells. Prominence values (meant to reflect how common each cell is in usage) will affect the
random choice of a cell in every interaction, as well as the rate of bias update in the
Rescorla–Wagner learning model.

To commit the updated word forms and prominence values use the *Apply* button at the
bottom of the window. To reload the values currently set in the simulation, use the *Discard*
button.

### The Tuning tab

We may often wish to repeatedly run a simulation with a range of similar but slightly
different starting conditions and see how those conditions affect the overall outcome of the
simulation, such as which inflection pattern happens to become dominant (if any), or whether
the [+back] and [−back] patterns both keep being represented close to 50%. Doing all of this
by hand would require us to set every starting condition one by one, run every one of them
several times and keep a tally of the outcomes.

To automate this process, the final tab panel presents a selection of input parameters
controlling the initial state of the community that can be configured to step through a range of
values successively, producing every possible combination of them. The simulation is then
repeated a given number of times for each one of the possible parameter combinations.

The user should first pick a parametrizable simulated community out of the templates
supplied in the top row (some of which are identical to the communities found in the .agr
files under the ```examples``` folder). When a template is selected, it will immediately appear
on the *Simulation* panel as prescribed by its default parameters. The desired value ranges of
the available parameters can be specified in the table below: every row has an input field for
the parameter's first value, last value and the step to increase or decrease the value by in
each iteration. The terms "our bias" and "their bias" are used just for mnemonic purposes,
they simply represent the biases of one "camp" in the simulated speech community versus the
other. The inner radius parameter controls the size of the smaller ring of speakers if a
template with rings has been selected. Please note that no other model parameters are
available in the tuning feature at this time, more they will be probably be added at a later
point. For the rest of the parameters the values set on the *Settings* tab panel apply.

Finally the user may specify the amount of repeated simulations to be performed from the
same starting conditions. The default amount of 100 is both performed relatively quickly and
is practical because it translates directly to percentages.

When the *Go* button is pressed the repeated simulations start and a small popup window 
appears showing a progress bar that tracks the number of parameter configurations already 
tested. The output is written to a text file in Comma-Separated Values format in the 
application's directory where each line shows the aggregate outcomes from one specific 
parameter configuration, in the following order:

| our bias | their bias | starting experience | inner radius |  number of simulation runs where form A became dominant | number of simulation runs where form B became dominant | number of simulation runs where neither became dominant | number of simulation runs where both stayed roughly equally relevant |
|:---------|:-----------|:--------------------|:-------------|:--------------------------------------------------------|:-------------------------------------------------------|:--------------------------------------------------------|:---------------------------------------------------------------------|

The output file should contain as many lines as there are possible parameter combinations, 
unless the user cancels the tuning process.

## Troubleshooting common issues

As the application is still under development, users may experience unexpected or unstable
behaviour at any time. A few typical problems and the recommended checks and actions to fix
them are listed below.

**Problem.** The simulation on the main tab seems to be doing nothing. I've clicked the *Start*
button but nothing happened.  
**Solution.** If you're using the "harmonic" learning model, please check if the starting
experience setting is too high on the *Settings* tab. If on the other hand you're using the
Rescorla−Wagner model, check the *Paradigm* tab to see if the prominence values look okay;
in particular, make sure to have at least one pair of variants that are different and have a
positive prominence. Especially if you're using a single-cell paradigm, that cell needs to have
two different word forms, otherwise there is no way for the speakers to influence each other
during the simulation.

**Problem.** The simulation seems stuck. I've clicked the fast forward (">>") button but
nothing happened.  
**Solution.** When the termination criteria (as specified on the *Settings* tab) have already
been met, the fast forward function will stop immediately. Please adjust the termination criteria
or use the *Start* button above to keep running the simulation beyond that point.

**Problem.** The graphics on the main tab seem to be broken: the tooltip supposed to be shown
hovering over the speaker appears way off.  
**Solution.** Please check your display settings and try using the defaults exclusively. If you
use Windows, navigate to the *Display settings* section, and under *Scale and layout* make sure
the *Change the size of text, apps and other items* option is set to 100%.

**Problem.** I can't find an option to edit the biases of individual speakers.  
**Solution.** Unfortunately there is no support for adjusting the biases from within the
application at this time. However the .agr files containing the latest state of a speech
community are written and formatted in human-readable JavaScript Object Notation and can
be opened and changed manually in any text editor. Look for the ```bias_a``` variable to set a
certain speaker's bias associated with form A (the left one in the table on the *Paradigm*
tab panel) in a particular cell.

**Problem.** I can't find an option to turn a regular speaker into a broadcaster.  
**Solution.** As in the Problem immediately above, there is currently no such option in the
application. Editing the .agr file that defines your speech community by hand and loading it
in the application is the only way right now. A speaker can be made into a broadcaster by
changing the value associated with its ```is_broadcaster``` variable from ```false``` to
```true```.

**Problem.** My settings are not saved when I click *Apply* on the second tab panel.  
**Solution.** You may have placed the application folder in a system directory that you don't
have write permissions for. Please move the application folder to a different directory, such
as your user directory.

**Problem.** My settings are not loaded at all on startup.  
**Solution.** You may have moved, deleted or renamed the user_settings.ini file in the
application's root folder. Please make sure the file is there under that exact filename.

**Problem.** One of my settings is not loaded correctly, instead it resets to the default value.  
**Solution.** Invalid values might appear in the user_settings.ini file on the right side of
an equals sign, especially if the file has been edited manually, which is discouraged. Please
rely on the application to save your preferences automatically when *Apply* is clicked on the
*Settings* tab panel. Note that the settings file is sensitive to formatting as well and even
just some extra whitespace might prevent your settings from being loaded correctly.

**Problem.** I don't seem to be able to set an arbitrary bias threshold, experience threshold or
max iterations.  
**Solution.** Those settings are constrained to a range of meaningful values by design. The
maximum number of iterations using the fast forward function is further limited to between
10^2 and 10^20.

## Bug reports and feedback

If you find any sort of bugs, errors or odd behaviours in the program that keep bothering you,
or have a cool idea for a new feature, please consider filing an issue
[on the official GitHub page](https://github.com/nilthehuman/morphohistory/issues) 
or letting the maintainer know by email: my contacts are found on
[the official webpage of the Hungarian Research Centre for Linguistics](https://nytud.hu/en/colleague/daniel-arato/profile).
And if you mysteriously enjoy using the application in its incomplete state on the other hand,
I would be most delighted to hear about that too.