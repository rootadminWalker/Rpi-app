#!/opt/miniconda3/bin/python
import os
import sys

if len(sys.argv) != 1:
	os.system("git config credential.helper 'cache --timeout=%s'" % sys.argv[0])
	print("Ok")

else:
	print("Missing parameter 'second'")

