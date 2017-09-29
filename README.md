# gitkali
The friendly, undescriminating, cross-platform kali and pentesting tool installer for Linux and Windows*

This package manager works similar to apt-get:
sudo ./gitkali.py {options} -args- <command>
Commands: **search**    - Search package listings for matching terms
          **update**    - Update your package listings
          **install**   - Installs the package via sudo git clone -v {package_path}
          **upgrade**   - Upgrades the package via sudo git pull origin master
Options:
          -h, --help      - Show this help message and exit
          -d, --directory - Specify the directory to install/upgrade packages (default: /usr/share)
          
*Windows compatibility still in the works

This script is currently in alpha stage, so please anticipate there will be bugs. 
Auto-tab completion is not implemented, and you currently cannot execute it 
from another directory other than where the executable gitkali.py is located.

Many other features are planned, but please submit ideas and issues.
