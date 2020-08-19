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
        # 常量
        self.crane = Crane()
        self.observation_space = 7  # (arm_omega, car_speed, hook_height, load, delta_theta, delta_x, delta_h)
        self.action_space = 3       # (arm_power, car_power, hook_power)
        self.dt = 0.1               # 模拟器运行时的时间精度，单位为秒
        self.radius_threshold = 0.3 # 进入目标点的（半径）距离阈值
        self.speed_threshold = 0.01 # 静止阈值
        self.total_t = 2000         # 一个episode的最大长度
        # self.opt_ratio = 10         # 每个操作对应持续几个dt

        # 运行状态变量
        self.target_theta = 0.0     # 下一个运行目标的极角
        self.target_r = 0.0         # 极径
        self.target_h = 0.0         # 高度
        self.target_load = 0.0      # 重量
        self.new_load = True        # 是否是装货，True是吊新的货物，False是卸货

        # 系统变量
        self.t = 0                  # 当前时刻
        self.count = 0              # 一个episode中完成的【到达目的地】次数，包括装载和卸载

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
        self.target_r = self.crane.car_limit_near_end + (self.crane.car_limit_far_end - self.crane.car_limit_near_end) * random.random()
        self.target_h = self.crane.height * random.random()
        self.target_load = self.crane.min_load + (self.crane.max_load - self.crane.min_load) * random.random()
        self.new_load = True

        self.t = 0
        self.count = 0

        return self.getState()

    def step(self, action):
        """
        do the action, return the tuple of (state, reward, done, _)

        params:
            action (list): [arm_power, car_power, hook_power], all -1.0 to 1.0
        """
        self.t += 1
        # do the action
        self.crane.rotate(action[0])
        self.crane.moveCar(action[1])
        self.crane.moveHook(action[2])
        self.crane.update(self.dt)

        # calculate the reward
        r = -1.0            # 每个时刻时间成本
        distCost = 0.0      # 距离Cost
        speedCost = 0.0     # 速度Cost

        dist = self.getDistance()
        speed = self.crane.getSpeed()
        distCost = self.getDistCost(dist)
        # print("dist: ", dist, "\t distCost: ", distCost)
        r -= distCost
        # r -= self.getSpeedCost(speed) # 想清楚在外面空间需不需要控制速度

        if dist < self.radius_threshold:
            speedCost = self.getSpeedCost(speed)
            r -= speedCost

            if speed < self.speed_threshold:
                r += 10000
                self.count += 1
                # 装货或卸货
                if self.new_load:
                    self.crane.loadWeight(self.target_load)
                    self.target_load = 0
                    self.new_load = False
                else:
                    self.crane.unloadWeight()
                    self.target_load = self.crane.min_load + (self.crane.max_load - self.crane.min_load) * random.random()
                    self.new_load = True
                # 生成新位置
                self.target_theta = random.random() * 2 * pi
                self.target_r = self.crane.car_limit_near_end + (self.crane.car_limit_far_end - self.crane.car_limit_near_end) * random.random()
                self.target_h = self.crane.height * random.random()

        # check if is done
        # 到达目的地就算完成这个episode
        done = False if self.count < 1 or self.t >= self. total_t else True

        # return
        return (self.getState(), r, done, {'distCost':distCost, 'speedCost':speedCost})

    def getState(self):
        """
        return the state of the agent

        (arm_omega, car_speed, hook_height, load, delta_theta, delta_x, delta_h)
        """
        state = []
        dtheta = self.crane.arm_theta - self.target_theta
        while dtheta < 0:
            dtheta += 2 * pi
        while dtheta >= 2 * pi:
            dtheta -= 2 * pi
        state.append(self.crane.arm_omega)
        state.append(self.crane.car_speed)
        state.append(self.crane.hook_height)
        state.append(self.crane.load)
        state.append(dtheta)
        state.append(self.crane.car_pos - self.target_r)
        state.append(self.crane.hook_height - self.target_h)

        return np.array(state)

    def getDistance(self):
        """
        return the distance of the hook to the target
        """
        hook_x = self.crane.car_pos * math.cos(self.crane.arm_theta)
        hook_y = self.crane.car_pos * math.sin(self.crane.arm_theta)
        hook_h = self.crane.hook_height

        target_x = self.target_r * math.cos(self.target_theta)
        target_y = self.target_r * math.sin(self.target_theta)

        dist = ( (hook_x - target_x)**2 + (hook_y - target_y)**2 + (hook_h - self.target_h)**2 )**0.5
        return dist

    def getDistCost(self, dist):
        """
        return the cost of distance

        0 ~ threshold: linear, 0.0 - 0.5
        threshold ~ inf: tanh, 0.5 - 1.0
        """
        # if dist <= self.radius_threshold:
        #     return 0.5 * dist / self.radius_threshold
        # else:
        #     return 0.5 + 0.5 * math.tanh((dist - self.radius_threshold) / 100.0 )
        return 0.1 * dist

    def getSpeedCost(self, speed):
        """
        return the cost of speed when the dist is lower than the dist_threshold

        0 ~ threshold:  0
        threshold ~ inf: exp, 0 - inf
        """
        if speed <= self.speed_threshold:
            return 0
        else:
            return math.exp(speed - self.speed_threshold)
    
    def getDetailToShow(self):
        """
        return a dict containing the detail data for debug
        """
        details = {}
        details['time'] = self.t * self.dt
        details['theta'] = self.crane.arm_theta / pi
        details['car_pos'] = self.crane.car_pos
        details['car_speed'] = self.crane.car_speed
        details['hook_height'] = self.crane.hook_height
        details['omega'] = self.crane.arm_omega
        details['alpha'] = self.crane.arm_alpha
        return details