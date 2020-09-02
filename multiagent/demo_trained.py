import random
import torch
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from World import World
from dqn_agent import Agent

env = World()
agent0 = Agent(state_size=env.observation_space, action_size=env.action_space, seed=0)
agent1 = Agent(state_size=env.observation_space, action_size=env.action_space, seed=0)
d = torch.load('./multiagent/checkpoint.pth')
agent0.qnetwork_local.load_state_dict(d['agent0'])
agent1.qnetwork_local.load_state_dict(d['agent1'])

# watch an untrained agent
state = env.reset()
for j in range(120):
    action0 = agent0.act(state)
    action1 = agent1.act(state)
    action = [action0, action1]
    env.render()
    state, reward, done, _ = env.step(action)
    if done:
        break 