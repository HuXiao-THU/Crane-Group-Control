"""
Discrete version of a crane for DQN and this is even more simple without the hook and the car
"""
import math
import numpy as np

class Crane(object):
    def __init__(self):
        self.ID = 0
        self.x = 100
        self.y = 100
        self.R1 = 30
        self.R2 = 8

        self.arm_theta = 0
        self.arm_omega = 0
        self.car_pos = 0
        self.hook_height = 0

        self.car_limit_near_end = 3     # 小车近端距离限制
        self.car_limit_far_end = 30     # 小车远端距离限制
        self.height = 10                # 塔吊大臂高度，即吊钩最高高度

        self.reset()
    
    def rotate(self, power):
        """
        change of speed of the arm

        paras:
        power(int): -1 to 1
        """
        self.arm_omega += power
        self.arm_omega = max(-4, min(4, self.arm_omega))

        self.arm_theta += self.arm_omega
        if self.arm_theta >= 360:
            self.arm_theta -= 360
        if self.arm_theta < 0:
            self.arm_theta += 360
    
    def moveCar(self, distance):
        """
        move the car by the distance

        paras:
        distance(int): -1 to 1
        """
        self.car_pos += distance
        self.car_pos = max(self.car_limit_near_end, min(self.car_limit_far_end, self.car_pos))

    def moveHook(self, h):
        """
        move the hook by h

        paras:
        h(int): -1 to 1
        """
        self.hook_height += h
        self.hook_height = max(0, min(self.height, self.hook_height))

    def reset(self):
        """
        reset the state of the crane randomly
        """
        self.arm_theta = np.random.randint(0, 360)
        self.arm_omega = 0
        self.car_pos = np.random.randint(self.car_limit_near_end, self.car_limit_far_end + 1)
        self.hook_height = np.random.randint(0, self.height)