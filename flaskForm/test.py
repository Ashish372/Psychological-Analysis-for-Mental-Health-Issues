import numpy as np
from os import path, getcwd
import matplotlib.pyplot as plt
class test1:
     def __init__(self, a):
         # d = getcwd()
         X = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18', 'Q19', 'Q20']
         MHP = [1, 2, 2, 4, 1, 2, 2, 4, 1, 2, 2, 4, 1, 2, 2, 4, 1, 2, 2, 4]
         c = [eval(i) for i in a]
         X_axis = np.arange(len(X))
         plt.figure(figsize=[10, 10])
         plt.bar(X_axis - 0.2, MHP, 0.4, label='mentally health person')
         plt.bar(X_axis + 0.2, c, 0.4, label='client')
         plt.xticks(X_axis, X, rotation=45)
         plt.xlabel("Questions")
         plt.ylabel("Score")
         plt.title("Question Number ")
         plt.legend()
         # plt.show()
         plt.savefig("static/test2.png")
         plt.close()