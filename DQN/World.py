import random
import math
import tkinter
import numpy as np
from math import pi
from Crane_discrete import Crane

class World(object):
    def __init__(self):
        self.crane = Crane()
        self.target_x = 0
        self.target_h = 0

        self.observation_space = 4  # (arm_theta, arm_omega, delta_x, delta_h)
        self.action_space = 7

        self.t = 0
        self.max_t = 120

        self.reset()

    def reset(self):
        self.t = 0
        self.target_x = np.random.randint(self.crane.car_limit_near_end, self.crane.car_limit_far_end + 1)
        self.target_h = np.random.randint(0, self.crane.height)
        self.crane.reset()

        return self.getState()

    def step(self, action):
        """
        paras:
        action(int): 0 to 6, index of the action
        """
        rotate_power = 0
        car_power = 0
        hook_power = 0

        if action == 1:
            rotate_power = 1
        elif action == 2:
            rotate_power = -1
        elif action == 3:
            car_power = 1
            self.crane.moveCar(car_power)
        elif action == 4:
            car_power = -1
            self.crane.moveCar(car_power)
        elif action == 5:
            hook_power = 1
            self.crane.moveHook(hook_power)
        elif action == 6:
            hook_power = -1
            self.crane.moveHook(hook_power)
        
        self.crane.rotate(rotate_power)
        
        # reward
        r = -1
        done = False

        if self.t > self.max_t:
            done = True

        if self.crane.arm_theta == 0:
            done = True
            r += 200
            r -= abs(self.crane.arm_omega) * 25
            r -= abs(self.crane.car_pos - self.target_x)
            if self.crane.hook_height < self.target_h :
                r -= 200
            else:
                r -= self.crane.hook_height - self.target_h

        # return state, r, done, _
        return (self.getState(), r, done, {})

    def getState(self):
        """
        get the state of (arm_theta, arm_omega, delta_x, delta_h)
        """
        return np.array([self.crane.arm_theta, self.crane.arm_omega, self.crane.car_pos - self.target_x, self.crane.hook_height - self.target_h])

    def render(self):
        """
        render the visualization
        """
        pass