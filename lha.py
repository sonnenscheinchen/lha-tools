#!/usr/bin/env python3

from amigaextractor import LhaExtractor
import sys

target_dir = '.'
verbose = False
app_name = sys.argv[0]
args = sys.argv[1:]


def usage(app_name=app_name):
    print('usage: lha [-]{xelv[vfi]}[w=<dir>] archive_file [file...]')
    print('commands:                          options:')
    print(' x   EXtract from archive')
    print(' e   Extract without paths')
    print(' l,v List / Verbose List')
    print(' t   Test file CRC in archive')
    print()
    print()
    print()
    quit()


if not args or args[0].strip('-') not in ('x', 'e', 'l', 'v', 't'):
    sys.stderr.write('Missing or wrong command.\n')
    usage()
else:
    arg_command = args.pop(0)

try:
    archive_name = args.pop(0)
except IndexError:
    sys.stderr.write('Missing archive name.\n')
    usage()

for arg in args:
    if arg.startswith('w='):
        target_dir = arg[2:]
    elif arg == '-v':
        verbose = True

print(args)
print(target_dir)
print(verbose)
print(arg_command)
print(archive_name)

lha = LhaExtractor(archive_name)

ok = True
if arg_command == 'x':
    ok, reason = lha.extract(dest=target_dir, use_paths=True, verbose=True)
elif arg_command == 'e':
    ok, reason = lha.extract(dest=target_dir, use_paths=False, verbose=True)

if not ok:
    sys.stderr.write('Error extracting archive: {0}'.format(reason))
    quit(1)

if arg_command == 'l':
    lha.printdir()
elif arg_command == 'v':
    lha.list_files(verbose=True)
elif arg_command == 't':
    lha.testlha()
