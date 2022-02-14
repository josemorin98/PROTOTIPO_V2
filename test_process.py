from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# df = pd.read_csv("/test/files/rezago/IRS_mpios_2000.csv")
df = pd.read_csv("/test/files/muertes/TasaD.csv")

corr = df.corr()
# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(9, 9))

# Draw the heatmap with the mask and correct aspect ratio
ax = sns.heatmap(corr, annot=True, linewidths=.5, vmin=0, vmax=1, cbar_kws={'label': 'colorbar title'})
sns.set(font_scale=.1)
plt.show()
