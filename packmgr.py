from bs4 import BeautifulSoup

from utils import *


class Path:

    gitkali = os.path.realpath(__file__)
    gitkali_dir = os.path.dirname(gitkali)
    packages = gitkali_dir + '/kali-packages.lst'
    kali_repo = 'http://git.kali.org/gitweb/'

# Symbols for print statements
Ok = Symbol.ok              # [*] (color blue)
Success = Symbol.success    # [+] (color green)
Fail = Symbol.fail          # [-] (color red)
Warn = Symbol.warn          # [!] (color orange)


# REPOSITORY FUNCTIONS
#
# Description: These functions deal with the kali repositories themselves and are directly called for updating, reading
#              from and writing to the local package lists. Similar to "apt-get update"


def check_kali_packages():          # Checks if the kali package file exists
    # TODO: Eventually, build in a way to load custom package lists
    if os.path.isfile(Path.packages):
        print(Success + ' Loading packages from %s' % Path.packages)
        if os.stat(Path.packages).st_size == 0:
            print(Fail + " Kali Package file is empty. Performing update")
            get_updates()
        return True


def get_repos():                    # Grabs repositories from git.kali.org

    print(Ok + " Getting latest repositories from kali.org... ")
    from requests import get
    try:
        return get(Path.kali_repo)
    except ConnectionError:
        print(Fail + " Unable to connect to kali.org. Check your Internet Connection...")
        exit()


def process_repos(html_data):       # Processes repositories from git.kali.org/packages and returns them as a list
    
    print(Success + " Packages received. Processing...")
    package_list = []
    soup = BeautifulSoup(html_data.content, 'lxml')
    table = soup.find('table')
    rows = table.findAll('tr')
    for row in rows:
        col = row.findAll('a', attrs={'class': 'list'})         # Some BS wizardry right here @_@
        col = [ele.string for ele in col]
        try:
            pack = col[0].split('/')[-1]
            package_list.append(str(pack))
        except IndexError:
            pass
    return package_list


# Cleans and writes kali packages from process_repos() to kali-packages.lst (local repos)
# Format
# package name      git://git.kali.org/packages/package-name.git
def write_packages(package_list):
    with open(Path.packages, 'w') as kpack:
        lines = {}                                                      # Always use a dictionary for cleanliness
        print(Ok + " Cleaning Packages")
        bad_packages = ['kali', 'debian', 'gnome']
        for pack in package_list:
            if ".git" not in pack.lower():                              # Ignore non-git repos
                pass

            # We don't want Kali, Debian or Gnome packages because they are unnecessary and may break a non-deb OS
            for bad in bad_packages:
                if bad in pack.lower():
                    pass

            package_name = pack.split('.')[0]                           # Takes the .git out of the name
            package_url = "git://git.kali.org/packages/" + pack         # This is the URL convention of git.kali.org
            lines[package_name] = package_url                           # Dictionary to hold packages

        print(Ok + " Packages are nice and squeaky clean!")
        print(Ok + " Writing repositories to %s..." % Path.packages)
        for k, v in sorted(lines.items()):
            kpack.writelines('%-30s %s\n' % (k, v))                     # Write packages to kali-packages.lst

    # Spinner.stop()
    print(Success + " Done!")

# This is the final function that calls all the above in the proper sequence to do the job

def get_updates():
    p = process_repos(get_repos())
    write_packages(p)
    print(Success + " Packages have been updated!")


# INSTALLATION FUNCTIONS
#
# Description: The following functions are tasked with arranging package upgrades and installation procedures
def test_packages(*packages):
    for each in packages:
        print("Printing each package: %s" % each)
    print("Printing Packages: %s" % packages)

def get_local_packages(packages):      # Gets packages from kali-packages.lst and prepare for installation
    print(Ok + "Loading Packages...")

    try:
        if not check_kali_packages():
            print(Fail + "Hmm...the package list does not seem to exist...\n")
            print(Ok + "No problem, I'll make a new one for you!")
            get_repos()

            if not check_kali_packages():
                print(Fail + "Something is wrong...I still can't find the repo list. Exiting...")
                exit()

    except OSError as e:
        print(Fail + "Some kind of path error occurred here. Dumping StackTrace:")
        print(e)
        exit()

    to_install = {}                     # This is the list of urls we will return to the install() function.
    local_packages = {}                 # This is the dictionary of packages by package_name: package_url.
    file = open(Path.packages, 'r')
    lines = file.readlines()
    file.close()                        # Done with the file, let's free up some memory.

    for x in lines:

        get_name = str(x).split()[0]    # string manipulation to grab the first half of the package (name)
        get_url = str(x).split()[1]     # string manipulation to grab the second half of the package (url)
        local_packages[get_name] = get_url

    # DEBUG:    print([x for x in packages])
    missing = [x for x in packages if x not in local_packages.keys()]   # List packages that do not exist
    if missing:
        found = [x for x in packages if x in local_packages.keys()]     # List packages that DO exist
        if len(found) == 0:         # If found is empty...exit
            print(Fail + " Could not find any of the specified packages...")
            exit()
        else:
            print("We are missing the following packages: ")
            for m in missing:
                print("\t" + Fail + " %s" % m)

            print("But we found the following packages: ")
            for f in found:
                print("\t" + Ok + " %s" % f)

            response = input("Continue installing found packages? [y/N]")
            if response.upper() == 'Y':
                print(Ok + "Pulling packages...: " + str(found))
                packages = found
            else:
                print("Exiting...")
                exit()

    print(Ok + "Pulling packages...",)
    for p in packages:
        try:
            to_install[p] = local_packages[p]
            print(Success + " Pulled %s" % p)

        except KeyError:
            print(Fail + " Failed to pull %s because it does not exist. We checked twice! How did you do this!? o.O"% p)

    return to_install


def install(package_name, package_url, install_dir):
    package_path = install_dir + '/' + package_name
    try:
        if os.path.exists(package_path):
            print(Symbol.warn + " WARNING: THIS PATH ALREADY EXISTS!")
            response = input("Do you wish to overwrite? [y/N]: ")
            if response.upper() != 'Y':
                return "Closing... "
    except OSError:
        sys.stderr("Failed due to path error. If installing to a custom directory, check that your path exists")
        return None

    print(Symbol.ok + " Cloning {} to {}...".format(package_name, package_path))
    try:
        from git import Repo
        Repo.clone_from(package_url, package_path)

    except ImportError:
        response = input("Failed to import GitPython. Do you wish to install it? [Y/n]: ", default='Y')
        if response.upper() != 'Y':
            sys.stderr("Failed to install packages due to missing python library \"GitPython\"\n"
                       "To install, run 'sudo python -m pip install GitPython'")
            sys.exit("Missing apt package: python-git")

    print(Symbol.success + " %s cloned successfully" % package_name)
    return None


def install_all(directory=Path.packages):
    # Yes it's a troll, no, it's not implemented, and no, I don't plan to. It's a bad idea. :P

    danger_will_robinson()

    response = input("Are you ABSOLUTELY SURE you want to do this!? [y/N] ... ")
    if response.uppercase() == 'Y':
        response = input("REALLY REALLY SURE!? [y/N] ... ")
        if response.uppercase() == 'Y':
            point_of_no_return()
            exit()
        else:
            exit()
    else:
        exit()


# Collects git repos in specified directory and performs a git pull origin master
def upgrade(packages, directory):
    print(Ok + " Upgrading repositories in %s " % directory)

    if len(packages) == 0:

        git_dirs = []
        dirs = FileWalker(directory)

        for dir in dirs:
            if os.path.isdir(dir) and dir.endswith('.git'):
                dir = dir.split('.git')[0]
                print("Updating: ", dir)
                git_dirs.append(dir)

    else:

        git_dirs = []
        dirs = FileWalker(directory)

        for p in packages:
            for dir in dirs:
                if os.path.isdir(dir) and dir.endswith('.git') and p in dir:
                    dir = dir.split('.git')[0]
                    print("Updating: ", dir)
                    git_dirs.append(dir)

    if len(git_dirs) != 0:
        try:
            import git
            for d in git_dirs:

                try:

                    git.cmd.Git(d).pull()
                    print(Success + " %s is now up to date" % d)

                # If the repo requires an approved public key, this script will fail.
                except git.exc.GitCommandError as e:

                    if "Permission denied" in e.stderr:

                        # TODO: Figure out how to use git tokens in this thing...
                        # print(Ok + " Permissions requested. Trying token...")
                        # try :
                        #    <some function that accepts tokens>
                        # except git.exc.GitCommandError:
                        #    print("NOPE. NOT HAPPENIN! @_@")

                        print(Fail + ' You do not have permissions to download this repository. \n' + Ok +
                                     ' If you are trying to upgrade a repository which requires a token or ssh key '
                                     'this must be done manually for now. Sorry, homie! :(')

                    elif "no tracking information" in e.stderr:
                        print(Fail + ' Unable to upgrade. There is no tracking information for ', d)

                    elif "local changes" in e.stderr:
                        print(Fail + " Unable to upgrade because you have made changes to %s. To prevent these "
                                     "changes being overwritten by merge, stash or commit them first." % d)

                    elif "unmerged" in e.stderr:
                        print(Fail + " Unable to upgrade %s due to unmerged changes. Please commit your changes." % d)

                    else:
                        print(Fail + ' Unable to upgrade %s. Reason for failure unknown. Dumping error...' % d)
                        print(e)


        except ImportError:
            response = input("Failed to import GitPython. Do you wish to install it? [Y/n]", default='Y')
            if response is not 'Y':
                sys.stderr("Failed to install packages due to missing python library \"GitPython\"\n"
                           "To install, run 'sudo python -m pip install GitPython'")
                sys.exit("Missing apt package: python-git")

    else:
        print(Fail + " No git directories found. Either your path is incorrect, or you have not installed anything")