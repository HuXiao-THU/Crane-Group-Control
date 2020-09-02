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
agent = Agent(state_size=env.observation_space, action_size=env.action_space, seed=0)
agent.qnetwork_local.load_state_dict(torch.load('./DQN/checkpoint.pth'))

# watch an untrained agent
state = env.reset()
for j in range(120):
    action = agent.act(state)
    env.render()
    state, reward, done, _ = env.step(action)
    if done:
        break 