#!/usr/bin/python
# Support for python2
from __future__ import print_function
#Modify system path
import sys
sys.path.append('../pycThermopack/')
# Importing pyThermopack
from pyctp import saftvrqmie
# Importing Numpy (math, arrays, etc...)
import numpy as np
# Importing Matplotlib (plotting)
import matplotlib.pyplot as plt

# Instanciate and init PeTS object
qSAFT = saftvrqmie.saftvrqmie()
qSAFT.init("He,H2,Ne")
qSAFT.set_tmin(temp=2.0)

# Plot phase envelope
z = np.array([0.01, 0.89, 0.1])
T, P, v = qSAFT.get_envelope_twophase(1.0e4, z, maximum_pressure=1.5e7, calc_v=True)
Tc, vc, Pc = qSAFT.critical(z)
plt.plot(T, P*1.0e-6)
plt.plot([Tc], [Pc*1.0e-6], "ko")
plt.ylabel(r"$P$ (MPa)")
plt.xlabel(r"$T$ (K)")
plt.title("SAFT-VRQ Mie phase diagram")
plt.show()
plt.clf()
