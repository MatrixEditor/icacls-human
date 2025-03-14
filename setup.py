# Copyright (C) MatrixEditor 2025
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os

from setuptools import setup
from subprocess import Popen, call, STDOUT, PIPE


VER_MAJOR = 0
VER_MINOR = 1
VER_PREREL = "dev"
try:
    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, "w")) == 0:
        p = Popen(
            "git rev-parse --short HEAD",
            shell=True,
            stdin=PIPE,
            stderr=PIPE,
            stdout=PIPE,
        )
        (outstr, __) = p.communicate()
        VER_CHASH = outstr.strip().decode("utf-8")

        VER_LOCAL = "+{}".format(VER_CHASH)
    else:
        VER_LOCAL = ""
except Exception:
    VER_LOCAL = ""


def local_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)


setup(
    name="icacls2h",
    version=".".join([str(VER_MAJOR), str(VER_MINOR), VER_PREREL, VER_LOCAL]),
    author="MatrixEditor",
    author_email="",
    description="Converts output from icacls to human-readable format",
    long_description=open(local_path("README.md")).read(),
    long_description_content_type="text/markdown",
    license="GNU GPLv3",
    packages=[],  # no packages
    scripts=[local_path("icacls2h.py")],
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
    ],
)
