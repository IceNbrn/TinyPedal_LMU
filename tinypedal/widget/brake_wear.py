#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Brake Wear Widget
"""

from .. import calculation as calc
from ..const_common import TEXT_NA
from ..module_info import minfo
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_width = font_m.width * 4 + bar_padx
        self.threshold_remaining = min(max(self.wcfg["warning_threshold_remaining"], 0), 100) * 0.01

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )
        bar_style_desc = self.set_qss(
            fg_color=self.wcfg["font_color_caption"],
            bg_color=self.wcfg["bkg_color_caption"],
            font_size=int(self.wcfg['font_size'] * 0.8)
        )

        # Remaining brake thickness
        if self.wcfg["show_remaining"]:
            layout_remain = self.set_grid_layout()
            self.bar_style_remain = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_remaining"],
                    bg_color=self.wcfg["bkg_color_remaining"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_remaining"])
            )
            self.bars_remain = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_remain[0],
                width=bar_width,
                count=4,
                last=0,
            )
            self.set_grid_layout_quad(
                layout=layout_remain,
                targets=self.bars_remain,
            )
            self.set_primary_orient(
                target=layout_remain,
                column=self.wcfg["column_index_remaining"],
            )

            if self.wcfg["show_caption"]:
                cap_remain = self.set_qlabel(
                    text="brak wear",
                    style=bar_style_desc,
                )
                layout_remain.addWidget(cap_remain, 0, 0, 1, 0)

        # Wear difference
        if self.wcfg["show_wear_difference"]:
            layout_diff = self.set_grid_layout()
            self.bar_style_diff = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_wear_difference"],
                    bg_color=self.wcfg["bkg_color_wear_difference"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_wear_difference"])
            )
            self.bars_diff = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_diff[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_diff,
                targets=self.bars_diff,
            )
            self.set_primary_orient(
                target=layout_diff,
                column=self.wcfg["column_index_wear_difference"],
            )

            if self.wcfg["show_caption"]:
                cap_diff = self.set_qlabel(
                    text="wear diff",
                    style=bar_style_desc,
                )
                layout_diff.addWidget(cap_diff, 0, 0, 1, 0)

        # Estimated lifespan in laps
        if self.wcfg["show_lifespan_laps"]:
            layout_laps = self.set_grid_layout()
            self.bar_style_laps = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_lifespan_laps"],
                    bg_color=self.wcfg["bkg_color_lifespan_laps"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_lifespan_laps"])
            )
            self.bars_laps = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_laps[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_laps,
                targets=self.bars_laps,
            )
            self.set_primary_orient(
                target=layout_laps,
                column=self.wcfg["column_index_lifespan_laps"],
            )

            if self.wcfg["show_caption"]:
                cap_laps = self.set_qlabel(
                    text="est. laps",
                    style=bar_style_desc,
                )
                layout_laps.addWidget(cap_laps, 0, 0, 1, 0)

        # Estimated lifespan in minutes
        if self.wcfg["show_lifespan_minutes"]:
            layout_mins = self.set_grid_layout()
            self.bar_style_mins = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_lifespan_minutes"],
                    bg_color=self.wcfg["bkg_color_lifespan_minutes"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_lifespan_minutes"])
            )
            self.bars_mins = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_mins[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_mins,
                targets=self.bars_mins,
            )
            self.set_primary_orient(
                target=layout_mins,
                column=self.wcfg["column_index_lifespan_minutes"],
            )

            if self.wcfg["show_caption"]:
                cap_mins = self.set_qlabel(
                    text="est. mins",
                    style=bar_style_desc,
                )
                layout_mins.addWidget(cap_mins, 0, 0, 1, 0)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        laptime_pace = minfo.delta.lapTimePace
        for idx in range(4):
            brake_curr = minfo.wheels.currentBrakeThickness[idx]
            max_thickness = minfo.wheels.maxBrakeThickness[idx]
            est_wear = minfo.wheels.estimatedBrakeWear[idx]

            if self.wcfg["show_thickness"]:
                brake_curr *= max_thickness / 100
                est_wear *= max_thickness / 100

            # Remaining brake thickness
            if self.wcfg["show_remaining"]:
                if self.wcfg["show_thickness"]:
                    threshold_remaining = self.threshold_remaining * max_thickness
                else:
                    threshold_remaining = self.threshold_remaining * 100
                self.update_remain(self.bars_remain[idx], brake_curr, threshold_remaining)

            # Wear differences
            if self.wcfg["show_wear_difference"]:
                self.update_diff(self.bars_diff[idx], est_wear)

            # Estimated lifespan in laps
            if self.wcfg["show_lifespan_laps"]:
                wear_laps = calc.wear_lifespan_in_laps(brake_curr, est_wear)
                self.update_laps(self.bars_laps[idx], wear_laps)

            # Estimated lifespan in minutes
            if self.wcfg["show_lifespan_minutes"]:
                wear_mins = calc.wear_lifespan_in_mins(brake_curr, est_wear, laptime_pace)
                self.update_mins(self.bars_mins[idx], wear_mins)

    # GUI update methods
    def update_remain(self, target, data, threshold_remaining):
        """Remaining brake thickness"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_remain[data <= threshold_remaining]
            )

    def update_diff(self, target, data):
        """Wear differences"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_diff[data > self.wcfg["warning_threshold_wear"]]
            )

    def update_laps(self, target, data):
        """Estimated lifespan in laps"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_laps[data <= self.wcfg["warning_threshold_laps"]]
            )

    def update_mins(self, target, data):
        """Estimated lifespan in minutes"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_mins[data <= self.wcfg["warning_threshold_minutes"]]
            )

    # Additional methods
    @staticmethod
    def format_num(value):
        """Format number"""
        return f"{value:.2f}"[:4].strip(".")
