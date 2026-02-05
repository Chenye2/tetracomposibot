import matplotlib.pyplot as plt
import numpy as np 

trial_r, score_r, best_r = np.loadtxt("randomsearch2.txt", delimiter=",", unpack=True)
trial_g, score_g, best_g = np.loadtxt("genetic_algorithms.txt", delimiter=",", unpack=True)

plt.plot(trial_r, best_r, label="Randomsearch2", color="red")
plt.plot(trial_g, best_g, label="GeneticAlgorithms", color="green")

plt.xlabel("Evaluations")
plt.ylabel("Meilleur Score")
plt.legend()
plt.show()
