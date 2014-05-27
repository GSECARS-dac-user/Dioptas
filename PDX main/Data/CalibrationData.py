__author__ = 'Clemens Prescher'

from pyFAI.peakPicker import Massif
from pyFAI.blob_detection import BlobDetection
from pyFAI.calibration import Calibration
from pyFAI.geometryRefinement import GeometryRefinement
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
from pyFAI.calibrant import Calibrant
from Data.HelperModule import get_base_name
import numpy as np
import pyqtgraph as pg

import matplotlib.pyplot as plt


class CalibrationData(object):
    def __init__(self, img_data=None):
        self.img_data = img_data
        self.points = []
        self.points_index = []
        self.geometry = AzimuthalIntegrator()
        self.calibrant = Calibrant()
        self.start_values = {'dist': 400e-3,
                             'wavelength': 0.4133e-10,
                             'pixel_width': 200e-6,
                             'pixel_height': 200e-6,
                             'polarization_factor': 0.95}
        self.fit_wavelength = False
        self.is_calibrated = False
        self.use_mask = False
        self.calibration_name = 'None'
        self.polarization_factor = 0.95
        self._calibrants_working_dir = 'ExampleData/Calibrants'

    def find_peaks_automatic(self, x, y, peak_ind):
        massif = Massif(self.img_data.img_data)
        cur_peak_points = massif.find_peaks([x, y])
        if len(cur_peak_points):
            self.points.append(np.array(cur_peak_points))
            self.points_index.append(peak_ind)
        return np.array(cur_peak_points)

    def find_peak(self, x, y, search_size, peak_ind):
        left_ind = np.round(x - search_size * 0.5)
        top_ind = np.round(y - search_size * 0.5)
        x_ind, y_ind = np.where(self.img_data.img_data[left_ind:(left_ind + search_size),
                                top_ind:(top_ind + search_size)] == \
                                self.img_data.img_data[left_ind:(left_ind + search_size),
                                top_ind:(top_ind + search_size)].max())
        x_ind = x_ind[0] + left_ind
        y_ind = y_ind[0] + top_ind
        self.points.append(np.array([x_ind, y_ind]))
        self.points_index.append(peak_ind)
        return np.array([np.array((x_ind, y_ind))])

    def clear_peaks(self):
        self.points = []
        self.points_index = []

    def search_peaks_on_ring(self, peak_index, delta_tth=0.1, algorithm='Massif', upper_limit=55000):
        if self.is_calibrated == False:
            return

        #transform delta from degree into radians
        delta_tth = delta_tth / 180.0 * np.pi

        # get appropiate two theta value for the ring number
        tth_calibrant_list = self.calibrant.get_2th()
        tth_calibrant = np.float(tth_calibrant_list[peak_index])
        print tth_calibrant

        # get the calculated two theta values for the whole image
        if self.geometry._ttha is None:
            tth_array = self.geometry.twoThetaArray(self.img_data.img_data.shape)
        else:
            tth_array = self.geometry._ttha

        # create mask based on two_theta position
        mask = abs(tth_array - tth_calibrant) <= delta_tth


        # init the peak search algorithm
        if algorithm == 'Massif':
            peak_search_algorithm = Massif(self.img_data.img_data)
        elif algorithm == 'Blob':
            peak_search_algorithm = BlobDetection(self.img_data.img_data * mask)
            peak_search_algorithm.process()
        else:
            return

        # calculate the mean and standard deviation of this area
        sub_data = np.array(self.img_data.img_data.ravel()[np.where(mask.ravel())], dtype=np.float64)
        sub_data[np.where(sub_data > upper_limit)] = np.NaN
        mean = np.nanmean(sub_data)
        std = np.nanstd(sub_data)

        # set the threshold into the mask (don't detect very low intensity peaks)
        threshold = mean + std
        mask2 = np.logical_and(self.img_data.img_data > threshold, mask)
        mask2[np.where(self.img_data.img_data > upper_limit)] = False
        size2 = mask2.sum(dtype=int)

        keep = int(np.ceil(np.sqrt(size2)))
        try:
            res = peak_search_algorithm.peaks_from_area(mask2, Imin=mean - std, keep=keep)
        except IndexError:
            res = []

        # Store the result
        if len(res):
            self.points.append(np.array(res))
            self.points_index.append(peak_index)

    def set_calibrant(self, filename):
        self.calibrant = Calibrant()
        self.calibrant.load_file(filename)
        self.geometry.calibrant = self.calibrant

    def set_start_values(self, start_values):
        self.start_values = start_values
        self.polarization_factor = start_values['polarization_factor']

    def calibrate(self):
        self.geometry = GeometryRefinement(self.create_point_array(self.points, self.points_index),
                                           dist=self.start_values['dist'],
                                           wavelength=self.start_values['wavelength'],
                                           pixel1=self.start_values['pixel_width'],
                                           pixel2=self.start_values['pixel_height'],
                                           calibrant=self.calibrant)
        self.refine()
        self.integrate()
        self.is_calibrated = True
        self.calibration_name = 'current'

    def recalibrate(self, method='massif'):
        self.automatic_peak_search(method)
        self.refine()
        self.integrate()

    def refine(self):
        self.geometry.data = self.create_point_array(self.points, self.points_index)
        self.geometry.refine2()
        if self.fit_wavelength:
            self.geometry.refine2_wavelength(fix=[])

    def integrate(self):
        self.integrate_1d()
        self.integrate_2d()

    def integrate_1d(self, num_points=1400, mask=None, polarization_factor=None, filename=None, unit='2th_deg'):
        if polarization_factor == None:
            polarization_factor = self.polarization_factor
        self.tth, self.int = self.geometry.integrate1d(self.img_data.img_data, num_points, method='lut', unit=unit,
                                                       mask=mask, polarization_factor=polarization_factor,
                                                       filename=filename)
        return self.tth, self.int

    def integrate_2d(self, mask=None, polarization_factor=None, unit='2th_deg'):
        if polarization_factor == None:
            polarization_factor = self.polarization_factor
        res = self.geometry.integrate2d(self.img_data.img_data, 2024, 2024, method='lut', mask=None, unit=unit,
                                        polarization_factor=polarization_factor)
        self.cake_img = res[0]
        self.cake_tth = res[1]
        self.cake_azi = res[2]
        return self.cake_img

    def create_point_array(self, points, points_ind):
        res = []
        for i, point_list in enumerate(points):
            if point_list.shape == (2,):
                res.append([point_list[0], point_list[1], points_ind[i]])
            else:
                for point in point_list:
                    res.append([point[0], point[1], points_ind[i]])
        return np.array(res)

    def get_point_array(self):
        return self.create_point_array(self.points, self.points_index)

    def get_calibration_parameter(self):
        pyFAI_parameter = self.geometry.getPyFAI()
        pyFAI_parameter['polarization_factor'] = self.polarization_factor
        try:
            fit2d_parameter = self.geometry.getFit2D()
            fit2d_parameter['polarization_factor'] = self.polarization_factor
        except TypeError:
            fit2d_parameter = None
        try:
            pyFAI_parameter['wavelength'] = self.geometry.wavelength
            fit2d_parameter['wavelength'] = self.geometry.wavelength
        except RuntimeWarning:
            pyFAI_parameter['wavelength'] = 0

        return pyFAI_parameter, fit2d_parameter

    def load(self, filename):
        self.geometry = GeometryRefinement(np.zeros((2, 3)),
                                           dist=self.start_values['dist'],
                                           wavelength=self.start_values['wavelength'],
                                           pixel1=self.start_values['pixel_width'],
                                           pixel2=self.start_values['pixel_height'],
                                           calibrant=self.calibrant)
        self.geometry.load(filename)
        self.calibration_name = get_base_name(filename)
        self.is_calibrated = True

    def save(self, filename):
        self.geometry.save(filename)
        self.calibration_name = get_base_name(filename)