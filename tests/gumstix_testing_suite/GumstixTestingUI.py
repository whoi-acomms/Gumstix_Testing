# $Id$

from Tkinter import *
from ttk import *
import sys
import os
import shutil
import tkFileDialog
import tkMessageBox
import subprocess as sp
import multiprocessing as mp
from threading import Thread
from Queue import Queue, Empty
from time import sleep


#Just a container to hold information specific to each Test
class TestFile():
    def __init__(self, filename, tag, dep_list, wasrun, will_be_run, passed, results):
        #name of the test file
        self.filename = filename
        #Priority tag (i.e. 00a)
        self.tag = tag
        #list of dependencies (by tag, 00a, 00b, etc)
        self.dep_list = dep_list
        #did the test pass (bool)
        self.passed = passed
        #was the test run (bool)
        self.wasrun = wasrun
        #should the test be run (int 0 or 1)
        self.will_be_run = will_be_run
        #string of test output
        self.results = results


#A class found on the web, conveniently allows scrolling a list of widgets
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

#This is run in a thread to read and put lines of output in subprocesses into a queue
def enqueue_output(out, queue):
    #block waiting for lines of output, an empty line signals the process ended
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

#This is the func targeted by the process that runs the tests. The real work is done here
def run_tests(tests, running, q_out, dir_name):
    q_out.put('Starting Tests...\n')
    #get the list of tests by priority tag
    testlist = tests.keys()
    #put the priority tags in lexicographic order (this will place higher priorities first)
    testlist.sort()

    #iterate over each test
    runcount = 0
    passcount = 0
    for filetag in testlist:
        #if termination signal received, exit loop
        if not running.value:
            break
        #get the individual test at each iteration rather than all at once and then iterating to avoid desynching the dict
        test = tests[filetag]
        q_out.put('**TEST %s***\n' % test.filename)
        runtest = True
        #check the dependencies have been run and passed
        for dep in test.dep_list:
            if not tests[dep].passed:
                runtest = False
                q_out.put('Dependency %s for test %s not met, '
                          'ignoring test...\n' % (dep, test.filename))
                break
        #skip test if deps not met or if this test is not marked for execution
        if not runtest or not test.will_be_run:
            continue

        runcount += 1

        #build the full path to the file
        filepath = os.path.join(dir_name, test.filename)
        q_out.put('Running test file %s...\n' % test.filename)
        test.passed = False
        tests[test.tag] = test
        #Spawn a child process to execute the file with python *insert child labor joke*
        cmd = [sys.executable, filepath]
        testrunner = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, bufsize=1)

        #start a queue and thread to read and add to queue lines of output from the subproc
        q = Queue()
        t = Thread(target=enqueue_output, args=(testrunner.stdout, q))
        t.daemon = True
        t.start()

        #initialize test.results so it can be appended in the loop
        test.results = ''

        #while the termination signal has not been given and the process hasn't completed
        while running.value and testrunner.poll() is None:
            try:
                #get a line of output
                line = q.get_nowait()
            except Empty:
                continue
            #append new output read to the results attribute
            #and add to the stdout Queue between this proc and the parent TKinter proc
            q_out.put(line)
            test.results += line
            #Passed
            if line == 'PASSED\n':
                passcount += 1
                test.passed = True
                test.wasrun = True
                break
            #Failed
            elif line == 'FAILED\n':
                test.passed = False
                test.wasrun = True
                break

        #if the test finished, print all output still in the queue
        if testrunner.poll() is not None:
            while not q.empty():
                line = q.get()
                q_out.put(line)
                test.results += line
                if line == 'PASSED\n':
                    passcount += 1
                    test.passed = True
                elif line == 'FAILED\n':
                    test.passed = False
            test.wasrun = True
        #IMPORTANT STEP, set the proc-safe dict to point to our local test object
        tests[test.tag] = test
    #tests done
    running.value = 0
    q_out.put('Testing finished.\n')
    q_out.put('%i passed out of %i tests run\n' % (passcount, runcount))

#The GUI itself
class TestingUI(Tk):

    def log_queue(self):
        try:
            #pull a line from the queue and print it
            line = self.queue.get_nowait()
            self.write_to_log(line)
        except Empty:
            pass
        #if there is a test running or the queue isn't empty yet, call this again until both conditions are met
        if self.running.value or not self.queue.empty():
            self.after_idle(lambda: self.after(0, self.log_queue))
        #Refresh test listing only if a test has been updated
        testlist = self.test_files_dict.keys()
        testlist.sort()
        refresh = False
        for ind, key in enumerate(testlist):
            runbool = self.test_files_dict[key].wasrun
            if len(self.oldrunlist) == len(testlist):
                if self.oldrunlist[ind] != runbool:
                    refresh = True
                    self.oldrunlist[ind] = runbool
            else:
                self.oldrunlist.append(runbool)
                refresh = True
        if refresh:
            self.after_idle(lambda: self.after(0, self.refresh_test_list))

    #Writes the message into the log file
    def write_to_log(self, message):
        #write this to logfile
        self.logfile.write(message)
        #append onto the console box text
        self.console_text.append(message)
        #redefine the text list to only the final [line_max] number of lines
        if len(self.console_text) > self.console_line_max:
            self.console_text = self.console_text[-self.console_line_max:]
        #concatenate all the lines in the list together
        display_text = ''
        for line in self.console_text:
            display_text += line
        #resize the console_box to the size of the text
        self.console_box.configure(height=len(self.console_text))
        #delete the old content
        self.console_box.delete(1.0, END)
        #add the new content
        self.console_box.insert(END, display_text)

    def select_all(self):
        #set all checkboxes to the value of the selectall box
        for i in xrange(len(self.checkbuttons)):
            if not self.checkvars[i].get() == self.selectall_var.get():
                self.checkbuttons[i].invoke()

    #toggles the .run attr of Test File, this method is for checkboxes
    def toggle_test(self, var, test):
        #if a test is running, reset the value change
        if self.running.value:
            if var.get():
                var.set(0)
            else:
                var.set(1)
            tkMessageBox.showwarning('Running Test', 'There is a test running, please wait for it to '
                                                     'finish or stop the test before trying again.')
        #no test running
        else:
            #toggle the run value
            tfile = self.test_files_dict[test]
            tfile.will_be_run = var.get()
            self.test_files_dict[test] = tfile
            #if this was turned on, turn on its dependencies
            if var.get():
                for tag in tfile.dep_list:
                    if (not self.test_files_dict[tag].will_be_run == var.get()) and not self.test_files_dict[tag].passed:
                        self.checkdict[tag].invoke()
            #if this was turned off, turn off its dependents
            else:
                #important to assign TestFiles at each iteration, not all before or you end up
                #with desynched recursive calls
                keys = self.test_files_dict.keys()
                for key in keys:
                    testfile = self.test_files_dict[key]
                    if (test in testfile.dep_list) and ((testfile.will_be_run != var.get()) and not self.test_files_dict[test].passed):
                        self.checkdict[testfile.tag].invoke()

    #Starts a new test process
    def start_command(self):
        #check that there are tests to run
        if not self.test_files_dict:
            tkMessageBox.showwarning('No Test Directory', 'There is no test directory selected, please select '
                                                          'a directory before trying again.')
        #check a test is not already running
        elif self.running.value:
            tkMessageBox.showwarning('Running Test', 'There is a test running, please wait for it to '
                                                     'finish or stop the test before trying again.')
        else:
            self.write_to_log('Starting...\n')
            self.running.value = 1
            #reset tests that are about to be run
            testlist = self.test_files_dict.keys()
            testlist.sort()
            for tag in testlist:
                test = self.test_files_dict[tag]
                if test.will_be_run:
                    test.wasrun = False
                    test.passed = False
                    self.test_files_dict[tag] = test
            #start a process running to execute all tests
            self.proc = mp.Process(target=run_tests, args=(self.test_files_dict, self.running,
                                                           self.queue, self.directory_name))
            self.proc.start()
            #update the log to get realtime output
            self.after_idle(self.log_queue)
            #update the test list to show intermediary results
            self.after_idle(self.refresh_test_list)

    #Stops the current test process
    def stop_command(self):
        if self.running.value:
            #set signal to terminate
            self.running.value = 0
            self.write_to_log('Stopping tests...\n')
            #wait for the proc to die on its own, without blocking
            while self.proc.is_alive():
                sleep(.5)
            self.write_to_log('Done\n')
        else:
            tkMessageBox.showwarning('No Test Running', 'There is not a test running right now.')

    #Prints the results of the given test
    def print_results(self, test):
        #Create a new popup windows with a scrollable frame of test results
        self.top = Toplevel(self)
        self.top.title('Results for %s' % test.filename)
        self.scroll_results = VerticalScrolledFrame(self.top)
        self.scroll_results.pack(fill=BOTH, expand=1)
        header = '\n****RESULTS FOR TEST %s****\n' % test.filename
        #generate the results text from the Dict of Test Files
        self.result_text = Text(self.scroll_results.interior)
        self.result_text.insert(END, header + self.test_files_dict[test.tag].results.decode('utf-8'))
        self.result_text.tag_add('ResultHighlight', 'end -2 lines', 'end')
        #Check if test passed or failed to color the PASSED/FAILED final line
        if self.test_files_dict[test.tag].passed:
            self.result_text.tag_config('ResultHighlight', foreground='green')
        else:
            self.result_text.tag_config('ResultHighlight', foreground='red')
        self.result_text.pack(fill=BOTH, expand=1)


    #Query for a directory and initialize TestFile containers from valid test files in the directory
    def askdirectory(self):
        if self.running.value:
            tkMessageBox.showwarning('Running Test', 'There is a test running, please wait for it to '
                                                     'finish or stop the test before trying again.')
            return
        #get dir name
        self.directory_name = tkFileDialog.askdirectory(mustexist=True)
        self.directory_var.set(self.directory_name)

        filenames = []
        #get only toplevel file names
        for (dirpath, dirnames, fnames) in os.walk(self.directory_name):
            filenames.extend(fnames)
            break

        #iterate over these filenames
        for filename in filenames:
            #check for priority tag prefix
            if not filename[:2].isdigit() or not filename[2].isalpha() or not filename[3] == '_':
                self.write_to_log('\'' + filename + '\' does not have a valid priority tag.\nSee README for'
                                  ' more information about filenames.\n')
                continue
            try:
                #open the file
                file = open(os.path.join(self.directory_name, filename), 'r')
                line = file.readline()
                #read the dependencies list on the first line
                if not line[:14] == '#dependencies=':
                    self.write_to_log('Dependencies list missing from \'' + filename + '\'. Ignoring...\n')
                    continue
                #parse the dependencies list (surrounded by quotes, delimited by commas)
                deplist = line[14:].split("\"")
                deps = deplist[1].split(',')
                if deps[0] == '':
                    deps = []
                #build a TestFile and put it in the dict of test files, key= priority tag
                self.test_files_dict[filename[:3]] = TestFile(filename, filename[:3], deps, False, 0, False,
                                                            'Test ' + filename[:3] + ' has not been run yet.')
                file.close()
            except IOError:
                self.write_to_log("Could not open \'" + filename + "\'. Ignoring...\n")
                continue
        self.refresh_test_list()

    #Refresh the list of test files widgets from the dict of Test Files
    def refresh_test_list(self):
        rownum=1
        testlist = self.test_files_dict.keys()
        testlist.sort()
        #Remove the old widgets from the grid
        for widg in self.checkbuttons:
            Grid.forget(widg)
        for widg in self.filenames:
            Grid.forget(widg)
        for widg in self.dependencies:
            Grid.forget(widg)
        for widg in self.results:
            Grid.forget(widg)
        for widg in self.view_results:
            Grid.forget(widg)
        #Remove them from their lists as well
        self.checkdict.clear()
        del self.checkbuttons[:]
        del self.checkvars[:]
        del self.filenames[:]
        del self.dependencies[:]
        del self.result_strings[:]
        del self.results[:]
        del self.view_results[:]

        #Build a row of widgets for each test file
        for test in testlist:
            tf = self.test_files_dict[test]
            Grid.rowconfigure(self.file_frame.interior, rownum, weight=1)

            #checkboxes
            self.checkvars.append(IntVar(value=tf.will_be_run))
            self.checkbuttons.append(Checkbutton(self.file_frame.interior, variable=self.checkvars[-1],
                                                 command=lambda tag=tf.tag, var=self.checkvars[-1]:
                                                 self.toggle_test(var, tag)))
            self.checkdict[test] = self.checkbuttons[-1]
            self.checkbuttons[-1].grid(row=rownum, sticky=N+S+E+W)
            #filename Message
            self.filenames.append(Message(self.file_frame.interior, bg='white', text=tf.filename,
                                          highlightbackground='black', highlightthickness=1))
            self.filenames[-1].bind('<Configure>', lambda e: self.filenames[-1].configure(width=e.width-2))
            self.filenames[-1].grid(row=rownum, column=1, sticky=N + S + E + W)
            #Dependency list Message
            self.dependencies.append(Message(self.file_frame.interior, text=tf.dep_list,
                                             bg='white', highlightbackground='black',
                                             highlightthickness=1))
            self.dependencies[-1].bind('<Configure>', lambda e: self.dependencies[-1].configure(width=e.width-2))
            self.dependencies[-1].grid(row=rownum, column=2, sticky=N + S + E + W)
            #Only build these widgets if the test has been run already
            if tf.wasrun:
                #Result Message StringVars
                self.result_strings.append(StringVar())
                if tf.passed:
                    self.result_strings[-1].set("PASS")
                    color = 'green'
                else:
                    self.result_strings[-1].set("FAIL")
                    color = 'red'
                #Result Message
                self.results.append(Message(self.file_frame.interior, textvariable=self.result_strings[-1],
                                            fg=color, bg='white', highlightbackground='black',
                                            highlightthickness=1))
                self.results[-1].grid(row=rownum, column=3, sticky=N + S + E + W)
                #View Results Buttons
                self.view_results.append(Button(self.file_frame.interior,
                                                text='View Output',
                                                command=lambda tf=tf: self.print_results(tf)))
                self.view_results[-1].grid(row=rownum, column=4, sticky=N + S + E + W)
            rownum += 1

    #Override destroy method to query for saving log file on quit
    #And to kill the xterm window
    def destroy(self):
        #check if a test is running
        if self.running.value:
            if tkMessageBox.askokcancel('Running Test', 'There is a test running. Stop test and quit?'):
                self.stop_command()
            else:
                return
        try:
            #Query to save logfile
            val = tkMessageBox.askyesnocancel('Save', 'Do you want to save the log file for this session?')
            #cancel
            if val is None:
                return
            #yes
            elif val:
                #copy logfile to the file given by the saveas dialog
                filename = tkFileDialog.asksaveasfilename(defaultextension='.txt')
                logfile = os.path.join(os.getcwd(), filename)
                shutil.copy('stdout.txt', logfile)
            #simply close and destroy the logfile
            #On windows, os.remove will fail due to a file lock from a subprocess
            #that I haven't been able to track down
            self.logfile.close()
            os.remove('stdout.txt')
            if self.proc and self.proc.is_alive():
                self.proc.terminate()
            self.quit()
        except:
            if self.proc and self.proc.is_alive():
                self.proc.terminate()
            self.quit()

    def __init__(self, *args, **kwargs):
        self.proc = None
        #open the logfile
        self.logfile = open('stdout.txt', 'w+')

        #create the root
        root = Tk.__init__(self, *args, **kwargs)

        #instantiate the test files dict and stdout queue (shared state in processes)
        self.manager = mp.Manager()
        self.queue = mp.Queue()
        manager_dict = self.manager.dict()
        self.test_files_dict = manager_dict

        #create a list to hold the old value of test.run for each testfile.
        # This is used to check if refresh_test_list needs to execute or not
        self.oldrunlist = []

        #instantiate the thread-safe value that signals running or not (0-false, 1-true)
        self.running = mp.Value('i', 0)

        #give weight to grid cells so they resize
        Grid.rowconfigure(self, 0, weight=1)
        for x in range(2):
            Grid.columnconfigure(self, x, weight=1)

        #set up the test file selection scrollframe
        self.file_frame = VerticalScrolledFrame(root)
        self.file_frame.grid(row=0, column=1, sticky=N+S+E+W)

        #dict mapping test tag to corresponding checkbutton for recursive toggling of dependent tests
        self.checkdict = {}

        #lists for all widgets in the test file selection scrollframe
        self.checkvars = []
        self.checkbuttons = []
        self.filenames = []
        self.dependencies = []
        self.result_strings = []
        self.results = []
        self.view_results = []

        #checkbox select all
        self.selectall_var = IntVar()
        self.selectall = Checkbutton(self.file_frame.interior, text='Select all', variable=self.selectall_var,
                                     command=self.select_all)
        self.selectall.grid(row=0, sticky=N+S+E+W)

        #again, weight the grid cells
        for x in range(5):
            Grid.columnconfigure(self.file_frame.interior, x, weight=1)
        Grid.rowconfigure(self.file_frame.interior, 0, weight=1)

        #Create headers for the list of test files and bind them to resize
        #filename header
        self.filename_header = Message(self.file_frame.interior, bg='white', text='Test File',
                                       highlightbackground='black', highlightthickness=1)
        self.filename_header.bind('<Configure>', lambda e: self.filename_header.configure(width=e.width-2))
        self.filename_header.grid(row=0, column=1, sticky=N + S + E + W)
        #Dependency list header
        self.dependencies_header = Message(self.file_frame.interior, bg='white', text='Dependencies',
                                           highlightbackground='black',
                                           highlightthickness=1)
        self.dependencies_header.bind('<Configure>', lambda e: self.dependencies_header.configure(width=e.width-2))
        self.dependencies_header.grid(row=0, column=2, sticky=N + S + E + W)
        #Result header
        self.result_header = Message(self.file_frame.interior, text='Result', bg='white',
                                     highlightbackground='black',
                                     highlightthickness=1)
        self.result_header.bind('<Configure>', lambda e: self.result_header.configure(width=e.width-2))
        self.result_header.grid(row=0, column=3, sticky=N+S+E+W)
        #View Results header
        self.view_results_header = Message(self.file_frame.interior, bg='white', text='Output',
                                           highlightbackground='black',
                                           highlightthickness=1)
        self.view_results_header.bind('<Configure>', lambda e: self.view_results_header.configure(width=e.width-2))
        self.view_results_header.grid(row=0, column=4, sticky=N+S+E+W)

        #set up the left half frame
        self.left_frame = Frame(root)
        self.left_frame.grid(row=0, column=0, sticky=N + S + E + W)

        #Weight the cells so they expand
        Grid.columnconfigure(self.left_frame, 0, weight=1)
        for x in range(2):
            Grid.rowconfigure(self.left_frame, x, weight=1)

        #Set up inframe console
        self.termf = VerticalScrolledFrame(self.left_frame)
        self.termf.grid(row=1, sticky=N+S+E+W)
        self.termf.vscrollbar.set(0,1)
        self.console_text = []
        self.console_line_max = 64
        self.console_box = Text(self.termf.interior)
        self.console_box.pack(fill=BOTH, expand=1)

        #set up the frame for the dir browse and start/stop buttons
        self.button_frame = Frame(self.left_frame)
        self.button_frame.grid(row=0, sticky=N + S + E + W)

        #Weight the cells so they expand
        for x in range(2):
            Grid.columnconfigure(self.button_frame, x, weight=1)
        for y in range(2):
            Grid.rowconfigure(self.button_frame, y, weight=1)

        #set up the file browser button and text box
        self.browser = Button(self.button_frame, text="Browse", command=self.askdirectory)
        self.browser.grid(row=0, column=0, sticky=E)
        self.directory_var=StringVar()
        self.directory = Entry(self.button_frame, textvariable=self.directory_var)
        self.directory_var.set('Select a directory...')
        self.directory.grid(row=0, column=1, sticky=W, columnspan=1)

        #set up start and stop buttons
        Style().configure('green.TButton', foreground='green')
        Style().configure('red.TButton', foreground='red')
        self.start = Button(self.button_frame, style='green.TButton', text="Start", command=self.start_command)
        self.start.grid(row=1, column=0)
        self.stop = Button(self.button_frame, style='red.TButton', text="Stop", command=self.stop_command)
        self.stop.grid(row=1, column=1)

if __name__ == "__main__":
    app = TestingUI()
    app.mainloop()
