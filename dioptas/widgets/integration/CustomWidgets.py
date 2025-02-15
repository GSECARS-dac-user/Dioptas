# -*- coding: utf-8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray diffraction data
# Principal author: Clemens Prescher (clemens.prescher@gmail.com)
# Copyright (C) 2014-2019 GSECARS, University of Chicago, USA
# Copyright (C) 2015-2018 Institute for Geology and Mineralogy, University of Cologne, Germany
# Copyright (C) 2019 DESY, Hamburg, Germany
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from qtpy import QtWidgets, QtGui, QtCore

from ..CustomWidgets import LabelAlignRight, FlatButton, HorizontalSpacerItem, HorizontalLine


class MouseCurrentAndClickedWidget(QtWidgets.QWidget):
    def __init__(self, clicked_color):
        super(MouseCurrentAndClickedWidget, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.cur_pos_widget = MousePositionWidget()
        self.clicked_pos_widget = MousePositionWidget(clicked_color)

        self._layout.addWidget(self.cur_pos_widget)
        self._layout.addWidget(self.clicked_pos_widget)

        self.setLayout(self._layout)


class MousePositionWidget(QtWidgets.QWidget):
    def __init__(self, color=None):
        super(MousePositionWidget, self).__init__()

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.x_pos_lbl = QtWidgets.QLabel('X:')
        self.y_pos_lbl = QtWidgets.QLabel('Y:')
        self.int_lbl = QtWidgets.QLabel('I:')

        self._layout.addWidget(self.x_pos_lbl)
        self._layout.addWidget(self.y_pos_lbl)
        self._layout.addWidget(self.int_lbl)

        self.setLayout(self._layout)
        self.style_widgets(color)

    def style_widgets(self, color):
        main_style_str = """
            QLabel {
                min-width: 70px;
            }
        """
        self.setStyleSheet(main_style_str)

        if color is not None:
            style_str = 'color: {};'.format(color)
            self.x_pos_lbl.setStyleSheet(style_str)
            self.y_pos_lbl.setStyleSheet(style_str)
            self.int_lbl.setStyleSheet(style_str)


class MouseUnitCurrentAndClickedWidget(QtWidgets.QWidget):
    def __init__(self, clicked_color):
        super(MouseUnitCurrentAndClickedWidget, self).__init__()
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.cur_unit_widget = MouseUnitWidget()
        self.clicked_unit_widget = MouseUnitWidget(clicked_color)

        self._layout.addWidget(self.cur_unit_widget)
        self._layout.addWidget(self.clicked_unit_widget)

        self.setLayout(self._layout)


class MouseUnitWidget(QtWidgets.QWidget):
    def __init__(self, color=None):
        super(MouseUnitWidget, self).__init__()

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.tth_lbl = QtWidgets.QLabel(u"2θ:")
        self.q_lbl = QtWidgets.QLabel('Q:')
        self.d_lbl = QtWidgets.QLabel('d:')
        self.azi_lbl = QtWidgets.QLabel('X:')

        self._layout.addWidget(self.tth_lbl)
        self._layout.addWidget(self.q_lbl)
        self._layout.addWidget(self.d_lbl)
        self._layout.addWidget(self.azi_lbl)

        self.setLayout(self._layout)
        self.style_widgets(color)

    def style_widgets(self, color):
        main_style_str = """
            QLabel {
                min-width: 70px;
            }
        """
        self.setStyleSheet(main_style_str)

        if color is not None:
            style_str = 'color: {};'.format(color)
            self.tth_lbl.setStyleSheet(style_str)
            self.d_lbl.setStyleSheet(style_str)
            self.q_lbl.setStyleSheet(style_str)
            self.azi_lbl.setStyleSheet(style_str)


class BrowseFileWidget(QtWidgets.QGroupBox):
    def __init__(self, files, checkbox_text):
        super(BrowseFileWidget, self).__init__()

        self._layout = QtWidgets.QGridLayout()
        self._layout.setContentsMargins(5, 8, 5, 7)
        # self._layout.setSpacing(3)

        self.load_btn = FlatButton('Load {}(s)'.format(files))
        self.file_cb = QtWidgets.QCheckBox(checkbox_text)

        self._load_layout = QtWidgets.QVBoxLayout()
        self._load_layout.setContentsMargins(5, 0, 0, 5)
        self._load_layout.addWidget(self.load_btn)
        self._load_layout.addWidget(self.file_cb)

        self._layout.addLayout(self._load_layout, 0, 0, 2, 1)

        self.directory_txt = QtWidgets.QLineEdit('')
        self.directory_btn = FlatButton('...')
        self.file_txt = QtWidgets.QLineEdit('')

        self.step_file_widget = StepFileWidget()
        self._layout.addWidget(self.step_file_widget, 0, 1, 2, 2)
        self.step_series_widget = StepFrameWidget()
        self._layout.addWidget(self.step_series_widget, 0, 3, 2, 2)

        self.step_series_widget.setVisible(False)

        self._layout.addWidget(self.file_txt, 2, 0, 1, 5)
        self._directory_layout = QtWidgets.QHBoxLayout()
        self._directory_layout.addWidget(self.directory_txt)
        self._directory_layout.addWidget(self.directory_btn)
        self._layout.addLayout(self._directory_layout, 3, 0, 1, 5)
        self._layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum,
                                                   QtWidgets.QSizePolicy.Minimum), 1, 5)

        self.setLayout(self._layout)

        self.style_widgets()

    def style_widgets(self):
        self.load_btn.setMaximumWidth(120)
        self.load_btn.setMinimumWidth(120)
        self.load_btn.setMinimumHeight(22)

        small_btn_width = 35
        self.directory_btn.setMaximumWidth(small_btn_width)
        self.directory_btn.setMinimumWidth(small_btn_width)

        self.setStyleSheet("""
               QPushButton {
                   height: 22 px;
               }
               """)


class StepWidget(QtWidgets.QWidget):
    """Widget with buttons to step a number up and down and a Spinbox with the step size"""
    iteration_name = ''

    def __init__(self):
        super(StepWidget, self).__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        self.small_btn_max_width = 50
        self.small_btn_min_width = 20

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(5, 0, 0, 5)
        self.init_navigator()

        self.setLayout(self._layout)

    def init_navigator(self):
        self.next_btn = FlatButton('>')
        self.next_btn.setToolTip('Loads next {}'.format(self.iteration_name))
        self.previous_btn = FlatButton('<')
        self.previous_btn.setToolTip(('Loads previous {}'.format(self.iteration_name)))
        self.step_txt = QtWidgets.QSpinBox()
        self.step_txt.setValue(1)
        self.step_txt.setRange(1, 10000)

        self.next_btn.setMaximumWidth(self.small_btn_max_width)
        self.previous_btn.setMaximumWidth(self.small_btn_max_width)
        self.next_btn.setMinimumWidth(self.small_btn_min_width)
        self.previous_btn.setMinimumWidth(self.small_btn_min_width)
        self.step_txt.setMinimumWidth(25)

        self._navigator_layout = QtWidgets.QGridLayout()
        self._navigator_layout.addWidget(self.previous_btn, 0, 0)
        self._navigator_layout.addWidget(self.next_btn, 0, 1)
        self._step_layout = QtWidgets.QHBoxLayout()
        self._step_layout.addWidget(LabelAlignRight('Step:'))
        self._step_layout.addWidget(self.step_txt)
        self._navigator_layout.addLayout(self._step_layout, 1, 0, 1, 2)
        self._layout.addLayout(self._navigator_layout)


class StepFileWidget(StepWidget):
    iteration_name = 'file'

    def __init__(self):
        super(StepFileWidget, self).__init__()
        self.browse_by_name_rb = QtWidgets.QRadioButton('By Name')
        self.browse_by_name_rb.setChecked(True)
        self.browse_by_time_rb = QtWidgets.QRadioButton('By Time')

        self._step_by_layout = QtWidgets.QVBoxLayout()
        self._step_by_layout.addWidget(self.browse_by_name_rb)
        self._step_by_layout.addWidget(self.browse_by_time_rb)
        self._layout.addLayout(self._step_by_layout)


class StepFrameWidget(StepWidget):
    iteration_name = 'frame'

    def __init__(self):
        super(StepFrameWidget, self).__init__()
        self.pos_txt = QtWidgets.QLineEdit()
        self.pos_validator = QtGui.QIntValidator(1, 1)
        self.pos_txt.setValidator(self.pos_validator)
        self.pos_txt.setToolTip('Currently loaded frame')
        self.pos_label = QtWidgets.QLabel('Frame:')
        self.pos_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self._pos_layout = QtWidgets.QVBoxLayout()
        self._pos_layout.addWidget(self.pos_label)
        self._pos_layout.addWidget(self.pos_txt)
        self._layout.addLayout(self._pos_layout)

        self.pos_txt.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
