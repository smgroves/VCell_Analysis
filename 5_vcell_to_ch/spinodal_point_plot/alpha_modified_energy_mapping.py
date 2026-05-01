import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ============================================================================
# PART 1: Equilibrium Mapping Plot
# ============================================================================

# Original scaling parameters
g_minus_0 = 4
g_plus_0 = 15
midpoint = (g_plus_0 + g_minus_0) / 2  # 9.5
range_g = g_plus_0 - g_minus_0  # 11

# Center point
center_g_minus = 4.2
center_g_plus = 8.4

# Create alpha values - 10 total points from -1 to +1
alpha_values = np.linspace(-1.0, 1.0, 10)

# Equilibrium points as a function of alpha
# These come from solving: ψ'(φ) = A, where A is from the common tangent construction
# For the double well potential with asymmetry, the equilibria shift nonlinearly
def get_equilibria(alpha):
    """
    Get phi equilibria for a given alpha value.
    These are computed from the common tangent construction on the modified energy.
    """
    # Known data points from your analysis
    equilibria_data = {
        -0.5: (-1.2075, 0.8742),
        -0.1: (-1.0350, 0.9683),
        0.0: (-1.0, 1.0),
        0.1: (-0.9683, 1.0350),
        0.5: (-0.8742, 1.2075),
    }
    
    # Find the closest data point for interpolation
    alpha_keys = sorted(equilibria_data.keys())
    
    if alpha in equilibria_data:
        return equilibria_data[alpha]
    
    # Linear interpolation between nearest points
    for i in range(len(alpha_keys) - 1):
        if alpha_keys[i] <= alpha <= alpha_keys[i+1]:
            alpha1, alpha2 = alpha_keys[i], alpha_keys[i+1]
            phi_m1, phi_p1 = equilibria_data[alpha1]
            phi_m2, phi_p2 = equilibria_data[alpha2]
            
            # Linear interpolation
            t = (alpha - alpha1) / (alpha2 - alpha1)
            phi_minus = phi_m1 + t * (phi_m2 - phi_m1)
            phi_plus = phi_p1 + t * (phi_p2 - phi_p1)
            return phi_minus, phi_plus
    
    # Extrapolate if outside range
    if alpha < alpha_keys[0]:
        alpha1, alpha2 = alpha_keys[0], alpha_keys[1]
        phi_m1, phi_p1 = equilibria_data[alpha1]
        phi_m2, phi_p2 = equilibria_data[alpha2]
        t = (alpha - alpha1) / (alpha2 - alpha1)
        phi_minus = phi_m1 + t * (phi_m2 - phi_m1)
        phi_plus = phi_p1 + t * (phi_p2 - phi_p1)
        return phi_minus, phi_plus
    else:
        alpha1, alpha2 = alpha_keys[-2], alpha_keys[-1]
        phi_m1, phi_p1 = equilibria_data[alpha1]
        phi_m2, phi_p2 = equilibria_data[alpha2]
        t = (alpha - alpha1) / (alpha2 - alpha1)
        phi_minus = phi_m1 + t * (phi_m2 - phi_m1)
        phi_plus = phi_p1 + t * (phi_p2 - phi_p1)
        return phi_minus, phi_plus

# Function to convert phi to g
def phi_to_g(phi, g_minus_scale, g_plus_scale):
    midpoint_scale = (g_plus_scale + g_minus_scale) / 2
    range_scale = g_plus_scale - g_minus_scale
    return midpoint_scale + (phi / 2) * range_scale

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# ============================================================================
# Subplot 1: Equilibrium Mapping
# ============================================================================

# Get colormap (viridis)
cmap = cm.get_cmap('viridis')
norm = plt.Normalize(vmin=alpha_values.min(), vmax=alpha_values.max())

# Plot mapped points for each alpha
for alpha in alpha_values:
    phi_m, phi_p = get_equilibria(alpha)
    g_m_mapped = phi_to_g(phi_m, center_g_minus, center_g_plus)
    g_p_mapped = phi_to_g(phi_p, center_g_minus, center_g_plus)
    
    color = cmap(norm(alpha))
    ax1.plot(g_m_mapped, g_p_mapped, 'o', markersize=10, color=color, 
            markeredgecolor='black', markeredgewidth=0.8, zorder=3)

# Plot initial point (alpha = 0)
ax1.plot(center_g_minus, center_g_plus, 'X', markersize=15, color='red', 
        markeredgecolor='darkred', markeredgewidth=1.5, zorder=4, label='α = 0')

# Highlight alpha = 0.5
idx_05 = np.argmin(np.abs(alpha_values - 0.5))
phi_m_05, phi_p_05 = get_equilibria(alpha_values[idx_05])
g_m_05 = phi_to_g(phi_m_05, center_g_minus, center_g_plus)
g_p_05 = phi_to_g(phi_p_05, center_g_minus, center_g_plus)
ax1.plot(g_m_05, g_p_05, 'o', markersize=14, markerfacecolor='none',
        markeredgecolor='yellow', markeredgewidth=3, zorder=5, label='α = +0.5')\

# Labels and title for subplot 1
ax1.set_xlabel('g₋ (Lower Equilibrium Concentration)', fontsize=12, fontweight='bold')
ax1.set_ylabel('g₊ (Upper Equilibrium Concentration)', fontsize=12, fontweight='bold')
ax1.set_title('Equilibrium Mapping Across α Values\nCentered on (4.2, 8.4)', 
             fontsize=13, fontweight='bold')

# Set limits and grid - rescale to fit all points
all_g_m = [phi_to_g(get_equilibria(a)[0], center_g_minus, center_g_plus) for a in alpha_values]
all_g_p = [phi_to_g(get_equilibria(a)[1], center_g_minus, center_g_plus) for a in alpha_values]
padding = 0.5
ax1.set_xlim(min(all_g_m) - padding, max(all_g_m) + padding)
ax1.set_ylim(min(all_g_p) - padding, max(all_g_p) + padding)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_aspect('equal')

# Colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax1, label='α Value', pad=0.15)

ax1.legend(loc='upper left', fontsize=10)

# ============================================================================
# Subplot 2: Free Energy f(φ)
# ============================================================================

# Define the free energy function
def free_energy(phi, alpha):
    """
    f(φ) = 1/12 * φ * (-4α(-3 + φ²) + 3φ(-2 + φ²))
    """
    return (1/12) * phi * (-4*alpha*(-3 + phi**2) + 3*phi*(-2 + phi**2))

# Create phi range
phi_range = np.linspace(-2, 2, 500)

# Plot free energy for different alpha values
alpha_plot_values = [-1.0, -0.5, 0.0, 0.5, 1.0]
colors_energy = plt.cm.RdYlBu(np.linspace(0, 1, len(alpha_plot_values)))

for i, alpha_val in enumerate(alpha_plot_values):
    f_vals = free_energy(phi_range, alpha_val)
    label = f'α = {alpha_val:+.1f}'
    if alpha_val == 0.5:
        ax2.plot(phi_range, f_vals, linewidth=3, color=colors_energy[i], label=label)
    else:
        ax2.plot(phi_range, f_vals, linewidth=2, color=colors_energy[i], label=label, alpha=0.8)

ax2.set_xlabel('φ', fontsize=12, fontweight='bold')
ax2.set_ylabel('f(φ)', fontsize=12, fontweight='bold')
ax2.set_title('Free Energy: $f(φ) = \\frac{1}{12}φ[-4α(-3+φ^2)+3φ(-2+φ^2)]$', 
             fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='best', fontsize=11)
ax2.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
ax2.axvline(x=0, color='k', linewidth=0.5, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/spinodal_point_plot/equilibrium_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# Print Summary
# ============================================================================

print("=" * 70)
print("EQUILIBRIUM MAPPING SUMMARY")
print("=" * 70)
print(f"Center point (α = 0): g₋ = {center_g_minus}, g₊ = {center_g_plus}")
print("-" * 70)
for alpha in [-0.5, -0.1, 0, 0.1, 0.5]:
    phi_m, phi_p = get_equilibria(alpha)
    g_m = phi_to_g(phi_m, center_g_minus, center_g_plus)
    g_p = phi_to_g(phi_p, center_g_minus, center_g_plus)
    highlight = " ← HIGHLIGHTED" if alpha == 0.5 else ""
    print(f"α = {alpha:+.1f}: φ₋ = {phi_m:7.4f}, φ₊ = {phi_p:7.4f} → g₋ = {g_m:6.2f}, g₊ = {g_p:6.2f}{highlight}")

print("\n" + "=" * 70)
print("FREE ENERGY EVALUATION AT KEY POINTS")
print("=" * 70)
for alpha_val in [-1.0, -0.5, 0.0, 0.5, 1.0]:
    f_at_0 = free_energy(0, alpha_val)
    f_at_1 = free_energy(1, alpha_val)
    f_at_neg1 = free_energy(-1, alpha_val)
    print(f"α = {alpha_val:+.1f}: f(-1) = {f_at_neg1:8.4f}, f(0) = {f_at_0:8.4f}, f(+1) = {f_at_1:8.4f}")