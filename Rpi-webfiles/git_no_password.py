#!/opt/miniconda3/bin/python
import os
import sys

if len(sys.argv) != 1:
	command = "git config credential.helper 'cache --timeout=%s'" % (sys.argv[1])
	os.system(command)
	print("excuted command %s" % command)
	print("Ok")


else:
	print("Missing parameter 'second'")

