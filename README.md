# prior_PureFocus850
Python device adaptor: Prior PureFocus850 Laser Autofocus System.
## Quick start:
There isn't one -> you have the read the manual, but here's the basic steps:
- Get the autofocus 'Head' installed behind the primary objective with the IR laser/dichroic facing the objective BFP.
- Connect everything up, including the 'Controller' USB to the PC, and the analog out cable (PF404) to the focus piezo (which needs a 0-10v analog input).
- Get the SDK from https://www.prior.com/download-category/software (PF850) (a version included here).
- The USB driver seems to be generic FTDI and should auto install on Windows.
- Run the GUI 'PureFocus850.exe' to test communication and start setting up.
- Now follow the manual 'Pure-Focus-850_EN_UK_Manual.pdf' (a version included here) to align the head to the optical axis of the microscope (1 time setup), and then configure for each objective/sample combination (regular setup, configurations can be saved).
- Finally start testing 'prior_PureFocus850.py' and 'prior_PureFocus850_test_example.py'
## Details:
- The document 'PureFocus850-Datasheet.pdf' is good for mechanical integration, dichroic transmission and part# info (a version included here).
- The document 'PureFocus-Software-Guide.pdf' is good for quickly navigating the GUI (a version included here).
- The device adaptor 'prior_PureFocus850.py' reveals just enough of the API to check/set the controller configuration, setup the piezo range and voltage, toggle the autofocus servo and 'digipot' mode (user convenience) and return a 'focus flag' (i.e. whether the controller thinks it's in focus or not).
- The example script 'prior_PureFocus850_test_example.py' shows how to use the autofocus in practice, with initialization, how to get a clean handover of piezo voltage back and forth between servo and user control mode (i.e. without jumps in focus) and how to check the 'focus flag' (good for user feedback when running the autofocus servo).
- The 'alignment' folder shows some example images of what the alignment can look like.
- The 'objectives' folder stores the config files for the system and different objectives. For example 'OBJ1 -Nikon40x0.95air-.txt' has a config for the said objective that seems to work well in practice (i.e. the autofocus stays reliably locked when scanning quickly over large, purposefully tilted samples, including large microfluidic samples with complex PDMS and water layers above the coverslip).
## Setup tips:
- Make sure to check that the servo direction is correct or it will run away instead of locking (SERVODIR,1 (or -1) in the SYSTEM.txt config file).
- **Good performance mostly depends on the quality of the feedback signal -> check this regularly using the GUI when switching objectives/samples.**
- The feedback signal is strongly dependent on the alignment to the current objective/sample and may need adjustment (in particular the '45 Deg' screw).
- Different objectives may benefit from different PID and laser power values (in particular KP, KI and LASER in the objective config file).
- Sample reflections can definitely upset the servo. Adjust the 'pinhole' center and width to cut out unwanted signals if needed (e.g. set PINHOLE,750,100 to reject anything more than 100 pixels away from 750).
- The 'offset' lens will need adjusting between different objectives. For user convenience it's best to set a good default position for a particular objective/sample combination and record this in the objective config file (e.g. LENSSO,1,23756). If the sample changes it may not be optimal anymore...
- The 'sample' and 'focus' flags may need adjusting on a per sample basis. To avoid this keep the margins wide on the thresholds and don't overly rely on them.

**Note:** The alignment from the **'45 Deg' screw** may drift or need tweaking between different samples/objectives.
