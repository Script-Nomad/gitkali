import itertools
import os
import sys
import threading
import time


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Symbol:
    end = Colors.ENDC
    success = Colors.OKGREEN + '[+]' + end
    fail = Colors.FAIL + '[-]' + end
    ok = Colors.OKBLUE + '[*]' + end
    warn = Colors.WARNING + '[!]' + end


class Spinner(object):
    spinner_cycle = itertools.cycle(['-', '/', '|', '\\'])

    def __init__(self):
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.init_spin)

    def start(self):
        self.spin_thread.start()

    def stop(self):
        self.stop_running.set()
        self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            sys.stdout.write(self.spinner_cycle.next())
            sys.stdout.flush()
            time.sleep(0.25)
            sys.stdout.write('\b')


# This Class pulled from Smoke-Zephyr to reduce number of libraries user must install
# Thanks to ZeroSteiner @ https://www.github.com/zeroSteiner/smoke-zephyr for letting me rip his code
class FileWalker:
    # This class is used to easily iterate over files in a directory.

    def __init__(self, filespath, absolute_path=False, skip_files=False, skip_dirs=False, filter_func=None):
        """
        :param str filespath: A path to either a file or a directory. If
            a file is passed then that will be the only file returned
            during the iteration. If a directory is passed, all files
            will be recursively returned during the iteration.
        :param bool absolute_path: Whether or not the absolute path or a
            relative path should be returned.
        :param bool skip_files: Whether or not to skip files.
        :param bool skip_dirs: Whether or not to skip directories.
        :param function filter_func: If defined, the filter_func function
            will be called for each file and if the function returns false
            the file will be skipped.
        """
        if not (os.path.isfile(filespath) or os.path.isdir(filespath)):
            raise Exception(filespath + ' is neither a file or directory')
        if absolute_path:
            self.filespath = os.path.abspath(filespath)
        else:
            self.filespath = os.path.relpath(filespath)
        self.skip_files = skip_files
        self.skip_dirs = skip_dirs
        self.filter_func = filter_func
        if os.path.isdir(self.filespath):
            self._walk = None
            self._next = self._next_dir
        elif os.path.isfile(self.filespath):
            self._next = self._next_file

    def __iter__(self):
        return self._next()

    def _skip(self, cur_file):
        if self.skip_files and os.path.isfile(cur_file):
            return True
        if self.skip_dirs and os.path.isdir(cur_file):
            return True
        if self.filter_func is not None:
            if not self.filter_func(cur_file):
                return True
        return False

    def _next_dir(self):
        for root, dirs, files in os.walk(self.filespath):
            for cur_file in files:
                cur_file = os.path.join(root, cur_file)
                if not self._skip(cur_file):
                    yield cur_file
            for cur_dir in dirs:
                cur_dir = os.path.join(root, cur_dir)
                if not self._skip(cur_dir):
                    yield cur_dir
        raise StopIteration

    def _next_file(self):
        if not self._skip(self.filespath):
            yield self.filespath
        raise StopIteration


def warn_non_standard_dir(directory):
    print(Symbol.warn + "You are attempting to install something into a non-standard installation directory: %s"
          % directory)
    print("This is not the recommended way to do things. If you know what you're doing, you may proceed.\n"
          "But I suggest changing the __install__ global variable at the top of in the %s script so that\n"
          "you do not need to specify -d every time." % sys.argv[0])


def danger_will_robinson():
    print("WAIT! Really REALLY think about this first...\n" +
          "Installing ALL Kali packages includes things that can easily screw up your Linux environment.\n" +
          "Things like Gnome/KDE, kernel packages, and drivers that may be potentially incompatible and dangerous!!!\n" +
          "This script can't protect you from yourself or the danger of OS destruction you are inviting into your system.\n")


def point_of_no_return():
    print("Well...too bad. :P\n" +
          "This hasn't been implemented yet because it's effin' dangerous and unpredictable.\n" +
          "Come back later when it's finished and some protections have been added.\n" +
          "If you're that determined to put a bullet in your kernel, \n" +
          "You can do a 'sudo rm -rf /' for all I care...\n")
