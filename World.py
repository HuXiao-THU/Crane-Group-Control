"""
This file contains the world that the agents are in
"""
from Crane_continuous import Crane
import numpy as np
import math
from math import pi
import random

class World(object):
    def __init__(self):
        super().__init__()
        self.crane = Crane()
        self.observation_space = 7  # (arm_omega, car_speed, hook_height, load, delta_theta, delta_x, delta_h)
        self.action_space = 3       # (arm_power, car_power, hook_power)
        self.dt = 0.1               # 模拟器运行时的时间精度，单位为秒

        self.target_theta = 0.0     # 下一个运行目标的极角
        self.target_x = 0.0         # 极径
        self.target_h = 0.0         # 高度
        self.target_load = 0.0      # 重量
        self.new_load = True        # 是否是装货，True是吊新的货物，False是卸货

        self.total_t = 2000         # 一个episode的最大长度
        self.t = 0                  # 当前时刻

        self.reset()
        
    def reset(self):
        """
        reset the environment, return the state
        """
        self.crane.arm_theta = random.random() * 2 * pi
        self.crane.car_pos = self.crane.car_limit_near_end + (self.crane.car_limit_far_end - self.crane.car_limit_near_end) * random.random()
        self.crane.hook_height = self.crane.height

        self.crane.arm_omega = 0.0
        self.crane.arm_alpha = 0.0
        self.crane.car_speed = 0.0
        self.crane.car_acceleration = 0.0
        self.crane.hook_speed = 0.0
        self.crane.load = 0.0

        self.target_theta = random.random() * 2 * pi
        self.target_x = self.crane.car_limit_near_end + (self.crane.car_limit_far_end - self.crane.car_limit_near_end) * random.random()
        self.target_h = self.crane.height * random.random()
        self.target_load = self.crane.min_load + (self.crane.max_load - self.crane.min_load) * random.random()

        return getState()

    def step(self, action):
        """
        do the action, return the tuple of (state, reward, done, _)

        params:
            action (list): [arm_power, car_power, hook_power], all -1.0 to 1.0
        """
        pass

    def getState(self):
        """
        return the state of the agent

        (arm_omega, car_speed, hook_height, load, delta_theta, delta_x, delta_h)
        """
        state = []
        state.append(self.crane.arm_omega)
        state.append(self.crane.car_speed)
        state.append(self.crane.hook_height)
        state.append(self.crane.load)
        state.append((self.crane.arm_theta - self.target_theta) % (2*pi))
        state.append(self.crane.car_pos - self.target_x)
        state.append(self.crane.hook_height - self.target_h)

        return state