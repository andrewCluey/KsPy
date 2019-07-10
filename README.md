# ksPy
Simple Python package that will accept user input, creates a kickstart file that is then saved to a vSphere ISO image.

ISO image can then be mounted to a bare metal server for a scripted build.

ks.cfg currently configures the following settings:
- Core VMKernel management settings to a local vSwitch (IP, SUbnet, DNS etc).
- sets root password.

## Future changes
- Make passing arguments easier with validated inputs (argparse/CLi/Menu etc).
- auto mount the ISO to a specified server and power on (possibly change boot order of server to boot from ISO first).
- expand ks.cfg file to finalise more host config (hardening, users, AD etc).
- move ks.cfg to a separate template file of some sort. 