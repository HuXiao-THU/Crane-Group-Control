import gym
import random
import torch
import numpy as np
import time
from collections import deque
import matplotlib.pyplot as plt
import pickle
import os

from World import World
from ddpg_agent import Agent

def train():
    env = World()
    agent = Agent(state_size=env.observation_space, action_size=env.action_space, random_seed=10)
    if os.path.exists('./DDPG/checkpoint_actor.pth'):
        checkpoint = torch.load('./DDPG/checkpoint_actor.pth')
        agent.actor_local.load_state_dict(checkpoint)
        agent.actor_target.load_state_dict(checkpoint)
    if os.path.exists('./DDPG/checkpoint_critic.pth'):
        checkpoint = torch.load('./DDPG/checkpoint_critic.pth')
        agent.critic_local.load_state_dict(checkpoint)
        agent.critic_target.load_state_dict(checkpoint)

    scores = ddpg(env, agent)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(np.arange(1, len(scores)+1), scores)
    plt.ylabel('Score')
    plt.xlabel('Episode #')
    # plt.show()
    fig.savefig('./train_curve.png')
    
    with open('./scores.pkl', 'b') as f:
        pickle.dump(scores, f)

def ddpg(env, agent, n_episodes=100000, max_t=120):
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
        if i_episode % 10 == 0:
            torch.save(agent.actor_local.state_dict(), './DDPG/checkpoint_actor.pth')
            torch.save(agent.critic_local.state_dict(), './DDPG/checkpoint_critic.pth')
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_deque)))   
    return scores

if __name__ == "__main__":
    train()