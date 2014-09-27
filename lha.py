#!/usr/bin/env python3

import argparse
from amigaextractor import LhaExtractor
import sys

uaem = 'uaem'

parser = argparse.ArgumentParser(description="Amiga command line archive\
extractor supporting FS-UAE Amiga emulator",\
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('command', help='''
x   eXtract archive
e   extract archive without paths
l   list archive contents
v   verbose list archive
t   test archive

''', choices='xelvt')
parse_uaem = parser.add_argument_group('FS-UAE meta file options')
parse_uaem.add_argument('-a', '--always',\
                        help='always write .uaem files (default: auto)',\
                        action='store_const',\
                        const='always', default='auto', dest=uaem)
parse_uaem.add_argument('-n', '--never', help='never write .uaem files',\
                        action='store_const', const='never', default='auto',\
                        dest=uaem)
parser.add_argument('archive', help='LHA archive', type=argparse.FileType('r'))
parser.add_argument('files', help='files to extract (optional)', nargs='*')
parser.add_argument('-d', '--dest', help='destination directory', default='.')
parser.add_argument('-f', '--force', help='overwrite existing files',\
                    action="store_true")
parser.add_argument('-v', '--verbose', help='verbose output',\
                    action="store_true")

args = parser.parse_args()

lha = LhaExtractor(args.archive.name)

if args.command == 'l':
    lha.list_files()
    quit()
elif args.command == 'v':
    lha.list_files(verbose=True)
    quit()
elif args.command == 't':
    lha.testlha()
    quit()
elif args.command == 'e':
    use_paths = False
elif args.command == 'x':
    use_paths = True

if not args.files:
    args.files.append(None)
for xfile in args.files:
    ok, reason = lha.extract(filename=xfile, dest=args.dest,\
                                use_paths=use_paths, verbose=args.verbose,\
                                uaem=args.uaem, overwrite=args.force)
    if not ok:
        break
if not ok:
    sys.stderr.write('Error extracting archive: {0}\n'.format(reason))
    quit(1)
