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
