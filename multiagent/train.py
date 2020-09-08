import random
import torch
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from World import World
from dqn_agent import Agent

def main():
    env = World()
    agents = [Agent(state_size=env.observation_space, action_size=env.action_space, seed=0) for i in range(env.getAgentNum())]
    scores = dqn(env, agents)
    with open('./multiagent/scores.pkl', 'wb') as f:
        pickle.dump(scores, f, protocol=pickle.HIGHEST_PROTOCOL)

    # plot the scores
    scores_window = deque(maxlen=100)
    avg_scores = []
    for score in scores:
        scores_window.append(score)
        avg_scores.append(np.mean(scores_window))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(np.arange(len(scores)), scores, linewidth=0.5, label='score')
    plt.plot(np.arange(len(avg_scores)), avg_scores, linewidth=2, label='MA score')
    plt.legend(['score', 'MA score'])
    plt.ylabel('Score')
    plt.xlabel('Episode #')
    fig.savefig('./multiagent/training_curve.png')

def dqn(env, agents, n_episodes=100000, max_t=720, eps_start=1.0, eps_end=0.01, eps_decay=0.995):
    """Deep Q-Learning.
    
    Params
    ======
        n_episodes (int): maximum number of training episodes
        max_t (int): maximum number of timesteps per episode
        eps_start (float): starting value of epsilon, for epsilon-greedy action selection
        eps_end (float): minimum value of epsilon
        eps_decay (float): multiplicative factor (per episode) for decreasing epsilon
    """
    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=100)  # last 100 scores
    eps = eps_start                    # initialize epsilon
    first_episode = 0

    if os.path.exists('./multiagent/checkpoint.pkl'):
        with open('./multiagent/checkpoint.pkl', 'rb') as f:
            ckpt = pickle.load(f)
        scores = ckpt['scores']
        for score in scores:
            scores_window.append(score)
        first_episode = ckpt['episode']
        eps = ckpt['eps']
        for i, agent in enumerate(agents):
            agent.qnetwork_target.load_state_dict(ckpt['qnetwork_target'][i])
            agent.qnetwork_local.load_state_dict(ckpt['qnetwork_local'][i])
            agent.optimizer.load_state_dict(ckpt['optimizer'][i])

    for i_episode in range(first_episode + 1, n_episodes+1):
        state = env.reset()
        score = 0
        done = False
        eps = 1/i_episode
        for t in range(max_t):
            actions = []
            for ID, agent in enumerate(agents):
                action = agent.act(state, eps)
                actions.append(action)
            next_state, reward, done, _ = env.step(actions)
            for ID, agent in enumerate(agents):
                agent.step(state, actions[ID], reward[ID], next_state, done)
            state = next_state
            score += sum(reward)
            if done:
                break 
        scores_window.append(score)       # save most recent score
        scores.append(score)              # save most recent score
        eps = max(eps_end, eps_decay*eps) # decrease epsilon
        print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)), end="")
        if i_episode % 1000 == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)))
            ckpt = {'qnetwork_local':[agent.qnetwork_local.state_dict() for agent in agents],
                    'qnetwork_target':[agent.qnetwork_target.state_dict() for agent in agents],
                    'optimizer':[agent.optimizer.state_dict() for agent in agents],
                    'episode':i_episode,
                    'scores':scores,
                    'eps':eps
            }
            with open('./multiagent/checkpoint.pkl', 'wb') as f:
                pickle.dump(ckpt, f)
            # torch.save(ckpt, './multiagent/checkpoint.pth')#要改成pickle！！！
        if np.mean(scores_window) >= 5500.0:
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode-100, np.mean(scores_window)))
            ckpt = {'qnetwork_local':[agent.qnetwork_local.state_dict() for agent in agents],
                    'qnetwork_target':[agent.qnetwork_target.state_dict() for agent in agents],
                    'optimizer':[agent.optimizer.state_dict() for agent in agents],
                    'episode':i_episode,
                    'scores':scores,
                    'eps':eps
            }
            with open('./multiagent/checkpoint.pkl', 'wb') as f:
                pickle.dump(ckpt, f)
            # torch.save(ckpt, './multiagent/checkpoint.pth')
            break
    return scores

if __name__ == '__main__':
    main()