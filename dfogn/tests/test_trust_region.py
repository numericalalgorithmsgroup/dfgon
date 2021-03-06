"""

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

The development of this software was sponsored by NAG Ltd. (http://www.nag.co.uk)
and the EPSRC Centre For Doctoral Training in Industrially Focused Mathematical
Modelling (EP/L015803/1) at the University of Oxford. Please contact NAG for
alternative licensing.

"""

# Ensure compatibility with Python 2
from __future__ import absolute_import, division, print_function, unicode_literals

from math import sqrt
import numpy as np
import unittest

from dfogn.trust_region import trsbox
from dfogn.util import calculate_model_value, to_upper_triangular_vector, right_multiply_hessian


def cauchy_pt(g, hess, delta):
    # General expression for the Cauchy point
    crv = np.dot(g, right_multiply_hessian(hess, g))
    gnorm = np.linalg.norm(g)
    if crv <= 0.0:
        alpha = delta / gnorm
    else:
        alpha = min(delta / gnorm, gnorm**2 / crv)
    s = -alpha * g
    red = calculate_model_value(g, hess, s)
    crvmin = np.dot(s, right_multiply_hessian(hess, s)) / np.dot(s, s)
    if crvmin < 0.0:
        crvmin = -1.0
    return s, red, crvmin


def cauchy_pt_box(g, hess, delta, lower, upper):
    # General expression for the Cauchy point, lower <= s <= upper
    crv = np.dot(g, right_multiply_hessian(hess, g))
    gnorm = np.linalg.norm(g)
    if crv <= 0.0:
        alpha = delta / gnorm
    else:
        alpha = min(delta / gnorm, gnorm**2 / crv)
    # print("alpha = %g" % alpha)
    # Then cap with bounds:
    for i in range(len(g)):
        if g[i] > 0:  # s[i] negative, will hit lower
            alpha = min(alpha, -lower[i] / g[i])
        elif g[i] < 0:  # s[i] positive, will hit upper
            alpha = min(alpha, -upper[i] / g[i])
        # print("alpha = %g after i=%g" % (alpha, i))
    s = -alpha * g
    red = calculate_model_value(g, hess, s)
    crvmin = np.dot(s, right_multiply_hessian(hess, s)) / np.dot(s, s)
    if crvmin < 0.0:
        crvmin = -1.0
    return s, red, crvmin


class TestUncInternal(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        hess = to_upper_triangular_vector(H)
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer for internal minimum?
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, hess, Delta)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        print(crvmin)
        self.assertAlmostEqual(crvmin, 1.2, 'Wrong crvmin')


class TestUncBdry(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        hess = to_upper_triangular_vector(H)
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, hess, Delta)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        self.assertAlmostEqual(crvmin, 0.0, 'Wrong crvmin')


class TestUncBdry2(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = 5.0 / 12.0
        hess = to_upper_triangular_vector(H)
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, hess, Delta)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        self.assertAlmostEqual(crvmin, 0.0, 'Wrong crvmin')


class TestUncBdry3(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([0.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = 0.5
        hess = to_upper_triangular_vector(H)
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([0.0, 0.0, -0.5])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, hess, Delta)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        self.assertAlmostEqual(crvmin, 0.0, 'Wrong crvmin')
        # self.assertAlmostEqual(crvmin, crvmin_cauchy, 'Wrong crvmin')


class TestUncHard(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([0.0, 0.0, 1.0])
        H = np.array([[-2.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
        Delta = sqrt(2.0)
        hess = to_upper_triangular_vector(H)
        xopt = np.zeros((n,))
        sl = -1e20 * np.ones((n,))
        su = 1e20 * np.ones((n,))
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([1.0, 0.0, -1.0])  # non-unique solution
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt(g, hess, Delta)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        self.assertAlmostEqual(crvmin, 0.0, 'Wrong crvmin')


class TestConInternal(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 2.0
        hess = to_upper_triangular_vector(H)
        xopt = np.ones((n,))  # trying nonzero (since bounds inactive)
        sl = xopt + np.array([-0.5, -10.0, -10.0])
        su = xopt + np.array([10.0, 10.0, 10.0])
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([-1.0, 0.0, -0.5])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer for internal minimum?
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt_box(g, hess, Delta, sl-xopt, su-xopt)
        # print(s_cauchy)
        # print(d)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.all(gnew == g + right_multiply_hessian(hess, d)), 'Wrong gnew')
        print(crvmin)
        self.assertAlmostEqual(crvmin, -1.0, 'Wrong crvmin')


class TestConBdry(unittest.TestCase):
    def runTest(self):
        n = 3
        g = np.array([1.0, 0.0, 1.0])
        H = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]])
        Delta = 5.0 / 12.0
        hess = to_upper_triangular_vector(H)
        xopt = np.zeros((n,))
        sl = xopt + np.array([-0.3, -0.01, -0.1])
        su = xopt + np.array([10.0, 1.0, 10.0])
        d, gnew, crvmin = trsbox(xopt, g, hess, sl, su, Delta)
        true_d = np.array([-1.0 / 3.0, 0.0, -0.25])
        est_min = calculate_model_value(g, hess, d)
        true_min = calculate_model_value(g, hess, true_d)
        # Hope to get actual correct answer
        # self.assertTrue(np.all(d == true_d), 'Wrong answer')
        # self.assertAlmostEqual(est_min, true_min, 'Wrong min value')
        s_cauchy, red_cauchy, crvmin_cauchy = cauchy_pt_box(g, hess, Delta, sl - xopt, su - xopt)
        self.assertTrue(est_min <= red_cauchy, 'Cauchy reduction not achieved')
        self.assertTrue(np.max(np.abs(gnew - g - right_multiply_hessian(hess, d))) < 1e-10, 'Wrong gnew')
        print(crvmin)
        self.assertAlmostEqual(crvmin, -1.0, 'Wrong crvmin')
        # self.assertAlmostEqual(crvmin, crvmin_cauchy, 'Wrong crvmin')

