*********************Mininet Installation************************

Installation from Packages
If you’re running a recent Ubuntu release, or Debian 11+, you can install the Mininet packages. Note that this may give you an older version of Mininet, but it can be a very convenient way to get started.

To confirm which OS version you are running, run the command

lsb_release -a
Next, install the base Mininet package by entering only one of the following commands, corresponding to the distribution you are running:

Mininet 2.3.0 on Debian 11: sudo apt-get install mininet
Mininet 2.2.2 on Ubuntu 20.04 LTS: sudo apt-get install mininet
Mininet 2.2.2 on Ubuntu 18.04 LTS: sudo apt-get install mininet
If it’s not obvious which Mininet version you have, you can try:

mn --version
Mininet supports multiple switches and OpenFlow controllers. For this test, we will use Open vSwitch in bridge/standalone mode.

To test this, try:

sudo mn --switch ovsbr --test pingall
If Mininet complains that Open vSwitch isn’t working, make sure it is installed and running:

sudo apt-get install openvswitch-switch
sudo service openvswitch-switch start
If you wish to go through the Mininet walkthrough, you will want to install additional software. The following commands

git clone https://github.com/mininet/mininet
mininet/util/install.sh -fw
will install the OpenFlow reference switch, reference controller and Wireshark dissector.










*************** Installation Floodlight***********************
Prerequisites
Linux
Your favorite flavor of Linux
Java development kit
JDK 8 for Floodlight master and above
JDK 7 for Floodlight v1.2 and below
Ant or Maven to build
Python development package
Eclipse IDE (Eclipse Luna Preferred)
Floodlight Master and Above
To download Java 8, please refer to these instructions. Please download the latest version of Eclipse, making sure the version you choose supports Java 8. To download remaining dependencies for Floodlight master and above:

Eclipse Luna version is recommended to successfully import Floodlight project. Other Eclipse version would work as well, just people sometimes might have trouble on configuring those versions(most of time, JDK issues and "unresolved compilation problem"). This tutorial is written and tested with Eclipse Luna version so that version is recommended. For Floodlight master branch, you should still ensure to have Java 8 installed in your environment and JDK 1.8 is correctly configured at Eclipse. 



sudo apt-get install build-essential ant maven python-dev
Floodlight v1.2 and Below
To download dependencies for Floodlight v1.2 and below:

sudo apt-get install build-essential openjdk-7-jdk ant maven python-dev eclipse
Mac
Mac OS X 10.6 or higher: older versions may work but have not been tested
Xcode 4.1 (for 10.7 Lion) or Xcode 4.0.2 (for 10.6 Snow Leopard) (includes gcc, make, git, etc.)
Java; just type 'javac' in a Terminal; this should automatically install the JDK if it isn't already present
Java 8 for Floodlight master and above
Java 7 for Floodlight v1.2 and below
Latest version of Eclipse
Note: Want to get started fast? You can use our VM here, which already includes the above dependencies for Floodlight v1.2 and below.

Windows
Floodlight is written in Java, so it should work in Windows; however, specific instructions are not provided aside from this helpful site for using ant on Windows and this helpful site that documents how to use git on Windows. If you wish to use Windows, do so at your own risk or use our Floodlight Linux VM instead.

Download And Build
Floodlight is simple to download from Github and build. Please follow the following steps to either download and install a new copy of Floodlight or update an existing installation of Floodlight:

Installing Floodlight from Scratch
The "git clone" step below uses the master version of Floodlight. To use a specific version, specify the version branch in the "git clone" step by appending "-b <branch-name>", e.g. "-b v1.2".

$ git clone git://github.com/floodlight/floodlight.git
$ cd floodlight
$ git submodule init
$ git submodule update
$ ant
 
$ sudo mkdir /var/lib/floodlight
$ sudo chmod 777 /var/lib/floodlight
Updating an Existing Floodlight Installation
The following steps show how to update Floodlight to master. Substitute "master" in the "git pull" step with your desired version's branch, e.g. "v1.1", "v1.2", etc. if you would like to switch to a different version.

$ cd floodlight
$ git pull origin master
$ git submodule init
$ git submodule update
If you are upgrading from Floodlight v1.2 or below to a newer version or the master branch, you should update to Java 8 at this point. Others should already have Java 8 installed or do not require it (if downgrading to v1.2 or below). Once you have satisfied this requirement, proceed with re-building the controller:

$ ant
Running Floodlight in the Terminal
Assuming java is in your path, you can directly run the floodlight.jar file produced by ant from within the floodlight directory:

$ java -jar target/floodlight.jar
Floodlight will start running and print log and debug output to your console. If you would like to save your log, you can redirect it to a file.

Eclipse IDE
Developing Floodlight in Eclipse
Its also possible to setup, develop and run Floodlight through Eclipse. Rather than setting up projects manually, its easily to use the Eclipse ant target.

$ ant eclipse
This creates several files: Floodlight.launch, Floodlight_junit.launch, .classpath, and .project. From these you can setup a new Eclipse project.

Open eclipse and create a new workspace
File -> Import -> General -> Existing Projects into Workspace. Then click "Next".
From "Select root directory" click "Browse". Select the parent directory where you placed floodlight earlier.
Check the box for "Floodlight". No other Projects should be present and none should be selected.
Click Finish.
You now have a working Eclipse project for Floodlight. You can run the project directly through Eclipse as well. Since we use a dynamic module loading system to run Floodlight, we must configure Eclipse to launch it in the correct manner.

Running Floodlight in Eclipse
Create the FloodlightLaunch target:

Click Run->Run Configurations
Right Click Java Application->New
For Name use FloodlightLaunch
For Project use Floodlight
For Main use net.floodlightcontroller.core.Main
Click Apply
To then run Floodlight click on the drop-down arrow next to the Play button and select the proper target to run. These also work with debug targets.

Simulating A Network
Now that Floodlight is running, you need to attach it to an OpenFlow network. One of the best tools for this is Mininet, a network simulation tool.

Download the Floodlight VM. It includes Floodlight and Mininet.
Start it in VMware Fusion or VirtualBox
Login (username is floodlight and password is floodlight)
Its possible to run Mininet against the locally running Floodlight (just type "sudo mn") but you can also run it against a remote controller you built as well.  To do that, type:
$ sudo mn --controller=remote,ip=<controller ip>,port=6653 --switch ovsk,protocols=OpenFlow13
Optionally run wireshark over ssh. Listen on "eth0? and filter for packets with "of" names.

$ ssh -X floodlight@<vm-ip>
$ sudo wireshark



