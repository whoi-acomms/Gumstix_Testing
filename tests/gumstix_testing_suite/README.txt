Gumstix Testing GUI - August 2013

Runs on standard python libraries (Tkinter for the GUI components). Simply run the 'GumstixTestingUI' script to bring up the GUI. 

Use the browse functionality to select a directory of test files to run. These files must adhere to a few formatting conventions or they will be ignored and not executed.

Test File conventions:
	
	-- Priority Tag Prefix --
		Valid test file names must be prefixed with 4 characters of the format ##X_ where # represents a digit and X a letter (i.e. "00a_test.py"). This is a priority tag meant to order the files and keep track of dependencies between files.

	-- Dependencies List --
		The first line of every test file must be of the form #dependencies="00a,00b,01a" where the comma seperated values are the priority tags of files that must be run and passed before this test is run.

	-- PASSED/FAILED --
		Every test file is expected to print either 'PASSED' or 'FAILED' at the end of the test accordingly (without the quotes, just the text).