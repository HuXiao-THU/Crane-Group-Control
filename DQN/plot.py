import matplotlib.pyplot as plt
import pickle
import numpy as np
from collections import deque

with open('./DQN/scores_1024.pkl', 'rb') as f:
    scores = pickle.load(f)

scores_window = deque(maxlen=100)
avg_scores = []
for score in scores:
    scores_window.append(score)
    avg_scores.append(np.mean(scores_window))

fig = plt.figure()
ax = fig.add_subplot(111)
plt.semilogx(np.arange(len(scores)), scores, linewidth=0.5, label='score')
plt.semilogx(np.arange(len(avg_scores)), avg_scores, linewidth=2, label='MA score')
plt.legend(['score', 'MA score'])
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()
# fig.savefig('./DQN/training_curve.png')