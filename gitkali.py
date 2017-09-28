#!/usr/bin/python3

"""
Written by: True Demon
The non-racist Kali repository grabber for all operating systems.
Git Kali uses Offensive Security's package repositories and their generous catalog
of extremely handy penetration testing tools. This project is possible because
of Offensive Security actually sticking to good practices and keeping their
packages well-organized, so thanks OffSec! :)
#TryHarder
"""

# TODO: Finish Install Script
# TODO: Categorize tool searches
# TODO: Categorization of repos is a big task to be done later
# TODO: Include package management

import argparse

import packmgr as packager
from utils import *     # includes sys, os

prog_info = "GIT Kali Project"
__author__ = "True Demon"
__winstall__ = "C:\\ProgramFiles\\GitKali\\"        # Default package installation directory for Windows
__linstall__ = "/usr/share"                        # Default package installation directory for Linux
__install__ = ""                                    # Used to store default install directory based on OS

try:
    if os.name == 'posix':
        __install__ = __linstall__
        if os.getuid():
            print("You need to be root to install packages. Try again as sudo.")
            sys.exit()

    elif os.name == 'nt':
        __install__ = __winstall__
        from ctypes import windll

        if not windll.shell32.IsUserAnAdmin():
            print("You must be an administrator to install packages. Please run from an escalated cmd.")

    else:
        sys.stderr("Could not detect your privileges / operating system. "
                   "This script only supports Linux (Posix) and Windows (nt) systems.")

except OSError:
    sys.stderr("Unknown Operating System detected. You must have invented this one yourself! Teach me, Senpai!")
    exit()

except ImportError as e:
    sys.stderr("Invalid or missing libraries: \n%s" % e)


def search(search_word):
    # search function for valid packages to install
    found = []
    with open('kali-packages.lst', 'r') as file:
        packages = file.readlines()
        for p in packages:
            if search_word in p.split()[0]:
                found.append(p.split()[0])

        if not len(found):
            print(Symbol.fail + " Could not find any matching packages")
            return None
        print("Found packages: ")
        print(' '.join(found))


def check_install_dir(install_dir=__install__):
    if os.path.exists(install_dir):
        try:
            os.chdir(install_dir)
            if os.getcwd() != install_dir:
                print("Something went wrong. We can't get to your installation directory: %s" % install_dir)
                sys.exit()

        except OSError:
            print("Somehow, you broke it. Dunno how ya did it, but a bug report would be mighty handy to figure out how!")
            sys.exit(-1)


def main():

    parser = argparse.ArgumentParser(prog='gitkali.py', description='The apt-like Kali package installer for Linux',
                                     epilog=prog_info, formatter_class=argparse.RawTextHelpFormatter)
    parser._positionals.title = "Commands"
    parser.add_argument("command", choices=["search", "install", "update", "upgrade"],
                        help="search  : search package list for compatible packages\n" +
                        "install : install specified package\n" +
                        "update  : update package lists\n" +
                        "upgrade : upgrade kali packages\n\n"
    )
    parser.add_argument("packages", action='store', metavar='package', nargs='*', help="package(s) to upgrade/install")
    parser.add_argument("-d", "--directory", action='store', default=__install__,
                        help="Alternate installation directory")

    args = parser.parse_args()
    packages = [str(p) for p in args.packages]      # Converts args.package(tuple) to list of strings for ease of use

    args.directory = os.path.abspath(args.directory)

    if args.command == 'search':
        packager.check_kali_packages()
        for p in packages:
            search(p)

    elif args.command == 'update':
        packager.get_updates()
        exit()

    elif args.command == 'upgrade':
        packager.upgrade(packages, args.directory)

    elif args.command == 'install':
        if len(packages) == 0 :
            print("No packages given")

        if '*' in packages:
            # NEVER EVER EVER EVER EEEEEEEVVVVVEEEEEEEEEEEERRRRRRRRRRR DO THIS!!!
            # TODO: EVENTUALLY...build a way for this to work safely...
            packager.install_all(args.directory)

        if args.directory != __install__:   # Usually /usr/share/
            check_install_dir(args.directory)                   # Check that the directory exists
            warn_non_standard_dir(args.directory)               # Warn the user that this is not advised
            response = input("Do you wish to proceed?: [y/N]")  # Confirm decision
            if response.upper() != 'Y':
                exit()

        packages_to_install = packager.get_local_packages(packages)
        # Returns a dictionary ex: {package_name: package_url}

        for p in packages_to_install:
            print("Proceeding with install: ", p)
            packager.install(p, packages_to_install[p], args.directory) # install(package_name, url, into directory)


if __name__ == "__main__":
    main()


