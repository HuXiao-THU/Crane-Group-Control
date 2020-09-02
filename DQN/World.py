import random
import math
import tkinter
import time
import numpy as np
from math import pi
from Crane_discrete import Crane
from render import Renderer

class Target(object):
    def __init__(self):
        self.ID = 0
        self.theta = 0
        self.h = 0
        self.x = 0

class World(object):
    def __init__(self, rendererPath='./data'):
        self.crane = Crane()
        self.target = Target()
        self.target.x = 0
        self.target.h = 0

        self.observation_space = 4  # (arm_theta, arm_omega, delta_x, delta_h)
        self.action_space = 7

        self.t = 0
        self.max_t = 120
        self.score = 0

        self.renderer = Renderer(rendererPath)

        self.reset()

    def reset(self):
        self.t = 0
        self.target.x = np.random.randint(self.crane.car_limit_near_end, self.crane.car_limit_far_end + 1)
        self.target.h = np.random.randint(0, self.crane.height)
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
        # reward
        r = -1

        if action == 1:
            rotate_power = 1
        elif action == 2:
            rotate_power = -1
        elif action == 3:
            car_power = 1
            self.crane.moveCar(car_power)
            r -= 0.5
        elif action == 4:
            car_power = -1
            self.crane.moveCar(car_power)
            r -= 0.5
        elif action == 5:
            hook_power = 1
            self.crane.moveHook(hook_power)
            r -= 0.5
        elif action == 6:
            hook_power = -1
            self.crane.moveHook(hook_power)
            r -= 0.5
        
        self.crane.rotate(rotate_power)
        
        done = False

        if self.t > self.max_t:
            done = True

        if self.crane.arm_theta == 0:
            done = True
            r += 200
            r -= abs(self.crane.arm_omega) * 25
            r -= abs(self.crane.car_pos - self.target.x)
            if self.crane.hook_height < self.target.h :
                r -= 200
            else:
                r -= self.crane.hook_height - self.target.h

        # return state, r, done, _
        self.score += r
        return (self.getState(), r, done, {})

    def getState(self):
        """
        get the state of (arm_theta, arm_omega, delta_x, delta_h)
        """
        return np.array([self.crane.arm_theta, self.crane.arm_omega, self.crane.car_pos - self.target.x, self.crane.hook_height - self.target.h])

    def render(self):
        """
        render the visualization
        """
        self.renderer.render([self.crane], [self.target], {'score':self.score})
        print(self.crane.arm_theta, "  ", self.crane.car_pos)
        time.sleep(0.2)