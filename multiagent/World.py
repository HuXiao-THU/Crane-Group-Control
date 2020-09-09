import random
import math
import tkinter
import time
import numpy as np
import csv
import queue
from math import pi
from Crane_discrete import Crane
from render import Renderer
from data import *

class Target(object):
    def __init__(self, crane):
        self.theta = 0
        self.x = 0
        self.h = 0
        self.done = False
        self.crane = crane
        self.ID = self.crane.ID

    def reset(self, data=None):
        if data == None:
            self.theta = np.random.randint(0, 360)
            self.x = np.random.randint(self.crane.car_limit_near_end, self.crane.car_limit_far_end + 1)
            self.h = np.random.randint(0, self.crane.height)
        else:
            self.theta = data[1]
            self.x = data[2]
            self.h = data[3]
        self.done = False

class Line(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class World(object):
    def __init__(self, rendererPath='./data', loadingTarget = True):
        self.crane_list = []
        self.target_list = []
        self.data = loadData()
        self.loadingTarget = loadingTarget
        if loadingTarget:
            self.target_data0 = loadTargetData()
            self.target_data = None

        for line in self.data:
            crane = Crane()
            crane.ID = line[0]
            crane.x = line[1]
            crane.y = line[2]
            crane.R1 = line[3]
            crane.R2 = line[4]
            self.crane_list.append(crane)

        for crane in self.crane_list:
            target = Target(crane)
            self.target_list.append(target)

        self.observation_space = 4 * len(self.crane_list)  # (arm_theta, delta_theta, arm_omega) * of other cranes
        self.action_space = 3
        self.reward_sharing_ratio = 0.1
        self.collision_pairs = [(0,1),(0,2),(2,3),(1,3)]

        self.t = 0
        self.max_t = 720
        self.score = 0
        self.collision = False

        self.renderer = Renderer(rendererPath)

        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.collision = False
        if self.loadingTarget:
            self.target_data = copyTargetData(self.target_data0)

        for target in self.target_list:
            target_state = None
            if self.loadingTarget and not self.target_data[target.ID].empty():
                target_state = self.target_data[target.ID].get()
            target.reset(target_state)

        clear = False
        while not clear:
            clear = True
            for crane in self.crane_list:
                crane.reset()
            for pair in [(0,1),(0,2),(2,3),(1,3)]:
                clear = clear and not self.checkCollision(pair[0], pair[1])
                if not clear:
                    break

        return self.getState()

    def step(self, action):
        """
        paras:
        action(list of int): index of each agent's action, 0 to 2
        """
        r = [-1 for crane in self.crane_list]
        for crane in self.crane_list:
            ID = crane.ID
            target = self.target_list[ID]
            car_power = 0
            hook_power = 0
            if target.done:
                r[ID] += 1
            if crane.car_pos > target.x:
                car_power = -1
            elif crane.car_pos < target.x:
                car_power = 1
            if crane.hook_height > target.h:
                hook_power = -1
            elif crane.hook_height < target.h:
                hook_power = 1

            rotate_power = 0
            
            if action[ID] == 1:
                rotate_power = 1
                if target.done:
                    r[ID] -=0.05
            elif action[ID] == 2:
                rotate_power = -1
                if target.done:
                    r[ID] -=0.05

            crane.rotate(rotate_power)
            crane.moveCar(car_power)
            crane.moveHook(hook_power)

            if crane.arm_theta == target.theta and not target.done:
                r[ID] += 200 - abs(crane.arm_omega) * 10
                target.done = True
                if self.loadingTarget and not self.target_data[crane.ID].empty():
                    target_state = self.target_data[crane.ID].get()
                    target.reset(target_state)

        # share reward
        s = sum(r)
        for crane in self.crane_list:
            r[crane.ID] += s * self.reward_sharing_ratio
        
        done = True
        for target in self.target_list:
            done = done and target.done

        # 碰撞检测，手动写一下哪些有必要检测的
        for pair in [(0,1),(0,2),(2,3),(1,3)]:
            if self.checkCollision(pair[0], pair[1]):
                r[pair[0]] -= 1000
                r[pair[1]] -= 1000
                done = True
                self.collision = True

        if self.t > self.max_t:
            done = True
            for ID in range(len(self.crane_list)):
                if not self.target_list[ID].done:
                    r[ID] -= 200
                    for i in range(len(self.crane_list)):
                        r[i] -= 200

        # return state, r, done, _
        self.score += sum(r)
        # print(r,"Target0: ", self.target_list[0].done," Target1: ", self.target_list[1].done)
        return (self.getState(), r, done, {'score':self.score, 'collision':self.collision})

    def getState(self):
        """
        get the state of n * (arm_theta, delta_theta, arm_omega)
        """
        state = []
        for crane in self.crane_list:
            delta_theta = crane.arm_theta - self.target_list[crane.ID].theta
            if delta_theta >= 360:
                delta_theta -= 360
            if delta_theta < 0:
                delta_theta += 360
            state.append(crane.arm_theta)
            state.append(delta_theta)
            state.append(crane.arm_omega)
            state.append(self.target_list[crane.ID].done)
        return np.array(state)

    def render(self):
        """
        render the visualization
        """
        self.renderer.render(self.crane_list, self.target_list, {'score':self.score, 'time':self.t})
        # print(self.crane.arm_theta, "  ", self.crane.car_pos)
        # time.sleep(0.2)

    def getAgentNum(self):
        """
        return the number of the agents
        """
        return len(self.data)

    def checkCollision(self, craneID1, craneID2):
        """
        check collision of two cranes
        """
        crane = self.crane_list[craneID1]
        l1 = Line(crane.x - math.cos(crane.arm_theta / 180 * pi) * crane.R2,
                    crane.y - math.sin(crane.arm_theta / 180 * pi) * crane.R2,
                    crane.x + math.cos(crane.arm_theta / 180 * pi) * crane.R1,
                    crane.y + math.sin(crane.arm_theta / 180 * pi) * crane.R1)
        crane = self.crane_list[craneID2]
        l2 = Line(crane.x - math.cos(crane.arm_theta / 180 * pi) * crane.R2,
                    crane.y - math.sin(crane.arm_theta / 180 * pi) * crane.R2,
                    crane.x + math.cos(crane.arm_theta / 180 * pi) * crane.R1,
                    crane.y + math.sin(crane.arm_theta / 180 * pi) * crane.R1)

        # 快速排斥实验
        if  max(l1.x1, l1.x2) < min(l2.x1, l2.x2) or\
            max(l1.y1, l1.y2) < min(l2.y1, l2.y2) or\
            max(l2.x1, l2.x2) < min(l1.x1, l1.x2) or\
            max(l2.y1, l2.y2) < min(l1.y1, l1.y2):
            return False

        # 跨越实验
        if (((l1.x1 - l2.x1)*(l2.y2 - l2.y1) - (l1.y1 - l2.y1)*(l2.x2 - l2.x1))*\
        ((l1.x2 - l2.x1)*(l2.y2 - l2.y1) - (l1.y2 - l2.y1)*(l2.x2 - l2.x1))) > 0 or\
        (((l2.x1 - l1.x1)*(l1.y2 - l1.y1) - (l2.y1 - l1.y1)*(l1.x2 - l1.x1))*\
        ((l2.x2 - l1.x1)*(l1.y2 - l1.y1) - (l2.y2 - l1.y1)*(l1.x2 - l1.x1))) > 0:
            return False
        else:
            return True

if __name__ == '__main__':
    env = World()
    env.crane_list[0].arm_theta = 10
    env.crane_list[1].arm_theta = 170
    print(env.checkCollision(0,1))