import matplotlib.pyplot as plt
import pickle
import numpy as np
from collections import deque

with open('./multiagent/checkpoint.pkl', 'rb') as f:
    ckpt = pickle.load(f)

scores = ckpt['scores'][50000:]
scores_window = deque(maxlen=100)
avg_scores = []
for score in scores:
    scores_window.append(score)
    avg_scores.append(np.mean(scores_window))

fig = plt.figure()
ax = fig.add_subplot(111)
# plt.semilogx(np.arange(len(scores)), scores, linewidth=0.5, label='score')
# plt.semilogx(np.arange(len(avg_scores)), avg_scores, linewidth=2, label='MA score')
plt.plot(np.arange(len(scores)), scores, linewidth=0.5, label='score')
plt.plot(np.arange(len(avg_scores)), avg_scores, linewidth=2, label='MA score')
plt.legend(['score', 'MA score'])
plt.ylabel('Score')
plt.xlabel('Episode #')
# plt.show()
fig.savefig('./multiagent/training_curve_2_new.png')