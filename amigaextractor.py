#!/usr/bin/env python3

from lhafile import LhaFile
import os.path
import pdb


class LhaExtractor(LhaFile):

    def __init__(self, lha_file_name):
        self.lha_file_name = lha_file_name
        self.lha_file = LhaFile(lha_file_name)
        super(LhaExtractor, self).__init__(lha_file_name)

        self.total_file_size = self.total_compress_size = 0
        for file in self.lha_file.filelist:
            self.total_file_size += file.file_size
            self.total_compress_size += file.compress_size
        self.total_ratio = self.total_compress_size * 100 / (
            self.total_file_size if self.total_file_size else 1)
        self.total_ratio = round(self.total_ratio, 2)

    def list_files(self, verbose=False):
        if not verbose:
            for file in self.lha_file.namelist():
                print(file)
            return
        num_files = len(self.lha_file.filelist)
        print(' PACKED  SIZE   RATIO  METHOD CRC       STAMP           PERM        NAME')
        print('------- ------- ------ ---------- ------------------- -------- --------------')
        for file in self.lha_file.filelist:
            ratio = file.compress_size * 100 / (
                file.file_size if file.file_size else 1)
            print(str(file.compress_size).rjust(7), end=' ')
            print(str(file.file_size).rjust(7), end=' ')
            print('{0:.2f}'.format(ratio).rjust(5), end='% ')
            print(file.compress_type.decode(), end=' ')
            print(hex(file.CRC)[2:].zfill(4), end=' ')
            print(file.date_time.strftime('%F %T'), end=' ')
            print(file.flag_bits, end=' ')
            print(file.filename)
            if file.comment:
                print(' : {0}'.format(file.comment))
        print('------- ------- ------ ---------- ------------------- -------- --------------')
        print(str(self.total_compress_size).rjust(7), end=' ')
        print(str(self.total_file_size).rjust(7), end=' ')
        print('{0:.2f}'.format(self.total_ratio).rjust(5), end='% ')
        print(str(num_files).rjust(40), end=' file(s)\n')
        print(file.create_system)

    def extract(self, filename=None, uaem='auto',
                dest='.', use_paths=True, overwrite=False, verbose=False):
        if filename and filename not in self.lha_file.namelist():
            raise FileNotFoundError('File not found in archive')
        if uaem not in ('auto', 'always', 'never'):
            raise ValueError('uaem must be auto, always or never')
        target_dir = os.path.realpath(dest)
        if not os.path.isdir(target_dir):
            raise FileNotFoundError('Target directory does not exist.')
        if not filename:
            files_to_extract = self.lha_file.namelist()
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
                print(target_file, end=' ')
            if not overwrite and os.path.isfile(target_file):
                #raise FileExistsError('File already exists')
                #continue
                return False, '{0} already exists.'.format(target_file)
            try:
                data = self.lha_file.read(file_to_extract)
            except Exception as e:
                return False, e.args[0]
            with open(target_file, 'wb') as output_file:
                output_file.write(data)
            filenote = self.lha_file.NameToInfo[file_to_extract].comment or ''
            protection_flags = self.lha_file.NameToInfo[
                file_to_extract].flag_bits or '----rwed'
            write_flags = False
            if uaem == 'always':
                write_flags = True
            elif uaem == 'auto':
                if filenote:
                    write_flags = True
                if protection_flags != '----rwed':
                    write_flags = True
            if write_flags:
                file_date = self.lha_file.NameToInfo[
                    file_to_extract].date_time.strftime('%F %T.00')
                uaem_string = '{0} {1} {2}\n'.format(
                    protection_flags, file_date, filenote)
                if verbose:
                    print(uaem_string)
                with open('{0}.uaem'.format(target_file), 'wt') as uaem_file:
                    uaem_file.write(uaem_string)
            if verbose:
                print()
        return True, ''

    def testlha(self):
        is_ok = True
        for file_to_test in self.lha_file.namelist():
            print(file_to_test, end=' --> ')
            try:
                data = self.lha_file.read(file_to_test)
            except Exception as e:
                print(e.args[0])
                is_ok = False
            else:
                print('OK')
        return is_ok

    def printdir(self):
        LhaExtractor.list_files(self, verbose=False)


if __name__ == '__main__':
    pass
