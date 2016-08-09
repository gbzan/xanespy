# -*- coding: utf-8 -*-
#
# Copyright © 2016 Mark Wolf
#
# This file is part of Xanespy.
#
# Xanespy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Xanespy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Xanespy.  If not, see <http://www.gnu.org/licenses/>.

"""Functions and classes that prepare experiments at specific
synchrotron beamlines."""

from typing import List, Tuple, Iterable
from collections import namedtuple
import os

import numpy as np

from edges import KEdge
from utilities import position

ZoneplatePoint = namedtuple('ZoneplatePoint', ('x', 'y', 'z', 'energy'))
DetectorPoint = namedtuple('DetectorPoint', ('z', 'energy'))


class Zoneplate():
    """Type of focusing optic using in X-ray microscopy. It must be moved
    with changing energy to properly focus the beam. In order to
    properly predict zoneplate positions, it needs either two
    position-energy pairs or one position-energy pair and a
    step. Passing two position-energy pairs is preffered because this
    allows x, y and z to be set properly instead of just z.

    Arguments
    ---------
    - start : The first zoneplate position-energy pair.

    - step : Adjustment in z-position for every positive change of 1 eV
      of beam energy.

    - end : The second zoneplate position-energy pair.

    """
    def __init__(self,
                 start: ZoneplatePoint,
                 z_step: int=None,
                 end: ZoneplatePoint=None):
        # Check sanity of arguments
        if z_step is None and end is None:
            msg = "Either `step` or `end` is required."
            raise ValueError(msg)
        elif z_step is not None and end is not None:
            msg = "Passing both `step` or `end` is confusing."
            raise ValueError(msg)
        elif z_step is None:
            # Calculate the step from start and end points
            self.step = position(
                x=(end.x - start.x) / (end.energy - start.energy),
                y=(end.y - start.y) / (end.energy - start.energy),
                z=(end.z - start.z) / (end.energy - start.energy),
            )
        else:
            self.step = position(x=0, y=0, z=z_step)
        self.start = start

    def position(self, energy: float):
        """Predict the x, y and z position of the zonplate for the given energy."""
        pos = position(
            x=self.start.x + self.step.x * (energy - self.start.energy),
            y=self.start.y + self.step.y * (energy - self.start.energy),
            z=self.start.z + self.step.z * (energy - self.start.energy),
        )
        return pos

    def z_position(self, energy: float):
        """Predict the z-position of the zoneplate for the given energy."""
        raise NotImplementedError("Use position().z instead")


class Detector(Zoneplate):
    """A calibration object for the position of the detector."""
    pass


def write_scaninfo_header(f, abba_mode, repetitions, ref_repetitions):
    f.write('VERSION 1\n')
    f.write('ENERGY 1\n')
    f.write('TOMO 0\n')
    f.write('MOSAIC 0\n')
    f.write('MULTIEXPOSURE 4\n')
    f.write('NREPEATSCAN   1\n')
    f.write('WAITNSECS   0\n')
    f.write('NEXPOSURES   {}\n'.format(repetitions))
    f.write('AVERAGEONTHEFLY   0\n')
    f.write('REFNEXPOSURES  {}\n'.format(ref_repetitions))
    f.write('REF4EVERYEXPOSURES   {}\n'.format(repetitions))
    f.write('REFABBA {}\n'.format(1 if abba_mode else 0))
    f.write('REFAVERAGEONTHEFLY 0\n')
    f.write('MOSAICUP   1\n')
    f.write('MOSAICDOWN   1\n')
    f.write('MOSAICLEFT   1\n')
    f.write('MOSAICRIGHT   1\n')
    f.write('MOSAICOVERLAP 0.20\n')
    f.write('MOSAICCENTRALTILE   1\n')
    f.write('FILES\n')

def ssrl6_xanes_script(dest,
                       edge: KEdge,
                       zoneplate: Zoneplate,
                       positions: List[position],
                       reference_position: position,
                       iterations: Iterable,
                       iteration_rest: int=0,
                       frame_rest: int=0,
                       binning: int=2,
                       exposure: int=0.5,
                       repetitions: int=5,
                       ref_repetitions: int=10,
                       abba_mode: bool=True):
    """Prepare a script file for running multiple consecutive XANES
    framesets on the transmission x-ray micrscope at the Advanced
    Photon Source beamline 8-BM-B. Both `iteration_rest` and
    `frame_rest` can be used to give the material time to recover from
    X-ray damage.

    Arguments
    ---------
    - dest : file-like object that will hold the resulting script

    - edge : Description of the absorption edge.

    - binning : how many CCD pixels to combine into one image pixel
      (eg. 2 means 2x2 CCD pixels become 1 image pixel.

    - exposure : How many seconds to collect for per frame

    - positions : Locations to move the x, y (and z) axes to in
      order to capture the image.

    - reference_position : Single x, y, z location to capture a
      reference frame.

    - iteration_rest : Time (in seconds) to wait between
      iterations. Beam will wait at reference location before starting
      next XANES set.

    - frame_rest : Time (in seconds) to wait between frames. Beam will
      wait at reference location before starting next energy frame.

    - zoneplate : Calibration details for the Fresnel zone-plate.

    - detector : Like zoneplate, but for detector.

    - iterations : iterable that contains an identifier for each XANES dataset.

    - repetitions : How many images to collect for each
      location/energy. These frames will then be averaged during
      analysis.

    - ref_repetitions : Same as `repetitions` but for reference frames.

    - abba_mode : If True, script will alternate sample and reference
      locations first to save time. Eg: reference, sample,
      change-energy, sample, reference, change-energy, etc. Not
      compatible with `frame_rest` argument.

    """
    # Sanity checks for arguments
    if frame_rest and abba_mode:
        raise ValueError("Cannot use `frame_rest` and `abba_mode` together.")
    # Save a template for writing string and sample frames
    ref_template = 'ref_{name}_{energy:07.1f}_eV_{ctr:03d}of{total:03d}.xrm\n'
    sam_template = '{name}_fov{fov}_{energy:07.1f}_eV_{ctr:03d}of{total:03d}.xrm\n'
    pos_template = 'moveto x {x:.2f}\nmoveto y {y:.2f}\nmoveto z {z:.2f}\n'
    # Command to set the exposure and binning (gets used repeatedly)
    exposure_str = 'setexp {exp:.2f}\nsetbinning {binning}\n'
    exposure_str = exposure_str.format(exp=exposure,
                                       binning=binning)
    # Prepare a scan info file for TXM Wizard
    dirname, filename = os.path.split(dest.name)
    scaninfo = os.path.join(dirname, "ScanInfo_" + filename)
    scaninfo = open(scaninfo, mode='w')
    write_scaninfo_header(f=scaninfo, abba_mode=abba_mode,
                          repetitions=repetitions,
                          ref_repetitions=ref_repetitions)
    for fs_name in iterations:
        # Flag to keep track of ABBA mode status
        ref_first = True
        # Start writing header in file
        dest.write(';; 2D XANES ;;\n')
        # Step through each energy and write the commands
        for E in edge.all_energies():
            dest.write(';;;; set the MONO and the ZP\n')
            dest.write('sete {:.02f}\n'.format(E))
            # Determine correct zoneplate settings
            zp_pos = zoneplate.position(energy=E)
            dest.write('moveto zpx {:.2f}\n'.format(zp_pos.x))
            dest.write('moveto zpy {:.2f}\n'.format(zp_pos.y))
            dest.write('moveto zpz {:.2f}\n'.format(zp_pos.z))
            # Determine commands for reference frame (but delay writing)
            ref_s = ';;;; Move to reference position\n'
            ref_s += pos_template.format(x=reference_position.x,
                                         y=reference_position.y,
                                         z=reference_position.z)
            # Pause to let material recover
            if frame_rest and ref_first:
                ref_s += 'wait {:d}\n'.format(frame_rest)
            ref_s += ';;;; Collect reference frames\n'
            ref_s += exposure_str
            for rep in range(0, ref_repetitions):
                xrmfile = ref_template.format(name=fs_name,
                                              energy=E,
                                              ctr=rep,
                                              total=ref_repetitions)
                ref_s += "collect {}".format(xrmfile)
                scaninfo.write(xrmfile)
            # Pause to let material recover
            if frame_rest and not ref_first:
                ref_s += 'wait {:d}\n'.format(frame_rest)
            # Write commands for collecting reference frames (if appropriate)
            if ref_first:
                dest.write(ref_s)
            # Write commands for collecting sample frames
            if ref_first:
                pos_list = positions
            else:
                # Go backwards if even step in ABBA mode
                pos_list = positions[::-1]
            for idx, sam_pos in enumerate(pos_list):
                if ref_first:
                    pos_idx = idx
                else:
                    pos_idx = len(pos_list) - idx - 1
                dest.write(';;;; Move to sample position {}\n'.format(pos_idx))
                dest.write(pos_template.format(x=sam_pos.x, y=sam_pos.y, z=sam_pos.z))
                dest.write(';;;; Collect frames sample position {}\n'.format(pos_idx))
                dest.write(exposure_str)
                for rep in range(0, repetitions):
                    xrmfile = sam_template.format(name=fs_name,
                                                  energy=E,
                                                  fov=pos_idx,
                                                  ctr=rep,
                                                  total=repetitions)
                    dest.write("collect {}".format(xrmfile))
                    scaninfo.write(xrmfile)
            # Write commands for collecting reference frames (if in ABBA mode)
            if not ref_first:
                dest.write(ref_s)
            # Toggle ABBA mode state if abba_mode is set
            ref_first = not (ref_first and abba_mode)
        # Move to reference position to avoid beam damage
        dest.write(';;;; Park at reference position\n')
        dest.write(pos_template.format(x=reference_position.x,
                                       y=reference_position.y,
                                       z=reference_position.z))
    # Pause to let the material recover (unless this is the last dataset)
    if iteration_rest and fs_name != iterations[-1]:
        dest.write('wait {:d}\n'.format(iteration_rest))
    # Close ScanInfo file
    scaninfo.close()

def sector8_xanes_script(dest,
                         edge: KEdge,
                         zoneplate: Zoneplate,
                         detector: Detector,
                         sample_positions: List[position],
                         names: List[str],
                         iterations: Iterable=range(0, 1),
                         binning: int=1,
                         exposure: int=30,
                         abba_mode: bool=True):
    """Prepare an script file for running multiple consecutive XANES
    framesets on the transmission x-ray micrscope at the Advanced
    Photon Source beamline 8-BM-B.

    Arguments
    ---------
    - dest : file-like object that will hold the resulting script

    - edge : Description of the absorption edge.

    - binning : how many CCD pixels to combine into one image pixel
      (eg. 2 means 2x2 CCD pixels become 1 image pixel.

    - exposure : How many seconds to collect for per frame

    - sample_positions : Locations to move the x, y (and z) axes to in
      order to capture the image.

    - zoneplate : Calibration details for the Fresnel zone-plate.

    - detector : Like zoneplate, but for detector.

    - names : sample name to use in file names.

    - iterations : iterable to contains an identifier for each full
      set of xanes location with reference.

    - abba_mode : If True, script will locations forward and backwards
      to save time. Eg: reference, sample, change-energy, sample,
      reference, change-energy, etc. Not compatible with `frame_rest`
      argument.

    """
    dest.write("setbinning {}\n".format(binning))
    dest.write("setexp {}\n".format(exposure))
    energies = edge.all_energies()
    starting_energy = energies[0]
    for iteration in iterations:
        # Status flag for using abba_mode
        reverse_positions = False
        # Approach target energy from below
        for energy in np.arange(starting_energy - 100, starting_energy, 2):
            dest.write("moveto energy {:.2f}\n".format(energy))
        for energy in energies:
            # Set energy
            dest.write("moveto energy {:.2f}\n".format(energy))
            # Set zoneplate
            dest.write("moveto zpz {:.2f}\n".format(zoneplate.position(energy).z))
            # Set detector
            dest.write("moveto detz {:.2f}\n".format(detector.position(energy).z))
            # Prepare range of sample positions
            if reverse_positions and abba_mode:
                position_indexes = range(len(sample_positions)-1, -1, -1)
            else:
                position_indexes = range(0, len(sample_positions))
            reverse_positions = not reverse_positions
            # Cycle through sample positions and collect data
            for idx in position_indexes:
                position = sample_positions[idx]
                name = names[idx]
                # Move to x, y, z
                dest.write("moveto x {:.2f}\n".format(position.x))
                dest.write("moveto y {:.2f}\n".format(position.y))
                dest.write("moveto z {:.2f}\n".format(position.z))
                # Collect frame
                filename = "{name}_xanes{iter}_{energy}eV.xrm"
                energy_str = "{}_{}".format(*str(float(energy)).split('.'))
                filename = filename.format(name=name,
                                           iter=iteration,
                                           energy=energy_str)
                dest.write("collect {filename}\n".format(filename=filename))
