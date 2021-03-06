#!/usr/bin/env python
'''
beaverAutoCAD is a software for calculating data recieved from AutoCAD DWG,
and creates a MS-Excel file of this data.

Copyright 2013 Shai Efrati

This file is part of beaverAutoCAD.

beaverAutoCAD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

beaverAutoCAD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with beaverAutoCAD.  If not, see <http://www.gnu.org/licenses/>.
'''

__version__ = "0.0.2"

import sys
import pygtk

if not sys.platform == 'win32':
    pygtk.require('2.0')

import gtk
import os.path
import datetime
import beaverAutoCAD_core

if gtk.pygtk_version < (2, 4, 0):
    print "Please install an updated version of pygtk.\nCurrently using pygtk version {}".format(gtk.pygtk_version)
    raise SystemExit

currentDirectory = os.getcwd()
now = datetime.datetime.now()
today_date = "%04d%02d%02d_%02d-%02d" % (now.year, now.month, now.day, now.hour, now.minute)
today_date_designed = "%02d/%02d/%04d %02d:%02d" % (now.day, now.month, now.year, now.hour, now.minute)

tooltiptext = "Automatic AutoCAD Calculations was made by Shai Efrati for NADRASH Ltd. (2013)"

try:
    with open('settings.txt') as settings_file:
        homeDir = settings_file.readline()
        print "File will be saved at: " + homeDir
except IOError:
    homeDir = os.path.expanduser("~" + "\My Documents")
    print 'Warning: No settings file found. Using default directory instead, and creating a settings file.'
    print "File will be saved at: " + homeDir


class PyAPP():
    def __init__(self):
        beaverAutoCAD_core.prompt_ascii_art()
        self.window = gtk.Window()
        self.window.set_title("beaverAutoCAD - Automating AutoCAD Calculations")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.create_widgets()
        self.connect_signals()
        try:
            self.window.set_icon_from_file("SE_Logo25.png")
        except Exception, e:
            print e.message
            sys.exit(1)
        self.window.show_all()
        gtk.main()

    def directory_settings(self):
        dir_name = self.dir_button.get_current_folder()
        print dir_name
        os.chdir(currentDirectory)
        with open("settings.txt", "w") as text_file:
            text_file.write(dir_name)
        filename = self.entry.get_text()
        return dir_name

    def set_file_name(self, filename):
        '''
        This method checks the existance of an XLS file, and allows the user to overwrite it, or use a different file.
        '''
        tableFilename = self.dir_button.get_current_folder() + '\\' + filename + ".xls"
        print tableFilename
        if os.path.isfile(tableFilename):
            md = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_CLOSE, "File " + filename + ".xls exist. Do you want to continue?")
            md.run()
            md.destroy()

    def create_widgets(self):
        self.vbox = gtk.VBox(spacing=10)

        self.hbox_logo = gtk.HBox(spacing=10)
        self.nadrashlogo = gtk.Image()
        self.nadrashlogo.set_from_file("Nadrash25mm90.png")
        self.nadrashlogo.set_tooltip_text(tooltiptext)
        self.hbox_logo.pack_start(self.nadrashlogo)

        self.hbox_file_settings = gtk.HBox(spacing=10)
        self.dir_button = gtk.FileChooserButton(title="Choose directory")
        self.dir_button.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.dir_button.set_tooltip_text("This is where your file will be saved")
        self.hbox_file_settings.pack_start(self.dir_button)
        self.label = gtk.Label("File Name: ")
        self.hbox_file_settings.pack_start(self.label)
        self.entry = gtk.Entry()
        self.hbox_file_settings.pack_start(self.entry)

        self.hbox_options_label = gtk.HBox(spacing=10)
        self.options_label = gtk.Label('OPTIONS')
        self.hbox_options_label.pack_start(self.options_label)

        self.hbox_options_buttons = gtk.HBox(spacing=5)
        self.vbox_options1 = gtk.VBox(spacing=10)
        self.use0Label = gtk.Label("Use layer 0 in calculation: ")
        self.vbox_options1.pack_start(self.use0Label)
        self.use0 = gtk.combo_box_new_text()
        self.use0.append_text('yes')
        self.use0.append_text('no')
        self.use0.set_active(1)
        self.use0.set_tooltip_text(
            "In cases where you don't want to count blocks in layer 0, choose no. Otherwise, choose yes")
        self.vbox_options1.pack_start(self.use0)

        self.unitsLabel = gtk.Label("DWG units: ")
        self.vbox_options1.pack_start(self.unitsLabel)
        self.units = gtk.combo_box_new_text()
        self.units.append_text('m')
        self.units.append_text('cm')
        self.units.append_text('mm')
        self.units.set_active(1)
        self.units.set_tooltip_text("Choose the units you used in the drawing")
        self.vbox_options1.pack_start(self.units)

        self.vbox_options2 = gtk.VBox(spacing=5)
        self.vbox_options2.set_tooltip_text("Case sensitive!")
        self.label = gtk.Label("Layers contain string: ")
        self.vbox_options2.pack_start(self.label)
        self.layers_contain_box = gtk.Entry()
        self.vbox_options2.pack_start(self.layers_contain_box)
        self.label = gtk.Label("Blocks contain string: ")
        self.vbox_options2.pack_start(self.label)
        self.blocks_contain_box = gtk.Entry()
        self.vbox_options2.pack_start(self.blocks_contain_box)

        self.hbox_options_label.pack_start(self.vbox_options1)
        self.hbox_options_label.pack_start(self.vbox_options2)


        self.hbox_functions_label = gtk.HBox(spacing=10)
        self.functions_label = gtk.Label('FUNCTIONS')
        self.hbox_functions_label.pack_start(self.functions_label)

        self.hbox_functions_buttons = gtk.HBox(spacing=10)
        self.vbox_functions_buttons1 = gtk.VBox(spacing=10)
        self.bLineLength = gtk.Button("Sum Lines Lengths in a DWG to MS-Excel")
        self.vbox_functions_buttons1.pack_start(self.bLineLength)
        self.bAreaSum = gtk.Button("Sum Areas in a DWG to MS-Excel")
        self.vbox_functions_buttons1.pack_start(self.bAreaSum)
        self.vbox_functions_buttons2 = gtk.VBox(spacing=10)
        self.bBlocksCount = gtk.Button("Count Blocks in a DWG to MS-Excel")
        self.vbox_functions_buttons2.pack_start(self.bBlocksCount)
        self.bBlocksCountPerLayer = gtk.Button("Count Blocks per layer in a DWG")
        self.vbox_functions_buttons2.pack_start(self.bBlocksCountPerLayer)
        self.hbox_functions_label.pack_start(self.vbox_functions_buttons1)
        self.hbox_functions_label.pack_start(self.vbox_functions_buttons2)

        self.hbox_progress_bar = gtk.HBox(spacing=10)
        self.pbar = gtk.ProgressBar()
        self.hbox_progress_bar.pack_start(self.pbar)
        self.button_exit = gtk.Button("Exit")
        self.hbox_progress_bar.pack_start(self.button_exit)
        self.button_exit.set_tooltip_text("Press to exit...")

        self.hbox_SE_logo = gtk.HBox(spacing=10)
        self.se_logo = gtk.Image()
        self.se_logo.set_from_file("SE_Logo25.png")
        self.hbox_SE_logo.pack_start(self.se_logo)
        self.se_logo.set_tooltip_text(tooltiptext)
        self.verLabel = gtk.Label("GUI Ver. " + __version__ + " // Core Ver. " + beaverAutoCAD_core.__version__)
        self.hbox_SE_logo.pack_start(self.verLabel)

        self.vbox.pack_start(self.hbox_logo)
        self.vbox.pack_start(self.hbox_file_settings)
        self.vbox.pack_start(self.hbox_options_label)
        self.vbox.pack_start(self.hbox_options_buttons)
        self.vbox.pack_start(self.hbox_functions_label)
        self.vbox.pack_start(self.hbox_functions_buttons)
        self.vbox.pack_start(self.hbox_progress_bar)
        self.vbox.pack_start(self.hbox_SE_logo)

        self.window.add(self.vbox)

    def connect_signals(self):
        '''
        This method connects signals to relevant actions
        '''
        self.dir_button.set_current_folder(homeDir)
        # self.filename = self.entry.set_text('temp' + today_date)
        self.filename = self.entry.set_text('{}_{}'.format(beaverAutoCAD_core.acad.ActiveDocument.Name[0:-4],
                                                           today_date))
        self.button_exit.connect("clicked", self.callback_exit)
        self.bLineLength.connect('clicked', self.callback_lines_lengths)
        self.bAreaSum.connect('clicked', self.callback_areas_sum)
        self.bBlocksCount.connect('clicked', self.callback_blocks_count)
        self.bBlocksCountPerLayer.connect('clicked', self.callback_blocks_count_per_layer)
        self.window.connect("destroy", gtk.main_quit)

    def callback_lines_lengths(self, widget, callback_data=None):
        '''
        This method connects the gui to the relevant function in the app's core
        '''
        self.layers_contain = self.layers_contain_box.get_text()
        if self.layers_contain != '':
            print 'Sum line lengths in layers contain: {}'.format(self.layers_contain)
        # self.set_file_name(filename)
        # calls the function from the core:
        # beaverAutoCAD_core.line_lengths_excel(filename, savingPath, draw_units)
        beaverAutoCAD_core.line_lengths_excel(filename="AAC_lines_{}".format(self.entry.get_text()),
                                              savingPath=self.directory_settings(),
                                              draw_units=self.units.get_active_text(),
                                              layers_contain=self.layers_contain)
        print "Done."


    def callback_areas_sum(self, widget, callback_data=None):
        '''
        This method connects the gui to the relevant function in the app's core
        '''
        self.layers_contain = self.layers_contain_box.get_text()
        if self.layers_contain != '':
            print 'Sum areas in layers contain: {}'.format(self.layers_contain)
        # self.set_file_name(filename)
        # calls the function from the core:
        # beaverAutoCAD_core.line_lengths_excel(filename, savingPath, draw_units)
        beaverAutoCAD_core.sum_areas_excel(filename="AAC_areas_{}".format(self.entry.get_text()),
                                           savingPath=self.directory_settings(),
                                           draw_units=self.units.get_active_text(),
                                           layers_contain=self.layers_contain)
        print "Done."


    def callback_blocks_count(self, widget, callback_data=None):
        '''
        This method connects the gui to the relevant function in the app's core
        '''
        # calls the function from the core:
        # beaverAutoCAD_core.count_blocks_excel(filename, savingPath, uselayer0, self.layers_contain)
        self.layers_contain = self.layers_contain_box.get_text()
        self.blocks_contain = self.blocks_contain_box.get_text()
        if self.layers_contain != '':
            print 'Counts blocks in layers contain: {}'.format(self.layers_contain)
        beaverAutoCAD_core.count_blocks_excel(filename="AAC_blocks_{}".format(self.entry.get_text()),
                                              savingPath=self.directory_settings(),
                                              uselayer0=self.use0.get_active_text(),
                                              layers_contain=self.layers_contain,
                                              blocks_contain=self.blocks_contain)
        print "Done."


    def callback_blocks_count_per_layer(self, widget, callback_data=None):
        '''
        This method connects the gui to the relevant function in the app's core
        '''
        self.layers_contain = self.layers_contain_box.get_text()
        self.blocks_contain = self.blocks_contain_box.get_text()
        if self.layers_contain != '':
            print 'Counts blocks in layers contain: {}'.format(self.layers_contain)
        # calls the function from the core:
        beaverAutoCAD_core.count_blocks_per_layer(filename="AAC_blocks_per_layer_{}".format(self.entry.get_text()),
                                                  savingPath=self.directory_settings(),
                                                  uselayer0=self.use0.get_active_text(),
                                                  layers_contain=self.layers_contain,
                                                  blocks_contain=self.blocks_contain)
        print "Done."


    def callback_exit(self, widget, callback_data=None):
        gtk.main_quit()


if __name__ == "__main__":
    app = PyAPP()