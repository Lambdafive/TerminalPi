# TerminalPi
How to turn a RaspberryPi into a cheap Windows Terminal client.

#Setting up the RaspberryPi from scratch
If you have an SD card with _NOOBS_ already installed then we're going to nuke it from a low-earth-orbit and start again.

We begin by installing the Raspbian distrobution onto a SD card and power up the Pi. 
Go [here](https://www.raspberrypi.org/downloads/raspbian/) and find and download the newest _.zip_ file (Jessie at the time of writing).
Unzip the file to extract the _.img_ file, which will take a while as it's 3Gb in size. Run _W32DiskImager_ to write the _.img_ file to the SD card.

Connect the Pi to a keyboard, HDMI lead/monitor, network. Then insert the SD card into the Pi and connect it to the power. There is no on/off switch for the Pi so it will boot as soon as it has power.

----

## Get the Pi up to speed

Raspbian now boots straight into a GUI. Hit _Ctrl+Alt+F2_ to jump to a terminal. Log in using the details below.

The default user name and password is _pi_ and _raspberry_ respectively. But these will soon get changed.

Once the Pi has booted you'll be shown a blue config screen. If you don't see it and only have a terminal prompt type:

```bash
sudo raspi-config
```

Select:

* 2 Change user password
	+ Pick an adequate password.
* 1 Expand Filesystem
* 3 Boot Options
	+ Select the 'Desktop Autologin' option.
* 8 Advanced Options
	+ A1 Overscan
		- Disable
	+ A2 Hostname
		- Pick a suitable hostname (username-pi for example)

When done hit the -> key twice to select _\<Finish\>_. If you get asked if you want to reboot select no. We'll do it later once everything is updated.

After all of that we should be presented with a command prompt. Which looks a little something like this:

```bash
pi@hostname ~ $
```

Before running updates we'll remove a few big programs that take up unnecessary space. Type:

```bash
sudo aptitude purge wolfram-engine sonic-pi
```
Hit _'y'_ followed by enter when asked if we want to continue.

Sudo lets our limited user account '_pi_' run admin level commands.

Update the firmware on the pi with:

```bash
sudo rpi-update
```

Then update the software repository and then upgrade the base system to the latest and greatest versions

```bash
sudo aptitude update && sudo aptitude full-upgrade -y 
```

After waiting for the little old Pi to chugg along and download, and then install everything we need to configure the system with the correct timezone data. This is done with the following command:

```bash
sudo dpkg-reconfigure tzdata
```
Select _Europe_ and _London_ from the menu options

Install the software needed with the following command:

```bash
sudo aptitude install rdesktop ntpdate usbmount avahi-daemon
```
This will install some software tools that will be useful later on.

+ _rdesktop_: A remote desktop client.
+ _ntpdate_: Tools to sync the system time with a remote timeserver. Required because the RaspberryPi doesn't have a hardware clock and the system time is liable to drift unless regularly kept in sync with an external source.
+ _usbmount_: Tool that auto mounts a Flash pen to a directory we can access via the remote session
+ _avahi-daemon_: Avahi allows us to access the pi remotely using _hostname.local_ instead of via IP. It does require bonjour/mDNS software installed on the client pc though (if you've installed iTunes on your pc you have it).

----

## Configure RPD script
Now use [git](https://en.wikipedia.org/wiki/Git_(software)) to get the latest version of the script that we will use to run the remote desktop software.

```bash
git clone https://github.com/Lambdafive/TerminalPi.git

cp terminalpi/rdp.py ~/
```

'_cp_' copies the _rdp.py_ script from the _terminalpi_ directory and places it into our users home directory (_~/_ is a shortcut to our home directory).


Next up we will use a command line based text editor to edit various config files and scripts.
The editor we will use is called _Nano_. Use the arrow keys to move the cursor. _Ctrl+X_ exits and
 _Ctrl+O_ will save a file (write Out). Type out:
 
```bash
nano rdp.py
```

Edit the _user, domain_ & _server_ variables to whatever you require and hit _Ctrl+X_ followed by _y_ and then hit _enter_ to save and exit.
 
----

## Configure Usbconf

Usbconf lets us deal with flash pens while the system is running. It mounts the pen to a directory, gives it proper permissions etc. Open the config file with:

```bash
sudo nano /etc/usbmount/usbmount.conf
```

Find lines that start with the variables below and edit their contents to match what's below.

```bash
MOUNTPOINTS="/media/usb0 /media/usb1"
MOUNTOPTIONS="sync,noexec,nodev,noatime,nodiratime,rw,user"
FS_MOUNTOPTIONS="-fstype=vfat,uid=1000,gid=1000"
```

Hit _Ctrl+X_ to save.

----

## Add scheduled tasks

We'll use the [cron daemon](https://en.wikipedia.org/wiki/Cron) to schedule some tasks to run at certain times. To edit the cron configuration type:

```bash
sudo crontab -e 
```

Which will open it in Nano. Scroll to the bottom and type the following (ensure the spaces are correct!)

```bash
0 4 * * * sudo shutdown -rF now
0 */12 * * * sudo ntpdate -u 192.168.1.80
```

Hit _Ctrl+X_ to exit and save. (_192.168.1.80_ is the ip address of the NTP server. A domain name will also work).

----

## Remove the User Interface
By default the RaspberryPi will boot to a GUI. But we would prefer that there is no GUI available and the 
only thing the users can see is an RDP logon window. This is where that happens.

```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```

This will open a file using Nano. Comment out the top 3 existing lines with _#_ and add `@/usr/bin/python3 /home/pi/rdp.py` to 
the bottom so that the file looks like this:

```bash
#@lxpanel -profile LXDE
#@pcmanfm -desktop -profile LXDE
#@xscreensaver -no-splash
@sh ${HOME}/.config/lxsession/LXDE-pi/autokey.sh
@/usr/bin/python3 /home/pi/rdp.py
```
Hit _Ctrl+X_ to save. Then go:

```bash
cd /etc/xdg/openbox/

sudo cp menu.xml menu.xml.backup

sudo nano menu.xml
```
First we navigate to the correct directory and create a backup of _menu.xml_ Then using nano we need to
 edit _menu.xml_ and remove all the text between the `<menu> </menu>` tags.

```xml
<menu id="root-menu" label-"Openbox 3">
...snip...
</menu>
```
**Bonus Challenge:** You could use `<!--` and `-->` to comment out everything between the `<menu>...</menu>` tags.

Hit _Ctrl+X_ to exit and save.

And that's it. Hit `sudo reboot` to reboot and (fingers crossed) be presented with an RDP Logon screen (See below for notes on connecting to Windows Server 2012 servers).

If you're at the login screen and need to access the command line _Ctrl+Alt+F1_ will drop you at a login
 prompt (username: _pi_). When your done use the `logout` command to leave and then _Ctrl+Alt+F7_ will get you back to the GUI.
 
Connecting to Server 2012
====

Version 1.7.* of Rdesktop won't connect to terminal servers running Windows 2012. Version 1.8.3 does but at the time of writing it isn't in the Raspbian repository, but this can be solved by grabbing the source code and compling it on the Pi.

Make sure the repositories are up to date with `sudo aptitude update && sudo aptitude full-upgrade` if you haven't done it in a while. 

First lets get a copy of the source via _wget_. Make sure you're in the home directory with `cd ~`. Then enter:

```bash
wget https://github.com/rdesktop/rdesktop/releases/download/v1.8.3/rdesktop-1.8.3.tar.gz
tar -zxvf rdesktop-1.8.3.tar.gz
```
This will download the tarred and gzipped file and then unpack it into the home folder. Before we start compling we need to install a few required developement packages and to remove the default version of rdesktop.

```bash
sudo aptitude install libx11-dev libgssglue-dev libgssglue1 libssl-dev
sudo aptitude remove rdesktop
```

Now we can start the compilation process. 

```bash
cd rdesktop-1.8.3 
./configure --disable-smartcard
make
sudo make install
```

The configure will check that all the dependencies for the compilation are installed if this throws an error you probably need to install a dev package. [Google is your friend](https://www.google.com). The `--disable-smartcard` option does what it says on the tin. If you need smartcard support, leave it off and deal with any extra packages you may need to install. `Make` will compile and `make install` will copy the files to their required locations. 

Reboot.

**Note:** You may get an error that mentions 'Credssp'. Check out this link [](http://devnops.blogspot.co.uk/2015/08/rdesktop-failed-to-connect-credssp.html) 


License
=====
This documentation is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License.](http://creativecommons.org/licenses/by-sa/4.0/)
