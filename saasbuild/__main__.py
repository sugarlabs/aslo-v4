#!/usr/bin/env python
"""
Sugar Activities App Store (SAAS)
https://github.com/sugarlabs-aslo/sugarappstore

Copyright 2020 SugarLabs
Copyright 2020 Srevin Saju <srevinsaju@sugarlabs.org>
Copyright 2020 Manish <sugar@radii.dev>

This file is part of "Sugar Activities App Store" aka "SAAS".

SAAS is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SAAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with SAAS.  If not, see <https://www.gnu.org/licenses/>.
"""
from .generator import SaaSBuild


def main():
    SaaSBuild()


if __name__ == "__main__":
    main()
