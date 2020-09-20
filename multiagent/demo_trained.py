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

def main():
    dt = 0.05

    env = World()
    agents = [Agent(state_size=env.observation_space, action_size=env.action_space, seed=0) for i in range(env.getAgentNum())]

    with open('./multiagent/checkpoint.pkl', 'rb') as f:
        ckpt = pickle.load(f)
    for i, agent in enumerate(agents):
        agent.qnetwork_target.load_state_dict(ckpt['qnetwork_target'][i])
        agent.qnetwork_local.load_state_dict(ckpt['qnetwork_local'][i])

    # collision = 0
    # test_num = 1000
    # scores = []
    # for i in range(1, test_num + 1):
    #     state = env.reset()
    #     score = 0
    #     for j in range(720):
    #         action = []
    #         for k in range(env.getAgentNum()):
    #             action.append(agents[k].act(state))
    #         state, reward, done, info = env.step(action)
    #         score += sum(reward)
    #         if done:
    #             if info['collision']:
    #                 collision += 1
    #             scores.append(score)
    #             break
    #     print('\rtest num: {:d}/{:d}\tcollision num: {:d}\tcollision rate: {:.2f}'.format(i, test_num, collision, collision/i), end='')

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # plt.plot(np.arange(len(scores)), scores, linewidth=0.5, label='score')
    # plt.legend(['score'])
    # plt.ylabel('Score')
    # plt.xlabel('Episode #')
    # fig.savefig('./multiagent/test_result.png')

    # watch an untrained agent
    while True:
        restart = False
        last_time = time.time()
        state = env.reset()
        for j in range(720):
            while True:
                restart = env.render()
                current_time = time.time()
                if current_time > last_time + dt:
                    last_time = current_time
                    break
            action = []
            for k in range(env.getAgentNum()):
                action.append(agents[k].act(state))
            state, reward, done, _ = env.step(action)
            if done or restart:
                env.render()
                # time.sleep(10)
                break 
        while not restart:
            restart = env.render()

if __name__ == "__main__":
    main()