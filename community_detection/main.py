# main.py
#
# Copyright 2022 Martin Pobaschnig
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
#
# SPDX-License-Identifier: GPL-3.0-or-later

from cdhf.data import Data

import cd


def main() -> None:
    data = Data("../../input/mmdata.json")

    data.load_all()

    c = cd.CD()

    c.set_data(data)

    c.find()

    p = c.plot_graph()
    p.show()

    pc = c.plot_graph_with_communities()
    pc.show()


if __name__ == "__main__":
    main()
