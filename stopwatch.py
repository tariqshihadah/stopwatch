"""
===============================================================================

Developed by Tariq Shihadah
tariq.shihadah@gmail.com

10/08/2018

===============================================================================
"""


################
# DEPENDENCIES #
################


import time
from statistics import mean, median, stdev
from tarpy.util.general import chunkit, infinite_count


#############
# STOPWATCH #
#############


class Stopwatch(object):
    """
    A functional, stopwatch-like tool with the ability to report time passed 
    and lap times in terms of seconds or hours:minutes:seconds using a default 
    or a given reporting format. The stopwatch can also report basic  
    statistics on lap times, such as min, max, mean, median, and standard
    deviation, as well as supervise timed loops, periodic time reporting, and
    more.
    
    Parameters
    ----------
    :start:     `boolean, default True`
                whether to start the stopwatch upon initialization
    :numeric:   `boolean, default False` whether to default to reporting time 
                values numerically or with a formatted string
    :hms:       `boolean, default True` whether to default to reporting time 
                values in terms of hours, minutes, and seconds (returned as a 
                list if numeric is True)
    :form:      `string, default None`
                a formatting string to use when reporting time values as a 
                formatted string
    :process:   `func, default None`
                a function to process raw results of seconds for reporting 
                purposes (supersedes numeric, hms, and form parameters)
    :resource:  `{'perf_counter', 'monotonic', 'process_time', 'time'},
                default 'perf_counter'`
                which function from the `time` module to use to perform timing 
                operations
    
    Methods
    -------
    :laps:      returns a list of lap times for all completed laps
    :check:     returns the total elapsed time on the stopwatch
    :lap:       returns the total elapsed time for the current lap and begins
                a new lap
    :check_after: returns the total elapsed time on the stopwatch after a
                  specified number of function calls
    :lap_after: returns the total elapsed time for the current lap and begins
                a new lap after a specified number of function calls
    :pause:     pauses the stopwatch
    :start:     resumes the stopwatch
    :reset:     resets the stopwatch
    :hit:       increase the number of hits on the stopwatch by one or a
                specified number
    :reset_hits: reset the number of hits on the stopwatch to zero
    :lastlap:   returns the lap time of the most recently logged lap
    :maxlap:    returns the lap time of the longest lap
    :minlap:    returns the lap time of the shortest lap
    :meanlap:   returns the mean of all lap times
    :medianlap: returns the median of all lap times
    :stdevlap:  returns the standard deviation of all lap times
    :func_timer: function wrapper which logs each call of the function as a
                 lap
    :loop_timer: creates an iterable which logs each chunk of iterations as a
                 lap and can report each chunk's operation time
    :timed_loop: iterate the given iterable for a fixed amount of time before 
                 cutting it off
    :now:       report current time in datetime format
    :report:    report active time passed along with a text message
    :report_now: report current time along with a text message
    
    Properties
    ----------
    :active:    returns a boolean indicating whether the stop watch is active
                (True) or paused (False)
    :inactive:  returns a boolean indicating whether the stop watch is paused
                (True) or active (False)
    :resource:  returns the selected `time` module function being used to
                perform timing operations
    :hits:      returns the number of hits on the stopwatch
    """
    def __init__(self, start=True, numeric=False, hms=True, form=None, 
                 process=None, resource='perf_counter'):
        # Get timing resource
        try:
            self._resource = getattr(time, resource)
        except AttributeError:
            raise AttributeError("""Please select a timing resource from the \
list of default options: {'perf_counter', 'monotonic', 'process_time', \
'time'}.""")
        # Initialize attributes
        self.reset(start=start)
        # Set default time reporting format
        self.numeric = numeric
        self.hms = hms
        self.process = process
        if hms:
            if form is None:
                self.form = "{0:.0f}:{1:02.0f}:{2:05.2f}"
            else:
                self.form = form
        else:
            if form is None:
                self.form = "{0:.2f}"
            else:
                self.form = form
                
    def __str__(self):
        return str(self.check(numeric=False))
    
    @property
    def resource(self):
        return self._resource
    
    @property
    def _time(self):
        if self._pause:
            return self._pause
        else:
            return self._resource()
        
    @property
    def active(self):
        return not bool(self._pause)
    
    @property
    def inactive(self):
        return bool(self._pause)
    
    @property
    def hits(self, **kwargs):
        return self._hits
    
    def laps(self, **kwargs):
        return [self._report(lap, **kwargs) for lap in self._laps]
    
    def stats(self, **kwargs):
        """
        Print the statistics of all logged laps.
        """
        print("""\
Lap Statistics
--------------
Count:  {} laps
Range:  {} - {}
Median: {}
Mean:   {}
Stdev.: {}
--------------
""".format(len(self._laps), self.minlap(), self.maxlap(), self.medianlap(),
           self.meanlap(), self.stdevlap()))
    
    def lastlap(self, **kwargs):
        """
        Return the last logged lap length.
    
        Returns
        -------
        a report of the maximum of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = self._laps[-1]
        return self._report(val, **kwargs)
    
    def maxlap(self, **kwargs):
        """
        Return the maximum lap length.
    
        Returns
        -------
        a report of the maximum of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = max(self._laps)
        return self._report(val, **kwargs)
    
    def minlap(self, **kwargs):
        """
        Return the minimum lap length.
    
        Returns
        -------
        a report of the minimum of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = min(self._laps)
        return self._report(val, **kwargs)
    
    def meanlap(self, **kwargs):
        """
        Return the mean lap length.
    
        Returns
        -------
        a report of the mean of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = mean(self._laps)
        return self._report(val, **kwargs)
    
    def medianlap(self, **kwargs):
        """
        Return the median lap length.
    
        Returns
        -------
        a report of the median of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = median(self._laps)
        return self._report(val, **kwargs)
    
    def stdevlap(self, **kwargs):
        """
        Return the standard deviation of lap lengths.
    
        Returns
        -------
        a report of the standard deviation of lap lengths
        """
        if len(self._laps) < 1:
            val = 0
        else:
            val = stdev(self._laps)
        return self._report(val, **kwargs)
    
    def check(self, start=False, pause=False, **kwargs):
        """
        Return the amount of active time passed.
        
        Parameters
        ----------
        :start:     `boolean` whether to automatically start the stopwatch  
                    upon calling the function if it is not already active
        :pause:     `boolean` whether to automatically pause the stopwatch  
                    upon calling the function if it is not already active
    
        Returns
        -------
        a report of the total elapsed active time
        """
        # Pause or start stopwatch if requested
        self.pause(pause)
        self.start(start)

        # Get amount of active time passed
        stamp = kwargs.get('stamp', self._time)
        self._check = stamp - self._start - self._less
        
        return self._report(self._check, **kwargs)
    
    def lap(self, printit=False, start=False, pause=False, log=True, 
            check=False, form=None, **kwargs):
        """
        Split lap, and return the amount of time passed since the last split.
        
        Parameters
        ----------
        :printit:   `boolean` whether to automatically print the output to
                    the standard out or to return it instead
        :start:     `boolean` whether to automatically start the stopwatch  
                    upon calling the function if it is not already active
        :pause:     `boolean` whether to automatically pause the stopwatch  
                    upon calling the function if it is not already active
        :log:       `boolean` whether to log the lap time in the object laps
                    property
        :form:      `string` a formatting string to use when printing results
                    if printing is requested; should include formatting keys
                    of 'l' for laps, 'c' for total active time
        :check:     `boolean` whether to also return the total amount of 
                    active time passed as a second value
    
        Returns
        -------
        a report of the most recent lap time; also returns the total amount
        of time passed at the time of the lap split as a second value if
        requested
        """
        # Pause or start stopwatch if requested
        self.pause(pause)
        self.start(start)
            
        # Get split and lap times
        get_split = self._time
        get_lap = get_split - self._split - self._lap_less
        
        # Log lap time (if the timer is running or if it is paused but elapsed
        # time is greater than zero)
        if log and (not self._pause or get_lap > 0):
            self._laps.append(get_lap)
            self._lap = get_lap
            self._split = get_split
            self._lap_less = 0 # Remove lap subtractions
        
        # Report
        res = (self._report(get_lap, **kwargs), self.check(stamp=get_split))
        if printit:
            if form is None:
                form='Lap Time: {l}; \tTotal Time: {c}'
            print(form.format(l=res[0], c=res[1]))
        elif check:
            return res
        else:
            return res[0]
    
    def check_after(self, after=None, printit=False, start=False, pause=False, 
                  **kwargs):
        """
        Return the amount of active time passed after a number of hits.
        
        Parameters
        ----------
        :after:     `integer` the number of hits (calls of this function) 
                    which must occur before a lap gets logged
        :printit:   `boolean` whether to automatically print the output to
                    the standard out or to return it instead
        :start:     `boolean` whether to automatically start the stopwatch  
                    upon calling the function if it is not already active
        :pause:     `boolean` whether to automatically pause the stopwatch  
                    upon calling the function if it is not already active
    
        Returns
        -------
        a report of the total elapsed active time
        """
        # Pause or start stopwatch if requested
        self.pause(pause)
        self.start(start)

        self.hit(**kwargs)
        if self._hits % after == 0:
            res = self.check(**kwargs)
            if printit:
                print(res)
            else:
                return res
        else:
            return None
        
    def lap_after(self, after=None, printit=False, start=False, pause=False, 
                  form=None, form_vals=None, log=True, check=False, **kwargs):
        """
        Split lap after a number of hits, and return the amount of time passed 
        since the last split.
        
        Parameters
        ----------
        :after:     `integer` the number of hits (calls of this function) 
                    which must occur before a lap gets logged
        :printit:   `boolean` whether to automatically print the output to
                    the standard out or to return it instead
        :start:     `boolean` whether to automatically start the stopwatch  
                    upon calling the function if it is not already active
        :pause:     `boolean` whether to automatically pause the stopwatch  
                    upon calling the function if it is not already active
        :form:      `string` a formatting string to use when printing results
                    if printing is requested; should include formatting keys
                    of 'h' for hits, 'l' for laps, 'c' for total active time
        :form_vals: `dict` a dictionary of formatting values to be entered in
                    the formatting string
        :log:       `boolean` whether to log the lap time in the object laps
                    property
        :check:     `boolean` whether to also return the total amount of 
                    active time passed as a second value
    
        Returns
        -------
        a report of the most recent lap time; also returns the total amount
        of time passed at the time of the lap split as a second value if
        requested
        """
        # Pause or start stopwatch if requested
        self.pause(pause)
        self.start(start)

        self.hit(**kwargs)
        if self._hits % after == 0:
            res = self.lap(log=log, check=True, **kwargs)
            if printit:
                if form is None:
                    form='Hits: {h}; \tLap Time: {l}; \tTotal Time: {c}'
                if type(form_vals) is dict:
                    print(form.format(h=self._hits, l=res[0], c=res[1], 
                                      **form_vals))
                elif form_vals is None:
                    print(form.format(h=self._hits, l=res[0], c=res[1]))
                else:
                    raise TypeError("""Formatting values must be provided as a 
dictionary of formatting keys and inputs""")
            else:
                return res if check else res[0]
        else:
            return None
        
    def hit(self, hits=1, **kwargs):
        """
        Increase the number of hits on the stopwatch by one or a given number.

        Parameters
        ----------
        :hits:      `integer` the number of hits to increase the hit count by
        """
        self._hits += hits
        
    def reset_hits(self):
        """
        Reset the number of hits on the stopwatch to zero.
        """
        self._hits = 0

    def pause(self, pauseit=True):
        """
        Pause the stopwatch, stopping time for both checks and laps.
    
        Returns
        -------
        None
        """
        if pauseit:
            # Check if the stopwatch is currently active
            if not self._pause:
                # Set pause time as current time (True)
                self._pause = self._time
        
    def start(self, startit=True):
        """
        Start the stopwatch, resuming time for both checks and laps.
    
        Returns
        -------
        None
        """
        if startit:
            # Check if the stopwatch is currently paused
            if self._pause:
                # Update pause subtractions
                self._less += self._resource() - self._pause
                self._lap_less += self._resource() - self._pause
            # Set pause time to zero (False)
            self._pause = 0
    
    def reset(self, start=True, **kwargs):
        """
        Reset the stopwatch and all stopwatch and lap variables.
        
        Parameters
        ----------
        :start:     `boolean` whether to automatically start the stopwatch  
                    upon re-initialization
    
        Returns
        -------
        None
        """
        # Get start time
        _start = kwargs.get('_start', self._resource())
        _less = kwargs.get('_less', 0)
        self._start = self._split = _start
        self._check = 0
        self._lap = 0
        self._hits = 0
        # Set pause subtractions
        if start:
            self._pause = 0
        else:
            self._pause = _start
        self._less = _less
        self._lap_less = 0
        # Reset records
        self._laps = []
        # Reset operational values
        self._break_loop = False
    
    def func_timer(self, func, report=False):
        """
        Function wrapper which times each call of the decorated function,
        logging the operation time of the function as a new lap. The wrapper
        automatically pauses the stopwatch between calls. The wrapper can
        print a report of function operation time if requested.
        
        Parameters
        ----------
        :func:      `function` the target function which will wrapped, timed,
                    and reported on
        :report:    `boolean, default True` whether to print split time 
                    reports for each operation of the wrapped function
        """
        self.reset(start=False)
        def wrapper(*args, **kwargs):
            self.start()
            result = func(*args, **kwargs)
            if report: print("Operation time: {}".format(
                    self.lap(pause=True)))
            else: self.lap(pause=True)
            return result
        return wrapper
    
    def loop_timer(self, iterable, every=None, report=False):
        """
        Creates a self-reporting iterable from an input iterable, printing
        split and total times elapsed for the iteration of a loop. The report
        is generated periodically based on the input `every` integer. To not
        print reports but only log them as laps, set the `report` parameter to
        `False`.
        
        Parameters
        ----------
        :iterable:  `iterable` an iterable which will be iterated by the
                    function, yielding the same values
        :every:     `integer, default 1` the number of iterated items to be 
                    evaluated in each timer report
        :report:    `boolean, default False` whether to print split time 
                    reports for the iteration of each chunk of items

        Yield
        -----
        iterable values
        """
        # Initialize
        self._break_loop = False
        
        # Divide iterable into chunks of input size
        if every is None:
            every = 1
        else:
            try:
                every = int(every)
                if every < 1:
                    raise ValueError("The 'every' parameter must be > 0")
            except:
                raise TypeError("The 'every' parameter must be an integer")
        chunks = chunkit(iterable, size=every)
        if report:
            try:
                i = len(iterable)
            except:
                i = 0
                for chunk in chunks:
                    i += len(chunk)
            j = len(chunks)
            print("Begin loop timer ({} items in {} chunks).".format(i, j))
        self.reset(start=False) # Reset stopwatch
        
        # Iterate over chunks of input iterable
        for i, chunk in enumerate(chunks):
            # Iterate and yield items within the chunk
            self.start()
            for j, x in enumerate(chunk):
                yield x
                if self._break_loop: break
                
            # Log/report times
            if report: print("""\
Items: {:,.0f} - {:,.0f} \tSplit time: {} \tTotal time: {}\
""".format(i*every+1, i*every+j+1, *self.lap(check=True)))
            else: self.lap()
            if self._break_loop: break
        
        if report: print("End loop timer.")
        
    def timed_loop(self, iterable=None, s=0, m=0, h=0, cutoff=0, **kwargs):
        """
        Iterate the given iterable for a fixed amount of time before cutting
        it off.
        
        Parameters
        ----------
        :iterable:  `iterable` an iterable which will be iterated by the
                    function, yielding the same values; if no value is given,
                    an infinite counter will be initialized, starting at 0
                    and counting by 1 until the input time has elapsed
        :s:         `int, float` number of seconds to use for expiratoin timer
        :m:         `int, float` number of minutes to use for expiratoin timer
        :h:         `int, float` number of hours to use for expiratoin timer
        :cutoff:    `int {0: overtime, 1: lastlap, 2: meanlap, 3: medianlap, 
                    4: maxlap}, default 0}` whether to cut-off iteration early 
                    to avoid over-running expiration time based on the 
                    expected time of the next lap, estimating based on the 
                    last, mean, median, or max lap time
        :kwargs:    keyword arguments passed to the loop_timer method
                    
        Yield
        -----
        iterable values
        """
        # Compute expiration time
        timer = s + 60*m + 3600*h
        # Define cutoff method options
        every = kwargs.get('every', 1)
        cutoff_ops = {1:'lastlap', 2:'meanlap', 3:'medianlap', 4: 'maxlap'}
        
        # If no iterable given, create infinite generator
        if iterable is None:
            iterable = infinite_count()
            
        # Iterate
        for i, x in enumerate(self.loop_timer(iterable, **kwargs)):
            # Yield next value
            yield x
            
            # Check for end of chunk
            if (i) % every == 0:
                
                # Check for expiration
                elapsed = self.check(numeric=True, hms=False)
                if cutoff == 0:
                    if elapsed >= timer:
                        self._break_loop = True
                
                # Check if there is time for another lap before expiration
                else:
                    try:
                        func = getattr(self, cutoff_ops[cutoff])
                        x = func(numeric=True, hms=False)
                        if elapsed + x*every > timer:
                            self._break_loop = True
                    except:
                        raise ValueError("Invalid cutoff option.")            
                
    def sync(self, *sws):
        """
        Synchronize input stopwatch instances with this stopwatch by resetting
        them and matching their active time variables.
        
        Parameters
        ----------
        :sw:        `Stopwatch` instances of the Stopwatch object type to 
                    synchronize with the current stopwatch
        """
        # Iterate over input arguments
        for sw in sws:
            # Confirm that input arguments are Stopwatch-type
            if not isinstance(sw, Stopwatch):
                raise TypeError("Input arguments must be Stopwatch-type.")
            # Syncronize stopwatch information
            sw.reset(start=self.active, _start=self._start, _less=self._less)
            
    def now(self, printit=False, form=None, long=False):
        """
        Report the current time in datetime format.

        Parameters
        ----------
        :printit:   `boolean` whether to automatically print the output to
                    the standard out or to return it instead
        :form:      `string` a formatting string to use when reporting time 
                    values as a formatted string (ignored if numeric is True); 
                    the string will receive three inputs of hours, minutes, 
                    and seconds if hms is True and will receive one input of 
                    seconds if hms is False
        """
        if form is None:
            if long:
                form = "%A %B %d, %Y %H:%M:%S"
            else:
                form = "%Y-%m-%d %H:%M:%S"
        res = time.strftime(form)
        if printit:
            print(res)
        else:
            return res
    
    def report(self, text, *fmts, reset=False, **kwargs):
        """
        Print the current amount of active time passed along with a given 
        text message. This is helpful when periodically reporting on the 
        progress of a lengthy process.
        
        Parameters
        ----------
        :text:      `str` a text message to include after the reported active
                    time passed
        :*fmts:     `str` formatting strings to be passed to the string 
                    formatting function which gets called on the provided 
                    text message; can also be passed through kwargs
        :reset:     whether to reset the stopwatch at the call of the function
        """
        # Check active time passed
        if reset:
            self.reset(start=False)
            res = self.check(start=True, **kwargs)
        else:
            res = self.check(**kwargs)
            
        # Format text string
        text = str(text)
        text = '[{}] '.format(res) + text.format(*fmts, **kwargs)
        print(text)

    def report_new(self, text, *fmts, **kwargs):
        """
        Reset the stopwatch and report no time passed along with a given 
        text message. This is helpful when periodically reporting on the 
        progress of a lengthy process, providing the initial message and 
        baseline time point.
        
        Parameters
        ----------
        :text:      `str` a text message to include after the reported active
                    time passed
        :*fmts:     `str` formatting strings to be passed to the string 
                    formatting function which gets called on the provided 
                    text message; can also be passed through kwargs
        """
        self.report(text, *fmts, reset=True, **kwargs)

    def report_beg(self, text, *fmts, **kwargs):
        """
        Reset the stopwatch and report no time passed along with a given 
        text message. This is helpful when periodically reporting on the 
        progress of a lengthy process, providing the initial message and 
        baseline time point.
        
        Parameters
        ----------
        :text:      `str` a text message to include after the reported active
                    time passed
        :*fmts:     `str` formatting strings to be passed to the string 
                    formatting function which gets called on the provided 
                    text message; can also be passed through kwargs
        """
        print("START TIME: {}".format(self.now(**kwargs)))
        self.report(text, *fmts, reset=True, **kwargs)

    def report_end(self, text, *fmts, **kwargs):
        """
        Reset the stopwatch and report no time passed along with a given 
        text message. This is helpful when periodically reporting on the 
        progress of a lengthy process, providing the initial message and 
        baseline time point.
        
        Parameters
        ----------
        :text:      `str` a text message to include after the reported active
                    time passed
        :*fmts:     `str` formatting strings to be passed to the string 
                    formatting function which gets called on the provided 
                    text message; can also be passed through kwargs
        """
        self.report(text, *fmts, reset=False, **kwargs)
        print("END TIME:   {}".format(self.now(**kwargs)))

    def report_now(self, text, *fmts, **kwargs):
        """
        Print the current time along with a given text message. This is 
        helpful when periodically reporting on the progress of a lengthy 
        process.
        
        Parameters
        ----------
        :text:      `str` a text message to include after the reported active
                    time passed
        :*fmts:     `str` formatting strings to be passed to the string 
                    formatting function which gets called on the provided 
                    text message; can also be passed through kwargs
        """
        # Format text string
        text = str(text)
        text = '[{}] '.format(self.now(**kwargs)) + \
                            text.format(*fmts, **kwargs)
        print(text)

    def _report(self, delta, printit=False, **kwargs):
        """
        Report the given amount of seconds elapsed in the stopwatch's chosen
        or default format.
        """
        # Get formatting info
        numeric = kwargs.get('numeric', self.numeric)
        hms = kwargs.get('hms', self.hms)
        form = kwargs.get('form', self.form)
        
        # If a report process is given, apply
        if not self.process is None:
            res = self.process(delta)
        # If numeric report requested, apply
        if numeric:
            # If hour-minute-second disaggregation requested, apply
            if hms:
                res = s_to_hms(delta)
            else:
                res = delta
        # If formatted report requested (else), apply
        else:
            # If hour-minute-second disaggregation requested, apply
            if hms:
                try:
                    res = form.format(*s_to_hms(delta))
                except IndexError:
                    raise ValueError("Invalid formatting string.")
            else:
                try:
                    res = form.format(delta)
                except IndexError:
                    raise ValueError("Invalid formatting string.")
        
        # Return or print the result
        if printit:
            print(res)
            return None
        else:
            return res
        
        
########################
# SUPPORTING FUNCTIONS #
########################


def stopwatch(numeric=False, hms=True, form=None):
    """
    Creates a Stopwatch object based on the input parameters and returns a 
    handle for the check function, which will return the time difference 
    between the original call of the stopwatch function and the call of the
    check function.

    Parameters
    ----------
    :numeric:   `boolean` whether to default to reporting time values 
                numerically or with a formatted string
    :hms:       `boolean` whether to default to reporting time values in terms
                of hours, minutes, and seconds (returned as a list if numeric
                is True)
    :form:      `string` a formatting string to use when reporting time values
                as a formatted string (ignored if numeric is True); the string
                will receive three inputs of hours, minutes, and seconds if
                hms is True and will receive one input of seconds if hms is
                False
    
    Returns
    -------
    a stopwatch object, initialized using the given parameters
    """
    obj = Stopwatch(numeric=numeric, hms=hms, form=form)
    return obj.check

def timed_loop(iterable=None, s=0, m=0, h=0, **kwargs):
    """
    """
    sw = Stopwatch()
    return sw.timed_loop(iterable=iterable, s=s, m=m, h=h, **kwargs)

def s_to_hms(s):
    """
    Convert a number of seconds into a three-number tuple of hours, minutes, 
    and seconds.

    Parameters
    ----------
    :seconds:   `numeric` number of seconds to convert to hours, minutes, and
                seconds
    
    Returns
    -------
    a tuple of hours, minutes, and seconds
    """
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return h, m, s

def hms_to_s(h, m, s):
    """
    Convert numbers of hours, minutes, and seconds into a number of seconds.

    Parameters
    ----------
    :h:     `numeric` number of hours to convert to seconds
    :m:     `numeric` number of minutes to convert to seconds
    :s:     `numeric` number of seconds
    
    Returns
    -------
    total number of seconds
    """
    seconds = h * 3600 + m * 60 + s
    return seconds
