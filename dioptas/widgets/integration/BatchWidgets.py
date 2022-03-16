import os

from qtpy import QtWidgets, QtCore, QtGui
from pyqtgraph import GraphicsLayoutWidget, ColorButton

from ..plot_widgets.ImgWidget import IntegrationBatchWidget
from ..plot_widgets.SurfaceWidget import SurfaceWidget
from .CustomWidgets import StepBatchWidget, FileViewWidget
from .CustomWidgets import MouseCurrentAndClickedWidget
from ..CustomWidgets import FlatButton, CheckableFlatButton, HorizontalSpacerItem, VerticalSpacerItem

from . import CLICKED_COLOR
from ... import icons_path


class BatchWidget(QtWidgets.QWidget):
    """
    Class describe a widget for batch integration
    """

    def __init__(self, parent=None):
        super(BatchWidget, self).__init__(parent)

        self.frame = QtWidgets.QFrame()
        self.frame.setObjectName('batch_frame')

        self._frame_layout = QtWidgets.QVBoxLayout()
        self._frame_layout.setContentsMargins(0, 0, 0, 0)
        self._frame_layout.setSpacing(0)

        # central layout
        self._central_layout = QtWidgets.QHBoxLayout()
        self._central_layout.setSpacing(0)
        self._frame_layout.setContentsMargins(0, 0, 0, 0)

        # Left control panel
        self.left_control_widget = QtWidgets.QWidget()
        self.left_control_widget.setObjectName('pattern_left_control_widget')
        self.left_control_widget.setMaximumWidth(30)
        self.left_control_widget.setMinimumWidth(30)
        self._left_control_layout = QtWidgets.QVBoxLayout()
        self._left_control_layout.setContentsMargins(4, 0, 4, 6)
        self._left_control_layout.setSpacing(4)

        self.scale_x_btn = CheckableFlatButton('x')
        self.scale_x_btn.setToolTip("Scale plot in X direction")
        self.scale_y_btn = CheckableFlatButton('y')
        self.scale_y_btn.setToolTip("Scale plot in Y direction")
        self.scale_z_btn = CheckableFlatButton('z')
        self.scale_z_btn.setToolTip("Scale plot in Z direction")
        self.scale_s_btn = CheckableFlatButton('s')
        self.scale_s_btn.setToolTip("Scale plot")
        self.scale_s_btn.setChecked(True)
        self.trim_h_btn = CheckableFlatButton('h')
        self.trim_h_btn.setToolTip("Cut higher values")
        self.trim_l_btn = CheckableFlatButton('l')
        self.trim_l_btn.setToolTip("Cut lower values")
        self.move_g_btn = CheckableFlatButton('g')
        self.move_g_btn.setToolTip("Move grid along y axis")
        self.move_m_btn = CheckableFlatButton('m')
        self.move_m_btn.setToolTip("Move marker along x axis")
        self.scroll_btn_group = QtWidgets.QButtonGroup()
        self.scroll_btn_group.addButton(self.scale_x_btn)
        self.scroll_btn_group.addButton(self.scale_y_btn)
        self.scroll_btn_group.addButton(self.scale_z_btn)
        self.scroll_btn_group.addButton(self.scale_s_btn)
        self.scroll_btn_group.addButton(self.trim_h_btn)
        self.scroll_btn_group.addButton(self.trim_l_btn)
        self.scroll_btn_group.addButton(self.move_g_btn)
        self.scroll_btn_group.addButton(self.move_m_btn)
        self.m_color_btn = ColorButton()
        self.m_color_btn.setToolTip("Set marker color")
        self.m_color_btn.setColor(0)
        self.m_color_btn.setMinimumHeight(80)

        self._left_control_layout.addWidget(self.m_color_btn)
        self._left_control_layout.addSpacerItem(VerticalSpacerItem())
        self._left_control_layout.addWidget(self.scale_x_btn)
        self._left_control_layout.addWidget(self.scale_y_btn)
        self._left_control_layout.addWidget(self.scale_z_btn)
        self._left_control_layout.addWidget(self.scale_s_btn)
        self._left_control_layout.addSpacerItem(VerticalSpacerItem())
        self._left_control_layout.addWidget(self.trim_h_btn)
        self._left_control_layout.addWidget(self.trim_l_btn)
        self._left_control_layout.addSpacerItem(VerticalSpacerItem())
        self._left_control_layout.addWidget(self.move_g_btn)
        self._left_control_layout.addWidget(self.move_m_btn)

        self.left_control_widget.setLayout(self._left_control_layout)
        self.left_control_widget.hide()
        self._central_layout.addWidget(self.left_control_widget)

        # Middle view area
        self.file_view_widget = FileViewWidget()
        self._central_layout.addWidget(self.file_view_widget)
        self.file_view_widget.hide()

        self.img_pg_layout = GraphicsLayoutWidget()
        self.img_view = IntegrationBatchWidget(self.img_pg_layout, orientation='horizontal')
        self._central_layout.addWidget(self.img_pg_layout)

        self.surf_view = SurfaceWidget()
        self.surf_pg_layout = self.surf_view.pg_layout
        self._central_layout.addWidget(self.surf_view)
        self.surf_view.hide()

        # Right control
        self.right_control_widget = QtWidgets.QWidget()
        self.right_control_widget.setObjectName('pattern_right_control_widget')
        self.right_control_widget.setMaximumWidth(30)
        self.right_control_widget.setMinimumWidth(30)
        self._right_control_layout = QtWidgets.QVBoxLayout()
        self._right_control_layout.setContentsMargins(4, 0, 4, 6)
        self._right_control_layout.setSpacing(4)

        self.view3d_f_btn = FlatButton("F")
        self.view3d_f_btn.setToolTip("Set front view")
        self.view3d_s_btn = FlatButton("R")
        self.view3d_s_btn.setToolTip("Set right view")
        self.view3d_t_btn = FlatButton("T")
        self.view3d_t_btn.setToolTip("Set top view")
        self.view3d_i_btn = FlatButton("I")
        self.view3d_i_btn.setToolTip("Set isometric view")
        self.tth_btn = CheckableFlatButton(u"2θ")
        self.tth_btn.setChecked(True)
        self.q_btn = CheckableFlatButton('Q')
        self.d_btn = CheckableFlatButton('d')
        self.unit_btn_group = QtWidgets.QButtonGroup()
        self.unit_btn_group.addButton(self.tth_btn)
        self.unit_btn_group.addButton(self.q_btn)
        self.unit_btn_group.addButton(self.d_btn)
        self.background_btn = CheckableFlatButton('bg')
        self.bkg_cut_btn = CheckableFlatButton('T')
        self.bkg_cut_btn.setToolTip("Trim data to show only region where background is calculated")
        self.view3d_f_btn.hide()
        self.view3d_s_btn.hide()
        self.view3d_t_btn.hide()
        self.view3d_i_btn.hide()

        self.scale_log_btn = CheckableFlatButton("log")
        self.scale_log_btn.setToolTip("Change scale to log")
        self.scale_sqrt_btn = CheckableFlatButton("√")
        self.scale_sqrt_btn.setToolTip("Change scale to sqrt")
        self.scale_lin_btn = CheckableFlatButton("lin")
        self.scale_lin_btn.setChecked(True)
        self.scale_lin_btn.setToolTip("Change scale to linear")
        self.unit_scale_group = QtWidgets.QButtonGroup()
        self.unit_scale_group.addButton(self.scale_log_btn)
        self.unit_scale_group.addButton(self.scale_sqrt_btn)
        self.unit_scale_group.addButton(self.scale_lin_btn)

        self._right_control_layout.addSpacerItem(VerticalSpacerItem())
        self._right_control_layout.addWidget(self.view3d_f_btn)
        self._right_control_layout.addWidget(self.view3d_s_btn)
        self._right_control_layout.addWidget(self.view3d_t_btn)
        self._right_control_layout.addWidget(self.view3d_i_btn)
        self._right_control_layout.addWidget(self.tth_btn)
        self._right_control_layout.addWidget(self.q_btn)
        self._right_control_layout.addWidget(self.d_btn)
        self._right_control_layout.addSpacerItem(VerticalSpacerItem())
        self._right_control_layout.addWidget(self.scale_lin_btn)
        self._right_control_layout.addWidget(self.scale_sqrt_btn)
        self._right_control_layout.addWidget(self.scale_log_btn)
        self._right_control_layout.addSpacerItem(VerticalSpacerItem())
        self._right_control_layout.addWidget(self.background_btn)
        self._right_control_layout.addWidget(self.bkg_cut_btn)
        self.right_control_widget.setLayout(self._right_control_layout)

        self._central_layout.addWidget(self.right_control_widget)
        self._frame_layout.addLayout(self._central_layout)

        # Bottom control layout
        self.bottom_control_widget = QtWidgets.QWidget()
        self.bottom_control_widget.setObjectName('pattern_bottom_control_widget')

        self.load_btn = FlatButton()
        self.load_btn.setToolTip("Load raw/proc data")
        self.load_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'open.ico')))
        self.load_btn.setIconSize(QtCore.QSize(13, 13))
        self.load_btn.setMaximumWidth(25)

        self.integrate_btn = FlatButton("Integrate")
        self.load_proc_btn = FlatButton("Load proc data")

        self.save_btn = FlatButton()
        self.save_btn.setToolTip("Save data")
        self.save_btn.setIcon(QtGui.QIcon(os.path.join(icons_path, 'save.ico')))
        self.save_btn.setIconSize(QtCore.QSize(13, 13))
        self.save_btn.setMaximumWidth(25)

        self.view_2d_btn = CheckableFlatButton("2D")
        self.view_3d_btn = CheckableFlatButton("3D")
        self.view_f_btn = CheckableFlatButton("F")
        self.view_2d_btn.setChecked(True)
        self.unit_view_group = QtWidgets.QButtonGroup()
        self.unit_view_group.addButton(self.view_2d_btn)
        self.unit_view_group.addButton(self.view_3d_btn)
        self.unit_view_group.addButton(self.view_f_btn)

        self.waterfall_btn = CheckableFlatButton("Waterfall")
        self.waterfall_btn.setToolTip("Create waterfall plot")

        self.calc_bkg_btn = FlatButton("Calc bkg")
        self.calc_bkg_btn.setToolTip("Extract background")

        self.phases_btn = CheckableFlatButton('Show Phases')
        self.autoscale_btn = FlatButton("AutoScale")

        self.bottom_control_layout = QtWidgets.QHBoxLayout()
        self.bottom_control_layout.addWidget(self.load_btn)
        self.bottom_control_layout.addWidget(self.save_btn)

        self.bottom_control_layout.addWidget(self.integrate_btn)
        self.bottom_control_layout.addWidget(self.calc_bkg_btn)
        self.bottom_control_layout.addWidget(self.waterfall_btn)
        self.bottom_control_layout.addWidget(self.phases_btn)
        self.bottom_control_layout.addWidget(self.autoscale_btn)

        self.bottom_control_layout.addSpacerItem(HorizontalSpacerItem())
        self.bottom_control_layout.addWidget(self.view_f_btn)
        self.bottom_control_layout.addWidget(self.view_2d_btn)
        self.bottom_control_layout.addWidget(self.view_3d_btn)
        self.bottom_control_layout.addSpacerItem(HorizontalSpacerItem())

        self.bottom_control_widget.setLayout(self.bottom_control_layout)

        self._frame_layout.addWidget(self.bottom_control_widget)

        # Sliding and positioning
        self.step_series_widget = StepBatchWidget()
        self.step_raw_widget = StepBatchWidget()
        self.step_raw_widget.hide()
        self.mouse_pos_widget = MouseCurrentAndClickedWidget(CLICKED_COLOR)

        self._positioning_layout = QtWidgets.QHBoxLayout()
        self._positioning_layout.setSpacing(0)
        self._positioning_layout.setContentsMargins(4, 4, 4, 4)
        self._positioning_layout.addWidget(self.step_series_widget)
        self._positioning_layout.addWidget(self.step_raw_widget)
        self._positioning_layout.addSpacerItem(HorizontalSpacerItem())
        self._positioning_layout.addWidget(self.mouse_pos_widget)

        self._frame_layout.addLayout(self._positioning_layout)

        self.frame.setLayout(self._frame_layout)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.frame)

        self.setLayout(self._layout)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("Batch widget")

        self.right_control_widget.setStyleSheet(
            """
            #pattern_frame, #pattern_right_control_widget, QLabel {
                background: black;
                color: yellow;
            }
            #pattern_right_control_widget QPushButton{
                padding: 0px;
                padding-right: 1px;
                border-radius: 3px;
            }
            """)

        self.left_control_widget.setStyleSheet(
            """
                #pattern_frame, #pattern_left_control_widget, QLabel {
                    background: black;
                    color: yellow;
                }
                #pattern_left_control_widget QPushButton{
                    padding: 0px;
                    padding-left: 1px;
                    border-radius: 3px;
                }
            """)

        self.bottom_control_widget.setStyleSheet(
            """
                #pattern_bottom_control_widget QPushButton{
                    padding: 0px;
                    padding-right: 5px;
                    padding-left: 5px;
                    border-radius: 3px;
                }
                #pattern_frame, #pattern_bottom_control_widget, QLabel {
                    background: black;
                    color: yellow;
                }
            """)

    def raise_widget(self):
        self.show()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.raise_()
