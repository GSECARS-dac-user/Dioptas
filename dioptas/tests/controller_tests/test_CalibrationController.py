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

import unittest
from mock import MagicMock
import os
import gc

import numpy as np

from qtpy import QtWidgets, QtCore
from qtpy.QtTest import QTest

from ..utility import QtTest, unittest_data_path, click_button
from ...model.DioptasModel import DioptasModel
from ...controller.CalibrationController import CalibrationController
from ...widgets.CalibrationWidget import CalibrationWidget

# mocking the functions which will block the unittest for some reason...
QtWidgets.QApplication.processEvents = MagicMock()
QtWidgets.QProgressDialog.setValue = MagicMock()


class TestCalibrationController(QtTest):
    def setUp(self):
        self.model = DioptasModel()

        self.calibration_widget = CalibrationWidget()
        self.calibration_controller = CalibrationController(widget=self.calibration_widget,
                                                            dioptas_model=self.model)

    def tearDown(self):
        del self.model
        gc.collect()

    def mock_integrate_functions(self):
        self.model.calibration_model.integrate_1d = MagicMock(return_value=([np.linspace(0, 100), np.linspace(0, 100)]))
        self.model.calibration_model.integrate_2d = MagicMock()

    def test_automatic_calibration(self):
        self.mock_integrate_functions()
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'LaB6_40keV_MarCCD.tif'))
        QTest.mouseClick(self.calibration_widget.load_img_btn, QtCore.Qt.LeftButton)
        self.calibration_controller.search_peaks(1179.6, 1129.4)
        self.calibration_controller.search_peaks(1268.5, 1119.8)
        self.calibration_controller.widget.sv_wavelength_txt.setText('0.31')
        self.calibration_controller.widget.sv_distance_txt.setText('200')
        self.calibration_controller.widget.sv_pixel_width_txt.setText('79')
        self.calibration_controller.widget.sv_pixel_height_txt.setText('79')
        calibrant_index = self.calibration_widget.calibrant_cb.findText('LaB6')
        self.calibration_controller.widget.calibrant_cb.setCurrentIndex(calibrant_index)

        QTest.mouseClick(self.calibration_widget.calibrate_btn, QtCore.Qt.LeftButton)
        self.app.processEvents()
        self.model.calibration_model.integrate_1d.assert_called_once()
        self.model.calibration_model.integrate_2d.assert_called_once()
        self.assertEqual(QtWidgets.QProgressDialog.setValue.call_count, 15)

        calibration_parameter = self.model.calibration_model.get_calibration_parameter()[0]
        self.assertAlmostEqual(calibration_parameter['dist'], .1967, places=4)

    def test_splines(self):
        self.mock_integrate_functions()
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'distortion', 'f4mnew.spline'))
        click_button(self.calibration_widget.load_spline_btn)

        self.assertIsNotNone(self.model.calibration_model.distortion_spline_filename)
        self.assertEqual(self.calibration_widget.spline_filename_txt.text(), 'f4mnew.spline')
        #
        click_button(self.calibration_widget.spline_reset_btn)
        self.assertIsNone(self.model.calibration_model.distortion_spline_filename)
        self.assertEqual(self.calibration_widget.spline_filename_txt.text(), 'None')

    def test_loading_and_saving_of_calibration_files(self):
        self.mock_integrate_functions()
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'LaB6_40keV_MarCCD.poni'))
        QTest.mouseClick(self.calibration_widget.load_calibration_btn, QtCore.Qt.LeftButton)
        QtWidgets.QFileDialog.getSaveFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'calibration.poni'))
        QTest.mouseClick(self.calibration_widget.save_calibration_btn, QtCore.Qt.LeftButton)
        self.assertTrue(os.path.exists(os.path.join(unittest_data_path, 'calibration.poni')))
        os.remove(os.path.join(unittest_data_path, 'calibration.poni'))

    def test_selecting_configuration_updates_parameter_display(self):
        self.mock_integrate_functions()
        calibration1 = {
            'dist': 0.2,
            'poni1': 0.08,
            'poni2': 0.081,
            'rot1': 0.0043,
            'rot2': 0.002,
            'rot3': 0.001,
            'pixel1': 7.9e-5,
            'pixel2': 7.9e-5,
            'wavelength': 0.3344,
            'polarization_factor': 0.99
        }
        calibration2 = {
            'dist': 0.3,
            'poni1': 0.04,
            'poni2': 0.021,
            'rot1': 0.0053,
            'rot2': 0.002,
            'rot3': 0.0013,
            'pixel1': 7.4e-5,
            'pixel2': 7.6e-5,
            'wavelength': 0.31,
            'polarization_factor': 0.98
        }

        self.model.calibration_model.set_pyFAI(calibration1)
        self.model.add_configuration()
        self.model.calibration_model.set_pyFAI(calibration2)

        self.model.select_configuration(0)

        model_calibration = self.model.configurations[0].calibration_model.pattern_geometry.getPyFAI()
        del model_calibration['detector']
        if 'splineFile' in model_calibration.keys():
            del model_calibration['splineFile']
        if 'max_shape' in model_calibration.keys():
            del model_calibration['max_shape']
        current_displayed_calibration = self.calibration_widget.get_pyFAI_parameter()
        del current_displayed_calibration['polarization_factor']
        self.assertEqual(model_calibration, current_displayed_calibration)

        self.model.select_configuration(1)
        model_calibration = self.model.configurations[1].calibration_model.pattern_geometry.getPyFAI()
        del model_calibration['detector']
        if 'splineFile' in model_calibration.keys():
            del model_calibration['splineFile']
        if 'max_shape' in model_calibration.keys():
            del model_calibration['max_shape']
        current_displayed_calibration = self.calibration_widget.get_pyFAI_parameter()
        del current_displayed_calibration['polarization_factor']
        self.assertEqual(model_calibration, current_displayed_calibration)

        self.calibration_widget.get_pyFAI_parameter()

    @unittest.skip('Does not work for unknown reasons')
    def test_calibrant_with_small_set_of_d_spacings(self):
        self.mock_integrate_functions()
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'LaB6_40keV_MarCCD.tif'))
        QTest.mouseClick(self.calibration_widget.load_img_btn, QtCore.Qt.LeftButton)
        self.calibration_controller.search_peaks(1179.6, 1129.4)
        self.calibration_controller.search_peaks(1268.5, 1119.8)
        calibrant_index = self.calibration_widget.calibrant_cb.findText('CuO')
        self.calibration_controller.widget.calibrant_cb.setCurrentIndex(calibrant_index)
        QtWidgets.QMessageBox.critical = MagicMock()
        click_button(self.calibration_widget.calibrate_btn)
        QtWidgets.QMessageBox.critical.assert_called_once()

    def test_loading_calibration_without_an_image_before(self):
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(
            return_value=os.path.join(unittest_data_path, 'LaB6_40keV_MarCCD.poni'))
        QTest.mouseClick(self.calibration_widget.load_calibration_btn, QtCore.Qt.LeftButton)
