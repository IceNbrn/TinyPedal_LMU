#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
API data adapter

To create new API adapter, duplicate rfactor2.py and fill in entries.
"""

from pyRfactor2SharedMemory import rF2MMap


class DataAdapter:
    """Read & sort data into groups

    Attributes:
        info: API object.
    """

    __slots__ = (
        "info",
    )

    def __init__(self, info: rF2MMap.RF2SM) -> None:
        """Initialize API setting

        Args:
            info: API object.
        """
        self.info = info
