/*
 * @BEGIN LICENSE
 *
 * Psi4: an open-source quantum chemistry software package
 *
 * Copyright (c) 2007-2023 The Psi4 Developers.
 *
 * The copyrights for code used from other parties are included in
 * the corresponding files.
 *
 * This file is part of Psi4.
 *
 * Psi4 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * Psi4 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along
 * with Psi4; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * @END LICENSE
 */
#pragma once

#include "psi4/libmints/onebody.h"
#include "psi4/libmints/mcmurchiedavidson.h"

namespace psi {

class BasisSet;
class OneBodyAOInt;
class SphericalTransform;

/*! \ingroup MINTS
 *  \class MultipolePotentialInt
 *  \brief Computes multipole potential integrals, needed for EFP/PE calculations.
 *
 *  Use an IntegralFactory to create this object.
 *  The compute method takes a vector of SharedMatrix objects, which will be populated
 *  in CCA lexicographic (alphabetical) order of Cartesian components.
 */
class MultipolePotentialInt : public OneBodyAOInt, public mdintegrals::MDHelper {
    // maximum multipole potential order to compute (order of the 1/R derivative)
    int order_;

    //! CCA-ordered Cartesian components for the multipoles
    std::vector<std::vector<std::array<int, 3>>> comps_der_;

    //! Boys function evaluator from Libint2
    std::shared_ptr<const libint2::FmEval_Chebyshev7<double>> fm_eval_;

    //! R matrix (9.5.31)
    std::vector<double> R;

    //! Computes the multipole potential between two Gaussian shells.
    void compute_pair(const libint2::Shell&, const libint2::Shell&) override;

   public:
    //! Constructor. Do not call directly use an IntegralFactory.
    MultipolePotentialInt(std::vector<SphericalTransform>&, std::shared_ptr<BasisSet>, std::shared_ptr<BasisSet>,
                          int order, int deriv = 0);
    //! Virtual destructor
    ~MultipolePotentialInt() override;
};

class MultipolePotentialInt_reg : public OneBodyAOInt, public mdintegrals::MDHelper {
    // maximum multipole potential order to compute (order of the 1/R derivative)
    double eta_;
    int order_;

    //! CCA-ordered Cartesian components for the multipoles
    std::vector<std::vector<std::array<int, 3>>> comps_der_;

    //! Boys function evaluator from Libint2
    std::shared_ptr<const libint2::FmEval_Chebyshev7<double>> fm_eval_;

    //! R matrix (9.5.31)
    std::vector<double> R;

//    void set_charge_field(std::make_shared<Matrix>);

    //! Computes the multipole potential between two Gaussian shells.
    void compute_pair_reg(double, const libint2::Shell&, const libint2::Shell&) override;

   protected:
    /// Matrix of coordinates/charges of partial charges
    std::vector<std::pair<double, std::array<double, 3>>> Zxyz_;
 
   public:
    //! Constructor. Do not call directly use an IntegralFactory.
    MultipolePotentialInt_reg(double eta, std::vector<SphericalTransform>&, std::shared_ptr<BasisSet>, std::shared_ptr<BasisSet>,
                          int order, int deriv = 0);
    //! Virtual destructor
    ~MultipolePotentialInt_reg() override;

    void setEta(double eta);

   // Set the field of charges
//    void set_charge_field(SharedMatrix C_) { C = C_; };
    void set_charge_field(std::vector<std::pair<double, std::array<double, 3>>>& Zxyz);
   // Get the field of charges
//    SharedMatrix charge_field() const { return C; }
   //
//    void compute_pair_reg(double eta, const libint2::Shell&, const libint2::Shell&) override;

};

class MultipolePotentialInt_erf : public OneBodyAOInt, public mdintegrals::MDHelper {
    // maximum multipole potential order to compute (order of the 1/R derivative)
    double omega_;
    int order_;

    //! CCA-ordered Cartesian components for the multipoles
    std::vector<std::vector<std::array<int, 3>>> comps_der_;

    //! Boys function evaluator from Libint2
    std::shared_ptr<const libint2::FmEval_Chebyshev7<double>> fm_eval_;

    //! R matrix (9.5.31)
    std::vector<double> R;

    //! Computes the multipole potential between two Gaussian shells.
    void compute_pair_erf(double, const libint2::Shell&, const libint2::Shell&) override;

   protected:
    /// Matrix of coordinates/charges of partial charges
    SharedMatrix C;
 
   public:
    //! Constructor. Do not call directly use an IntegralFactory.
    MultipolePotentialInt_erf(double omega, std::vector<SphericalTransform>&, std::shared_ptr<BasisSet>, std::shared_ptr<BasisSet>,
                          int order, int deriv = 0);
    //! Virtual destructor
    ~MultipolePotentialInt_erf() override;

    void setOmega(double omega);

   // Set the field of charges
    void set_charge_field(SharedMatrix C_) { C = C_; }
  
   // Get the field of charges
    SharedMatrix charge_field() const { return C; }
   //
};

}  // namespace psi
