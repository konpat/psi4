#
# @BEGIN LICENSE
#
# Psi4: an open-source quantum chemistry software package
#
# Copyright (c) 2007-2017 The Psi4 Developers.
#
# The copyrights for code used from other parties are included in
# the corresponding files.
#
# This file is part of Psi4.
#
# Psi4 is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3.
#
# Psi4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Psi4; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# @END LICENSE
#

from __future__ import absolute_import
from __future__ import print_function
from .vecutil import *
from .physconst import *
from .cov_radii import *

BOND_FACTOR = 1.2  # fudge factor for bond length threshold

_expected_bonds = {
    'H': 1,
    'C': 4,
    'N': 3,
    'O': 2,
    'F': 1,
    'P': 3,
    'S': 2,
    }


def xyz2mol(self):
    """Returns a string of Molecule formatted for mol2.

    Written by Trent M. Parker 9 Jun 2014

    """
    factor = 1.0 if self.PYunits == 'Angstrom' else psi_bohr2angstroms

    bonds = self.bond_profile()

    N = 0
    for i in range(self.natom()):
        if self.Z(i):
            N += 1

    # header
    text = '%s\n' % (self.tagline)
    text += '  Generated by xyz2mol\n\n'
    text += '%3i%3i  0  0  0  0  0  0  0  0999 V2000\n' % (N, len(bonds))

    # coordinates
    for i in range(self.natom()):
        [x, y, z] = self.atoms[i].compute()
        if self.Z(i):
            text += ' %9.4f %9.4f %9.4f %-2s  0  0  0  0  0\n' % \
                (x * factor, y * factor, z * factor, self.symbol(i))

    # bonds
    for p in range(len(bonds)):
        text += '%3i%3i%3i' % (bonds[p][0] + 1, bonds[p][1] + 1, bonds[p][2])
        text += '  0  0  0\n'

    text += 'M  END\n'
    return text


def missing_bonds(bonds, bond_tree, at_types):
    """Determine number of bonds missing for each atom"""
    n_missing = []
    for i in range(len(at_types)):
        n_bonds_i = 0
        for p in range(len(bonds)):
            at1 = bonds[p][0]
            at2 = bonds[p][1]
            if (at1 == i or at2 == i):
                bond_order = bonds[p][2]
                n_bonds_i += bond_order
        n_expect_i = _expected_bonds[at_types[i]]
        n_missing.append(n_expect_i - n_bonds_i)

    return n_missing


def missing_neighbors(bond_tree, n_missing):
    """Determine number of neighboring atoms missing bonds for each atom"""
    missing_neighbors = []
    for i in range(len(bond_tree)):
        N_neighbors = len(bond_tree[i])
        missing = 0
        for a in range(N_neighbors):
            j = bond_tree[i][a]
            if n_missing[j] > 0:
                missing += 1
        missing_neighbors.append(missing)
    return missing_neighbors


def bond_profile(self):
    """Obtain bonding topology of molecule"""

    # determine bond topology from covalent radii
    bonds = []
    for i in range(self.natom()):
        for j in range(i + 1, self.natom()):
            dist = norm(sub(self.xyz(j), self.xyz(i))) * psi_bohr2angstroms
            # TOOD check bohr/ang progress
            bonded_dist = BOND_FACTOR * (psi_cov_radii[self.symbol(i)] + psi_cov_radii[self.symbol(j)])
            if bonded_dist > dist:
                bonds.append([i, j, 1])

    # determine bond order from number of bonds
    N_atoms = self.natom()
    N_bonds = len(bonds)
    at_types = [self.symbol(i) for i in range(self.natom())]
    bond_tree = [[] for i in range(N_atoms)]
    for i in range(N_bonds):
        at1 = bonds[i][0]
        at2 = bonds[i][1]
        bond_tree[at1].append(at2)
        bond_tree[at2].append(at1)

    # determine bond order for all bonds from bond tree and element types
    n_missing = missing_bonds(bonds, bond_tree, at_types)
    n_neighbors_missing = missing_neighbors(bond_tree, n_missing)

    # add double / triple bonds if only one neighbor missing bonds
    N_left = math.floor(sum(n_missing) / 2)
    N_left_previous = N_left + 1
    N_iter = 0
    while N_left > 0:
        N_iter += 1

        if N_left == N_left_previous:
            neighbor_min += 1
        else:
            neighbor_min = 1

        N_left_previous = N_left

        # add a multiple bond to a deficient atom with the fewest number of deficient neighbors
        BREAK_LOOP = False
        for i in range(N_atoms):
            if n_missing[i] > 0 and n_neighbors_missing[i] == neighbor_min:
                N_neighbors = len(bond_tree[i])
                for a in range(N_neighbors):
                    j = bond_tree[i][a]
                    if n_missing[j] > 0:
                        for p in range(N_bonds):
                            at1 = bonds[p][0]
                            at2 = bonds[p][1]
                            if (at1 == i and at2 == j) or (at1 == j and at2 == i):
                                bonds[p][2] += 1
                                n_missing[i] += -1
                                n_missing[j] += -1
                                n_neighbors_missing[i] += -1
                                n_neighbors_missing[j] += -1
                                N_left = math.floor(sum(n_missing) / 2)
                                BREAK_LOOP = True
                    if BREAK_LOOP:
                        break
            if BREAK_LOOP:
                break

        # recalculate incomplete bond topology
        n_missing = missing_bonds(bonds, bond_tree, at_types)
        n_neighbors_missing = missing_neighbors(bond_tree, n_missing)

        # break cycle if takes more than given number of iterations
        max_iter = 100
        if N_iter > max_iter:
            print("""Error: multiple bond determination not complete""")
            print("""  %i bonds unaccounted for""" % (N_left))
            break

    # bond order is number of bonds between each bonded atom pair
    bond_order = []
    for p in range(N_bonds):
        bond_order.append(bonds[p][2])
    for p in range(len(bond_order)):
        bonds[p][2] = bond_order[p]

    return bonds
