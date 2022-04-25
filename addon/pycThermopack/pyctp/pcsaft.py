# Support for python2
from __future__ import print_function
# Import ctypes
from ctypes import *
# Importing Numpy (math, arrays, etc...)
import numpy as np
# Import platform to detect OS
from sys import platform, exit
# Import os utils
from os import path
# Import thermo
from . import thermo, saft

c_len_type = thermo.c_len_type


class pcsaft(saft.saft):
    """
    Interface to PC-SAFT model
    """

    def __init__(self):
        """
        Initialize PC-SAFT specific function pointers
        """
        # Load dll/so
        saft.saft.__init__(self)

        # Init methods
        self.eoslibinit_init_pcsaft = getattr(
            self.tp, self.get_export_name("eoslibinit", "init_pcsaft"))
        # Tuning methods
        self.s_get_kij = getattr(self.tp, self.get_export_name(
            "saft_interface", "pc_saft_get_kij"))
        self.s_set_kij = getattr(self.tp, self.get_export_name(
            "saft_interface", "pc_saft_set_kij_asym"))
        # SAFT specific methods
        self.s_get_pure_params = getattr(self.tp, self.get_export_name("saft_interface", "pc_saft_get_pure_params"))
        self.s_set_pure_params = getattr(self.tp, self.get_export_name("saft_interface", "pc_saft_set_pure_params"))

        # Define parameters to be set by init
        self.nc = None

    #################################
    # Init
    #################################

    def init(self, comps, parameter_reference="Default", simplified=False):
        """Initialize PC-SAFT model in thermopack

        Args:
            comps (str): Comma separated list of component names
            parameter_reference (str, optional): Which parameters to use?. Defaults to "Default".
            simplified (bool): Use simplified PC-SAFT (Default False)
        """
        self.activate()
        comp_string_c = c_char_p(comps.encode('ascii'))
        comp_string_len = c_len_type(len(comps))
        ref_string_c = c_char_p(parameter_reference.encode('ascii'))
        ref_string_len = c_len_type(len(parameter_reference))
	if simplified:
            c_simplified = c_int(1)
        else:
            c_simplified = c_int(0)

        self.eoslibinit_init_pcsaft.argtypes = [c_char_p,
                                                c_char_p,
                                                POINTER( c_int ),
                                                c_len_type,
                                                c_len_type]

        self.eoslibinit_init_pcsaft.restype = None

        self.eoslibinit_init_pcsaft(comp_string_c,
                                    ref_string_c,
                                    byref( c_simplified ),
                                    comp_string_len,
                                    ref_string_len)
        self.nc = max(len(comps.split(" ")),len(comps.split(",")))

        # Map pure fluid parameters
        self.m = np.zeros(self.nc)
        self.sigma = np.zeros(self.nc)
        self.eps_div_kb = np.zeros(self.nc)
        for i in range(self.nc):
            self.m[i], self.sigma[i], self.eps_div_kb[i], eps, beta = \
                self.get_pure_params(i+1)


    def get_kij(self, c1, c2):
        """Get binary well depth interaction parameter

        Args:
            c1 (int): Component one
            c2 (int): Component two

        Returns:
            kij (float): Well depth interaction parameter
        """
        self.activate()
        c1_c = c_int(c1)
        c2_c = c_int(c2)
        kij_c = c_double(0.0)
        self.s_get_kij.argtypes = [POINTER(c_int),
                                   POINTER(c_int),
                                   POINTER(c_double)]

        self.s_get_kij.restype = None

        self.s_get_kij(byref(c1_c),
                       byref(c2_c),
                       byref(kij_c))
        return kij_c.value

    def set_kij(self, c1, c2, kij):
        """Set binary well depth interaction parameter

        Args:
            c1 (int): Component one
            c2 (int): Component two
            kij (float): Well depth interaction parameter
        """
        self.activate()
        c1_c = c_int(c1)
        c2_c = c_int(c2)
        kij_c = c_double(kij)
        self.s_set_kij.argtypes = [POINTER(c_int),
                                   POINTER(c_int),
                                   POINTER(c_double)]

        self.s_set_kij.restype = None

        self.s_set_kij(byref(c1_c),
                       byref(c2_c),
                       byref(kij_c))


    def set_pure_params(self, c, m, sigma, eps_div_kb, eps=0.0, beta=0.0):
        """Set pure fluid PC-SAFT parameters

        Args:
            c (int): Component index (FORTRAN)
            m (float): Mean number of segments
            sigma (float): Segment diameter (m)
            eps_div_kb (float): Well depth divided by Boltzmann's constant (K)
            eps (float): Association energy (J/mol)
            beta (float): Association volume (-)
        """
        self.m[c-1] = m
        self.sigma[c-1] = sigma
        self.eps_div_kb[c-1] = eps_div_kb

        self.activate()
        c_c = c_int(c)
        param_c = (c_double * 5)(m, sigma, eps_div_kb, eps, beta)
        self.s_set_pure_params.argtypes = [POINTER(c_int),
                                           POINTER(c_double)]

        self.s_set_pure_params.restype = None

        self.s_set_pure_params(byref(c_c),
                               param_c)

    def get_pure_params(self, c):
        """Get pure fluid PC-SAFT parameters

        Args:
            c (int): Component index (FORTRAN)
        Returns:
            m (float): Mean number of segments
            sigma (float): Segment diameter (m)
            eps_div_kb (float): Well depth divided by Boltzmann's constant (K)
            eps (float): Association energy (J/mol)
            beta (float): Association volume (-)
        """
        self.activate()
        c_c = c_int(c)
        param_c = (c_double * 5)(0.0)
        self.s_get_pure_params.argtypes = [POINTER(c_int),
                                           POINTER(c_double)]

        self.s_get_pure_params.restype = None

        self.s_get_pure_params(byref(c_c),
                               param_c)
        m, sigma, eps_div_kb, eps, beta = param_c
        return m, sigma, eps_div_kb, eps, beta
