#!/usr/bin/env python3

from lhafile import LhaFile
import os.path


class LhaExtractor(LhaFile):

    def __init__(self, lha_file_name, *args, **kwargs):
        super().__init__(lha_file_name, *args, **kwargs)
        self.total_file_size = sum(
            [ f.file_size for f in self.filelist ])
        self.total_compress_size = sum(
            [ f.compress_size for f in self.filelist ])
        self.total_ratio = self.total_compress_size * 100 / (
            self.total_file_size if self.total_file_size else 1)

    def __write_metadata(self, file_to_extract, target_file, force):
        filenote = self.NameToInfo[file_to_extract].comment or ''
        protection_flags = self.NameToInfo[
            file_to_extract].flag_bits or '----rwed'
        if force is not True:
            if filenote == '' and protection_flags == '----rwed':
                return
        file_date = self.NameToInfo[
            file_to_extract].date_time.strftime('%F %T.00')
        uaem_string = '{0} {1} {2}\n'.format(
            protection_flags, file_date, filenote)
        with open('{0}.uaem'.format(target_file), 'wt') as uaem_file:
            uaem_file.write(uaem_string)

    def list_files(self, verbose=False):
        if not verbose:
            for item in self.namelist():
                print(item)
            return
        num_files = len(self.filelist)
        print(' PACKED  SIZE   RATIO  METHOD CRC       STAMP           PERM        NAME')
        print('------- ------- ------ ---------- ------------------- -------- --------------')
        for item in self.filelist:
            ratio = item.compress_size * 100 / (
                item.file_size if item.file_size else 1)
            print(str(item.compress_size).rjust(7), end=' ')
            print(str(item.file_size).rjust(7), end=' ')
            print('{0:.2f}'.format(ratio).rjust(5), end='% ')
            print(item.compress_type.decode(), end=' ')
            print(hex(item.CRC)[2:].zfill(4), end=' ')
            print(item.date_time.strftime('%F %T'), end=' ')
            print(item.flag_bits, end=' ')
            print(item.filename)
            if item.comment:
                print(' : {0}'.format(item.comment))
        print('------- ------- ------ ---------- ------------------- -------- --------------')
        print(str(self.total_compress_size).rjust(7), end=' ')
        print(str(self.total_file_size).rjust(7), end=' ')
        print('{0:.2f}'.format(self.total_ratio).rjust(5), end='% ')
        print('Created on: {0}'.format(item.create_system).center(30), end=' ')
        print(str(num_files).rjust(10), end=' file(s)\n')

    def extract(self, filename=None, uaem='auto',
                dest='.', use_paths=True, overwrite=False, verbose=False):
        if filename and filename not in self.namelist():
            return False, 'File not found in archive'
        if uaem not in ('auto', 'always', 'never'):
            raise ValueError('uaem must be auto, always or never')
        target_dir = os.path.realpath(dest)
        if not os.path.isdir(target_dir):
            return False, 'Target directory does not exist.'
        if not filename:
            files_to_extract = self.namelist()
        else:
            files_to_extract = [filename]
        for file_to_extract in files_to_extract:
            if not use_paths:
                target_file = os.path.join(
                    target_dir, file_to_extract.split('\\')[-1].split('/')[-1])
            else:
                target_file = os.path.join(
                    target_dir, os.sep.join(file_to_extract.split('\\')))
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
            if verbose:
                print(target_file)
            if not overwrite and os.path.isfile(target_file):
                continue
            try:
                data = self.read(file_to_extract)
            except Exception as e:
                return False, e.args[0]
            with open(target_file, 'wb') as output_file:
                output_file.write(data)

            if uaem == 'always':
                self.__write_metadata(file_to_extract, target_file, force=True)
            elif uaem == 'auto':
                self.__write_metadata(file_to_extract, target_file, force=False)
        return True, ''

    def testlha(self):
        is_ok = True
        for file_to_test in self.namelist():
            print(file_to_test, end=' --> ')
            try:
                data = self.read(file_to_test)
            except Exception as e:
                print(e.args[0])
                is_ok = False
            else:
                print('OK')
        return is_ok

    def printdir(self):
        self.list_files(verbose=False)


if __name__ == '__main__':
    pass
