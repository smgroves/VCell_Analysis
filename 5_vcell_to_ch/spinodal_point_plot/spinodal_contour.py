import numpy as np
import matplotlib.pyplot as plt

# Define your grid and function
x = np.linspace(0, 10, 100)
y = np.linspace(5, 20, 100)
X, Y = np.meshgrid(x, y)
Z = ((3-np.sqrt(3))/6)*(Y - X) + X

# Create contour plot with light grey grid

plt.figure(figsize=(8, 5))
plt.grid(color='lightgrey', linestyle='--', linewidth=0.5)
contour = plt.contour(X, Y, Z, levels=30)

#Add y = x line
plt.plot(x, x, 'r--', label='y = x')
# Add labels to the contours
plt.clabel(contour, inline=True, fontsize=10)

plt.colorbar(contour)
plt.xlim(0, 10)
plt.ylim(5, 20)
plt.ylabel('Condensate Well Concentration (max)')
plt.xlabel('Soluble Well Concentration (min)')
plt.title('Contour Plot with Labels')
plt.show()