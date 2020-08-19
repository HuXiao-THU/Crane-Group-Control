import gym
import random
import torch
import numpy as np
import time
from collections import deque
import matplotlib.pyplot as plt

from World import World
from ddpg_agent import Agent

def train():
    env = World()
    agent = Agent(state_size=env.observation_space, action_size=env.action_space, random_seed=10)

    scores = ddpg(env, agent)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(np.arange(1, len(scores)+1), scores)
    plt.ylabel('Score')
    plt.xlabel('Episode #')
    plt.show()

def ddpg(env, agent, n_episodes=2000, max_t=1200):
    scores_deque = deque(maxlen=100)
    scores = []
    max_score = -np.Inf
    for i_episode in range(1, n_episodes+1):
        state = env.reset()
        agent.reset()
        score = 0.0
        for t in range(max_t):
            action = agent.act(state)
            # action[0] = -1.0 + 2.0 * random.random()
            next_state, reward, done, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward
            # details = env.getDetailToShow()
            # print("\rtime: {:.1f}, rotate_power: {:.3f}, theta: {:.4f}*pi, omega: {:.4f}, car_power: {:.3f}, hook_power: {:.3f}, car_pos: {:.2f}, hook_height: {:.2f}, distCost: {:.3f}, speedCost: {:.3f}".format(details['time'], action[0], details['theta'], details['omega'], action[1], action[2], details['car_pos'], details['hook_height'], _['distCost'], _['speedCost']), end="")
            # print("\rcar_power: {:.3f}, speed: {:.3f}, pos: {:.3f}".format(action[1], details['car_speed'], details['car_pos']), end='')
            # time.sleep(0.1)
            if done:
                break 
        scores_deque.append(score)
        scores.append(score)
        print('Episode {}\tAverage Score: {:.2f}\tScore: {:.2f}'.format(i_episode, np.mean(scores_deque), score))
        if i_episode % 100 == 0:
            torch.save(agent.actor_local.state_dict(), 'checkpoint_actor.pth')
            torch.save(agent.critic_local.state_dict(), 'checkpoint_critic.pth')
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_deque)))   
    return scores

if __name__ == "__main__":
    train()