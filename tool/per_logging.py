# -*- coding: latin-1 -*-
"""
Copyright © 2016-2025 Eole-lien SC.
All rights reserved as Copyright owner.

Copyright ©

Personnalisation du logging
"""
import datetime as dt
import logging
import os
import threading
import traceback
from logging.handlers import RotatingFileHandler

from tool.configuration import config

_FORMAT = '%(levelname)-8s %(asctime)s %(processName).15s %(module)50s %(message)s'
_CSV_FORMAT = '%(levelname)s\t%(asctime)s.%(msecs)03d\t%(module)50s\t\"%(message)s\"'


# Storage for process id caller of logging
logging_caller = {}

# region defined log default configuration parameter if needed
def verify_logging():
    _log_path = os.environ.get('LOG_PATH', 'logs')
    _log_level = os.environ.get('LOG_LEVEL', 'INFO')
    _log_per_format = os.environ.get('LOG_PER_FORMAT', _CSV_FORMAT)
    if not hasattr(config, 'max_size'):
        # default value for log file size is 10Mo
        setattr(config, 'max_size', 10 * 1024 * 1024)
    if not hasattr(config, 'directory'):
        # directory where to store application log
        setattr(config, 'directory', _log_path)
    if not hasattr(config, 'thread_info'):
        # directory where to store application log
        setattr(config, 'thread_info', False)
    if not hasattr(config, 'level'):
        setattr(config, 'level', _log_level)
    if not hasattr(config, 'per_format'):
        setattr(config, 'per_format', _log_per_format)


verify_logging()
# endregion

def basic_config(**kwargs):
    """
    Redirection to the logging.basicConfig function.

    :param kwargs: 
    """
    logging.basicConfig(**kwargs)


class AnsiColorStreamHandler(logging.StreamHandler):
    """
    Improve the handler to add a color to the output based on the log level.
    """
    DEFAULT = '\x1b[0m'
    FOREGROUND_BLACK = '\x1b[30m'
    FOREGROUND_RED = '\x1b[31m'
    FOREGROUND_GREEN = '\x1b[32m'
    FOREGROUND_YELLOW = '\x1b[33m'
    FOREGROUND_BLUE = '\x1b[34m'
    FOREGROUND_MAGENTA = '\x1b[35m'
    FOREGROUND_CYAN = '\x1b[36m'
    FOREGROUND_WHITE = '\x1b[37m'

    BACKGROUND_BLACK = '\x1b[40m'
    BACKGROUND_RED = '\x1b[41m'
    BACKGROUND_GREEN = '\x1b[42m'
    BACKGROUND_YELLOW = '\x1b[43m'
    BACKGROUND_BLUE = '\x1b[44m'
    BACKGROUND_MAGENTA = '\x1b[45m'
    BACKGROUND_CYAN = '\x1b[46m'
    BACKGROUND_WHITE = '\x1b[47m'

    CRITICAL = BACKGROUND_RED + FOREGROUND_WHITE
    ERROR = FOREGROUND_RED
    WARNING = FOREGROUND_YELLOW
    INFO = FOREGROUND_GREEN
    PERF = FOREGROUND_MAGENTA
    DEBUG = FOREGROUND_CYAN

    @classmethod
    def _get_color(cls, log_level):
        if log_level >= logging.CRITICAL:
            return cls.CRITICAL
        elif log_level >= logging.ERROR:
            return cls.ERROR
        elif log_level >= logging.WARNING:
            return cls.WARNING
        elif log_level >= logging.INFO:
            return cls.INFO
        elif log_level >= logging.DEBUG:
            return cls.DEBUG
        else:
            return cls.DEFAULT

    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)

    def format(self, record):
        text = logging.StreamHandler.format(self, record)
        color = self._get_color(record.levelno)
        return color + text + self.DEFAULT


class WinColorStreamHandler(logging.StreamHandler):
    """
    Handler used to add color to the log (on Windows)
    """
    # wincon.h
    FOREGROUND_BLACK = 0x0000
    FOREGROUND_BLUE = 0x0001
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_CYAN = 0x0003
    FOREGROUND_RED = 0x0004
    FOREGROUND_MAGENTA = 0x0005
    FOREGROUND_YELLOW = 0x0006
    FOREGROUND_GREY = 0x0007
    FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.
    FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED

    BACKGROUND_BLACK = 0x0000
    BACKGROUND_BLUE = 0x0010
    BACKGROUND_GREEN = 0x0020
    BACKGROUND_CYAN = 0x0030
    BACKGROUND_RED = 0x0040
    BACKGROUND_MAGENTA = 0x0050
    BACKGROUND_YELLOW = 0x0060
    BACKGROUND_GREY = 0x0070
    BACKGROUND_INTENSITY = 0x0080  # background color is intensified.
    BACKGROUND_WHITE = BACKGROUND_BLUE | BACKGROUND_GREEN | BACKGROUND_RED

    DEFAULT = FOREGROUND_GREY
    CRITICAL = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
    ERROR = FOREGROUND_RED | FOREGROUND_INTENSITY
    WARNING = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
    INFO = FOREGROUND_GREEN
    DEBUG = FOREGROUND_CYAN

    @classmethod
    def _get_color(cls, log_level):
        if log_level >= logging.CRITICAL:
            return cls.CRITICAL
        elif log_level >= logging.ERROR:
            return cls.ERROR
        elif log_level >= logging.WARNING:
            return cls.WARNING
        elif log_level >= logging.INFO:
            return cls.INFO
        elif log_level >= logging.DEBUG:
            return cls.DEBUG
        else:
            return cls.DEFAULT

    def _set_color(self, code):
        import ctypes
        ctypes.windll.kernel32.SetConsoleTextAttribute(self._outhdl, code)

    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)
        # get file handle for the stream
        import ctypes.util
        # for some reason find_msvcrt() sometimes doesn't find msvcrt.dll on my system?
        crtname = ctypes.util.find_msvcrt()
        if not crtname:
            crtname = ctypes.util.find_library("msvcrt")
        crtlib = ctypes.cdll.LoadLibrary(crtname)
        self._outhdl = crtlib._get_osfhandle(self.stream.fileno())

    def emit(self, record):
        color = self._get_color(record.levelno)
        self._set_color(color)
        logging.StreamHandler.emit(self, record)
        self._set_color(self.DEFAULT)


class DateFormatter(logging.Formatter):
    """
    Formatter used to format the log message.
    """

    def __init__(self, msg, use_color=True, datefmt=None):
        logging.Formatter.__init__(self, msg, datefmt=datefmt)
        self.use_color = use_color

    converter = dt.datetime.fromtimestamp

    def formatTime(self, record: logging.LogRecord, datefmt=None):
        ct = self.converter(record.created)
        t = ct.strftime("%Y-%m-%d %H:%M:%S")
        s = "%s.%03d" % (t, record.msecs)
        return s

    def format(self, record: logging.LogRecord):
        """
        Format the console output line. Limits the fields processName, module, funcName and split msg field if
        length > 120 characters
        :param record: logging record
        :return: formatted line(s)
        """
        record.processName = loggers.get('name')
        # if module = per_logging, try to retrieve a more pertinent info ...
        if record.module == 'per_logging':
            summary = list(traceback.StackSummary.extract(traceback.walk_stack(None)))
            information = summary[0]
            for i, fs in enumerate(summary):
                if fs.lineno == record.lineno and fs.filename == record.pathname:
                    information = summary[i + 2]
                    break
            record.lineno = information.lineno
            record.module = os.path.basename(information.filename)
            record.funcName = '!!! ' + information.name

        # limits the module info to 50 characters
        record.module = '{},{}:{}'.format(record.funcName, record.module, record.lineno)
        if len(record.module) > 50:
            record.module = record.module[:50]

        # Insert indentation corresponding to level of threading
        thread_name = threading.current_thread().name
        hierarchy_level = _get_hierarchy_level(thread_name)
        indentation = _get_indentation(hierarchy_level)
        record.msg = " {0}{1}".format(indentation, record.msg)

        return super().format(record)

loggers = {}
def add_console_handler(caller:str) -> None:
    """
    add another handler to the logging system to display logs in console.
    :param caller: str: caller's name.
    """
    # Stores the PID of the calling process for displaying the right process name
    global logging_caller
    logging_caller[str(os.getpid())] = '{:<10}'.format(caller)
    global loggers

    _logger = loggers.get('name', '')
    loggers.update(dict(name=f'{caller}'))
    if _logger != '':
        return

    # try to give some colors in this poor world ...
    color_stream_handler_class = AnsiColorStreamHandler

    _ch = color_stream_handler_class()
    _ch.setFormatter(DateFormatter(_FORMAT))

    _per_logger = logging.getLogger()
    # _log_level = _per_logger.getEffectiveLevel()
    # _ch.setLevel(_log_level)

    # Replace StreamHandler by AnsiColorStreamHandler
    _remove = None
    for handler in _per_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            _remove = handler
            break
    if _remove is not None:
        _per_logger.removeHandler(_remove)
    _per_logger.addHandler(_ch)



_srcfile = os.path.normcase(basic_config.__code__.co_filename)


class Logger(logging.RootLogger):
    """
    Specialization of the RootLogger to retrieve the python file where the log is done.
    """
    def __init__(self):
        super(Logger, self).__init__(logging.DEBUG)


# logging.root = Logger()
if not os.path.exists(config.directory):
    os.makedirs(config.directory)


def namer(name: str=".1") -> str:
    """
    Generate a log file name based on the name and on the stacktrace.
    :param name: s
    :return: the generated name
    """
    stack_list = traceback.format_stack()
    ext = "log"
    if name.endswith(".1"):
        timestamp = dt.datetime.now()
        # format : yyyyMMdd_hhmm.ss_log.csv
        filename_format = "{}{:02}{:02}_{:02}{:02}.{:02}." + ext
        filename = filename_format.format(timestamp.year, timestamp.month, timestamp.day,
                                          timestamp.hour, timestamp.minute,
                                          timestamp.second)
        return os.path.join(os.environ.get('LOG_PATH', 'logs'), filename)
    else:
        return name


# DO NOT CHANGE backupCount VALUE, THE VALUE IS USED IN THE NAME GENERATION PROCESSING
rotating_handler = RotatingFileHandler(filename=namer(),
                                       maxBytes=10 * 1024 * 1024,
                                       encoding='utf-8',
                                       backupCount=1)
rotating_handler.namer = namer

basic_config(format=_CSV_FORMAT,
             level=os.environ.get("LOG_LEVEL", "INFO"),
             datefmt='%Y-%m-%dT%H:%M:%S')
logger0 = logging.getLogger()
logger0.addHandler(rotating_handler)

_hierarchy_levels = {}

def log_level(level):
    _logger = logging.getLogger()
    _level1 = _logger.getEffectiveLevel()
    _logger.setLevel(level)
    _level2 = _logger.getEffectiveLevel()
    # for handler in logger0.handlers:
    #     handler.setLevel(level)

def debug(message, *args, **kwargs):
    """
    Log a message with the DEBUG log level.
    This is used to display information useful to investigate problems.
    A DEBUG message is normally not DISPLAYED to the user.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.DEBUG, message, args, kwargs)


def info(message, *args, **kwargs):
    """
    Log a message with the INFO log level.
    This is used to log standard information to the user.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.INFO, message, args, kwargs)


def log(log_level, message, *args, **kwargs):
    """
    Log a message with a specific log level.
    
    :param log_level:
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(log_level, message, args, kwargs)


def warn(message, *args, **kwargs):
    """
    Log a message with the WARN log level.
    This is used to log warnings.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.WARN, message, args, kwargs)


def error(message, *args, **kwargs):
    """
    Log a message with the ERROR log level.
    This is used to log errors.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.ERROR, message, args, kwargs)


def fatal(message, *args, **kwargs):
    """
    Log a message with the FATAL log level.
    This is used to log fatal errors.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.FATAL, message, args, kwargs)


def critical(message, *args, **kwargs):
    """
    Log a message with the CRITICAL log level.
    This is used to log critical errors.
    
    :param message: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    _log(logging.CRITICAL, message, args, kwargs)


def _get_indentation(hierarchy_level):
    """
    Create the indentation string corresponding to the hierarchy level. (two spaces by level)
    :param hierarchy_level: the log hierarchy level represented by a numeric value.
    :return: the indentation string corresponding to the hierarchy level.
    :rtype: str
    """
    tab = "  "
    indentation = ""
    current = 0
    while current < hierarchy_level:
        indentation += tab
        current += 1
    return indentation


def _log(log_level, message, *args, **kwargs):
    """
    Main method for the logging process. This method is called by all public log method which provide the log level to used.
    This method should not be used.
    
    :param log_level: int: the log level to use to log the message
    :param message: obj: the message to log (will be stringify) 
    :param args: ignored
    :param kwargs: ignored
    :return: None
    """
    for s in str(message).split("\n"):
        logging.log(log_level, s)


def _get_hierarchy_level(thread_name):
    """
    Based on the thread name, returns the current hierachy level.
    :param thread_name: str: the thread's name
    :return: the hierachy level associated with the thread name. If none, returns 0.
    """
    if thread_name in _hierarchy_levels:
        return _hierarchy_levels[thread_name]
    return 0


def increase_hierarchy_level() -> None:
    """
    Increase the log level to use a hierarchical view of logs
    """
    thread_name = threading.current_thread().name
    current_thread_level = _get_hierarchy_level(thread_name)
    _hierarchy_levels[thread_name] = current_thread_level + 1


def decrease_hierarchy_level() -> None:
    """
    Decrease the log level to use a hierarchical view of logs
    """
    thread_name = threading.current_thread().name
    current_thread_level = _get_hierarchy_level(thread_name)
    _hierarchy_levels[thread_name] = current_thread_level - 1
    if _hierarchy_levels[thread_name] == 0:
        _hierarchy_levels.pop(thread_name, None)


class LoggedCalled(object):
    """
    Context to easily increase the log level hierarchy.
    """

    def __enter__(self):
        debug("<block>")
        increase_hierarchy_level()

    def __exit__(self, exc_type, exc_val, exc_tb):
        decrease_hierarchy_level()
        debug("</block>")