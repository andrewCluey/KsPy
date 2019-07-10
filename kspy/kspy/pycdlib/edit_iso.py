# Import standard python modules.
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

# Import pycdlib itself.
import pycdlib

# Create a new PyCdlib object.
iso = pycdlib.PyCdlib()

# Open up a file object.  This causes PyCdlib to parse all of the metadata on the
# ISO, which is used for later manipulation.
iso.open("e:\iso\VMware-ESXi-6.7.0.update01.iso")

ksstr = b'''


'''

iso.modify_file_in_place(BytesIO(ksstr), len(ksstr), '/KS_CUST.CFG;1')

modifiediso = BytesIO()
iso.write_fp(modifiediso)
iso.close()


# Close the ISO object.  After this call, the PyCdlib object has forgotten
# everything about the previous ISO, and can be re-used.
iso.close()