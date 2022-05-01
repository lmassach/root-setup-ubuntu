# ROOT setup for Ubuntu
Automatic downloader/compiler/installer script for [ROOT](https://root.cern.ch/) on Ubuntu-based distributions, distributed under the GNU GPL v3.

## How to use
Download and launch the `root_setup.py` file:
```bash
wget https://github.com/lmassach/root-setup-ubuntu/raw/main/root_setup.py
chmod +x root_setup.py
./root_setup.py
```
This will:
 - create a `root` directory in your home (i.e. `~/root`);
 - copy the script in it;
 - clone the [ROOT repo](https://github.com/root-project/root/) in `~/root/root` and switch to the `latest-stable` branch;
 - install the dependencies (this will run `sudo apt -y install [...]`: you may be asked for yor password);
 - configure ROOT to be built in `~/root/build` and installed in `~/root/install`;
 - compile ROOT - this usually takes order of an hour and will use all the available CPU cores.

For more options, see `./root_setup.py --help`.

## Extra: opening ROOT files from the file explorer
How to setup the `fileopen` macro to be used by the desktop shell (tested for GNOME):
 - create a shell script `~/root/do_fileopen.sh` with the following content and make it executable;
   ```bash
   #!/bin/bash
   source ~/root/install/bin/thisroot.sh
   root "$1" ~/root/install/macros/fileopen.C
   ```
 - create a desktop file `~/.local/share/applications/root_fileopen.desktop` with the following content;
   ```
   [Desktop Entry]
   Comment=
   Terminal=true
   Name=root_fileopen
   Exec=~/root/do_fileopen.sh %f
   Type=Application
   Icon=~/root/install/icons/Root6Icon.png
   Encoding=UTF-8
   Hidden=false
   NoDisplay=false
   ```
 - try to open a `.root` file by double-clicking, and select to use _root_fileopen_ to open it.

In the above steps, you might have to replace `~` with the absolute path to your home.
You might also want to add the `--web=off` to the ROOT command if you want the old `TBrowser` window to be used (instead of the new web-based browser introduced in ROOT 6.26).
