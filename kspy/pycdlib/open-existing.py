# This is a simple example program to show how to use PyCdlib to open up an
# existing ISO passed on the command-line, and print out all of the file names
# at the root of the ISO.

# Import standard python modules.
import sys

# Import pycdlib itself.
import pycdlib

# Create a new PyCdlib object.
iso = pycdlib.PyCdlib()

# Open up a file object.  This causes PyCdlib to parse all of the metadata on the
# ISO, which is used for later manipulation.
iso.open('''e:\ISO\VMware-ESXi-6.7.0.update01.iso''')

# Now iterate through each of the files on the root of the ISO, printing out
# their names.
for child in iso.list_children(iso_path='/'):
    print(child.file_identifier())

# Close the ISO object.  After this call, the PyCdlib object has forgotten
# everything about the previous ISO, and can be re-used.
iso.close()
