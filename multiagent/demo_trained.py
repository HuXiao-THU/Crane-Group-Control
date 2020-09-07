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
agents = [Agent(state_size=env.observation_space, action_size=env.action_space, seed=0) for i in range(env.getAgentNum())]

with open('./multiagent/checkpoint.pkl', 'rb') as f:
    ckpt = pickle.load(f)
for i, agent in enumerate(agents):
    agent.qnetwork_target.load_state_dict(ckpt['qnetwork_target'][i])
    agent.qnetwork_local.load_state_dict(ckpt['qnetwork_local'][i])

# watch an untrained agent
state = env.reset()
for j in range(720):
    action = []
    for k in range(env.getAgentNum()):
        action.append(agents[k].act(state))
    env.render()
    state, reward, done, _ = env.step(action)
    if done:
        break 