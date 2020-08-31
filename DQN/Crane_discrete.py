"""
Discrete version of a crane
"""
import math
import numpy as np

class Crane(object):
    def __init__(self):
        self.arm_theta = 0
        self.arm_omega = 0
        self.car_pos = 0
        self.hook_height = 0