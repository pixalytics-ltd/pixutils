# Python 2 / 3 compatability
from __future__ import print_function
try:
  basestring
except NameError:
  basestring = str

import requests, re, zipfile, os.path, glob, optparse, getpass, sys, subprocess
import shutil, struct

# Library testing
from pixutils import date_conversion

def main():
    usage = "usage: %prog"
    parser = optparse.OptionParser(usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False);

    (options, args) = parser.parse_args()    

    verb     = options.verbose

    year = 2017
    jday = 45
    print("date_conversion.ymd: ",year,jday)
    year,month,day = date_conversion.ymd(year,jday)
    print(year,month,day)



    print("Finished check")

if __name__ == "__main__":
    main()


#EOF
