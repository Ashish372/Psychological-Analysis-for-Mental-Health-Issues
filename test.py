import numpy as np
from os import path, getcwd
import matplotlib.pyplot as plt
class test1:
     def __init__(self, a):
         # d = getcwd()
         X = ['Somatic', 'Anxiety', 'Emotional', 'Disorganizatio', 'Guilt', 'Tension', 'Mannerism', 'Grandiosity', 'Depressive', 'Hostility', 'Suspiciousness', 'Hallucination', 'Retardation', 'Uncooperativeness', 'unusual thought', 'Blunt effect', 'Excitement', 'Disorientation']
         c = a
         X_axis = np.arange(len(X))
         # plt.ylim(bottom=0)

         plt.figure(figsize=[10, 10])

         # plt.bar(X_axis - 0.2, MHP, 0.4, label='mentally health person')
         plt.barh(X_axis + 0.2, c, label='client')

         plt.yticks(X_axis, X)
         plt.xlabel("Questions")
         plt.ylabel("Score")
         plt.title("BPRS")

         # plt.show()
         plt.savefig("static/test2.png")
         plt.close()
