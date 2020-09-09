import random
import torch
import pickle
import os
import numpy as np
import time
import matplotlib.pyplot as plt
from collections import deque
from World import World
from dqn_agent import Agent

dt = 0.017

env = World()
agents = [Agent(state_size=env.observation_space, action_size=env.action_space, seed=0) for i in range(env.getAgentNum())]

with open('./multiagent/checkpoint.pkl', 'rb') as f:
    ckpt = pickle.load(f)
for i, agent in enumerate(agents):
    agent.qnetwork_target.load_state_dict(ckpt['qnetwork_target'][i])
    agent.qnetwork_local.load_state_dict(ckpt['qnetwork_local'][i])

collision = 0
test_num = 100
for i in range(1, test_num + 1):
    state = env.reset()
    for j in range(720):
        action = []
        for k in range(env.getAgentNum()):
            action.append(agents[k].act(state))
        state, reward, done, info = env.step(action)
        if done:
            if info['collision']:
                collision += 1
            break
    print('\rtest num: {:d}/{:d}\tcollision num: {:d}\tcollision rate: {:.2f}'.format(i, test_num, collision, collision/i), end='')

# watch an untrained agent
last_time = time.time()
state = env.reset()
for j in range(720):
    while True:
        env.render()
        current_time = time.time()
        if current_time > last_time + dt:
            last_time = current_time
            break
    action = []
    for k in range(env.getAgentNum()):
        action.append(agents[k].act(state))
    state, reward, done, _ = env.step(action)
    if done:
        break 