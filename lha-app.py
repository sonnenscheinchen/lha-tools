#!/usr/bin/env python3

import sys
import os.path
from PyQt4 import QtGui, uic
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
#from amigaextractor import LhaExtractor
import amigaextractor


class LHAExtractorApp(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("lha-app.ui", self)
        self.ui.pbt_select.clicked.connect(self.onSelect)
        self.ui.pbt_doit.clicked.connect(self.onDoit)
        self.ui.pbt_exit.clicked.connect(self.onExit)
        self.ui.pbt_doit.setEnabled(False)
        self.archivename = None
        try:
            self.archivename = sys.argv[1]
        except IndexError:
            self.ui.statusbar.showMessage(
                'Click \"Select archive\" to display its contents.')
        else:
            if os.path.isfile(self.archivename):
                self.onSelect()
            else:
                self.ui.statusbar.showMessage(
                    'Unsupported archive: {0}'.format(self.archivename))
                self.archivename = None
                
    def onSelect(self):
        if not self.archivename:
            self.archivename = QtGui.QFileDialog.getOpenFileName(
                    self, 'Open file', filter=("LHA archive files (*.lha *.lzh)"))
        if not self.archivename:
            return
        try:
            self.lha = amigaextractor.LhaExtractor(self.archivename)
        except:
            self.ui.statusbar.showMessage(
                'Unsupported archive: {0}'.format(self.archivename))
            return
        self.ui.le_archive.setText(self.archivename)
        self.tw_contents.setRowCount(len(self.lha.filelist))
        rowcount = 0
        for arc_file in self.lha.filelist:
            ratio = arc_file.compress_size * 100 / (
                arc_file.file_size if arc_file.file_size else 1)

            item0 = QtGui.QTableWidgetItem(arc_file.flag_bits)

            item1 = QtGui.QTableWidgetItem()
            item1.setData(Qt.DisplayRole, str('{0:n}'.format(arc_file.compress_size)))
            item1.setData(Qt.TextAlignmentRole, Qt.AlignRight)

            item2 = QtGui.QTableWidgetItem()
            item2.setData(Qt.DisplayRole, str('{0:n}'.format(arc_file.file_size)))
            item2.setData(Qt.TextAlignmentRole, Qt.AlignRight)

            item3 = QtGui.QTableWidgetItem()
            item3.setData(Qt.DisplayRole, str('{0:.2f}'.format(ratio)))
            item3.setData(Qt.TextAlignmentRole, Qt.AlignRight)

            item4 = QtGui.QTableWidgetItem()
            item4.setData(Qt.DisplayRole, arc_file.compress_type.decode())
            item4.setData(Qt.TextAlignmentRole, Qt.AlignCenter)

            item5 = QtGui.QTableWidgetItem(arc_file.date_time.strftime(
                '%F %T'))

            item6 = QtGui.QTableWidgetItem(arc_file.comment)

            item7 = QtGui.QTableWidgetItem(arc_file.filename)

            items = (item0, item1, item2, item3, item4, item5, item6, item7)

            for value in zip(items, range(8)):
                self.tw_contents.setItem(rowcount, value[1], value[0])

            rowcount += 1

        message = 'Total: file size:  {0:n} Bytes, compressed: {1:n} Bytes, ratio: {2}%'.format(
                self.lha.total_file_size, self.lha.total_compress_size, self.lha.total_ratio)
        self.ui.statusbar.showMessage(message)
        self.ui.pbt_doit.setEnabled(True)

        hheader = self.tw_contents.horizontalHeader()
        hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        #vheader = self.tw_contents.verticalHeader()
        #vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)


    def onDoit(self):
        if not self.tw_contents.selectedItems() and self.rbt_extr_selected.isChecked():
            self.ui.statusbar.showMessage('Please select some files first.')
            return

        if self.rbt_uaem_always.isChecked():
            uaem = 'always'
        elif self.rbt_uaem_auto.isChecked():
            uaem = 'auto'
        else:
            uaem = 'never'

        overwrite = True if self.cb_opts_overwrite.isChecked() else False
        use_paths = True if self.cb_opts_paths.isChecked() else False
        output_dir = QtGui.QFileDialog.getExistingDirectory(
            self, 'Select an output directory')

        if not output_dir:
            return

        self.ui.pbt_doit.setEnabled(False)
        self.ui.pbt_select.setEnabled(False)
        self.ui.statusbar.showMessage('Working hard. Please wait.')

        file_list = []
        if self.rbt_extr_all.isChecked():
            file_list.append(None)
        else:
            selected_items = self.tw_contents.selectedItems()
            selected_rows = set()
            for tw_item in selected_items:
                selected_rows.add(tw_item.row())
            for row in selected_rows:
                file_list.append(self.lha.namelist()[row])
        for filename in file_list:
            ok, reason = self.lha.extract(filename=filename, uaem=uaem, dest=output_dir,
                             use_paths=use_paths, overwrite=overwrite)
            if not ok:
                break

        if not ok:
            self.ui.statusbar.showMessage(
                'Error while extracting archive: {0}'.format(reason))
        else:
            self.ui.statusbar.showMessage('Done.')

        self.ui.pbt_doit.setEnabled(True)
        self.ui.pbt_select.setEnabled(True)

    def onExit(self):
        QtCore.QCoreApplication.instance().quit()


app = QtGui.QApplication(sys.argv)
lha_app = LHAExtractorApp()
lha_app.show()
sys.exit(app.exec_())
