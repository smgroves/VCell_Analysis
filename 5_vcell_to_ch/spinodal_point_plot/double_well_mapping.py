# %%
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# Define energy functions
# ============================================================================


def original_energy(phi):
    """
    Original energy (symmetric double well)
    ψ(φ) = 1/12 φ(-4(-3+φ²) + 3φ(-2+φ²))
           = 1/12 φ(12 - 4φ² - 6φ² + 3φ⁴)
           = 1/12 φ(12 - 10φ² + 3φ⁴)
    """
    return (1/12) * phi * (12 - 10*phi**2 + 3*phi**4)


def energy_with_alpha(phi, alpha):
    """
    Modified energy with asymmetry parameter α
    ψ(φ, α) = 1/12 φ(-4α(-3+φ²) + 3φ(-2+φ²))
    """
    return (1/12) * phi * (-4*alpha*(-3 + phi**2) + 3*phi*(-2 + phi**2))


def tangent_line(phi, phi_1, phi_2, psi_1, psi_2):
    """
    Common tangent line between two points
    """
    slope = (psi_2 - psi_1) / (phi_2 - phi_1)
    return psi_1 + slope * (phi - phi_1)


def modified_energy_with_A(phi, alpha, A, B):
    """
    Modified energy with linear shift
    ψ₂(φ) = ψ(φ, α) - A*φ - B
    """
    return energy_with_alpha(phi, alpha) - A*phi - B

# ============================================================================
# Create figure with multiple subplots
# ============================================================================

# %%


fig = plt.figure(figsize=(20, 10))

# Define alpha values and their properties
# A is calculated as the slope of the common tangent: (psi_p - psi_m) / (phi_p - phi_m)
alpha_cases = [
    {'alpha': -1.0, 'phi_m': -1.4150, 'phi_p': 0.7484},
    {'alpha': -0.5, 'phi_m': -1.2075, 'phi_p': 0.8742},
    {'alpha': 0.0, 'phi_m': -1.0, 'phi_p': 1.0},
    {'alpha': 0.5, 'phi_m': -0.8742, 'phi_p': 1.2075},
    {'alpha': 1.0, 'phi_m': -0.7484, 'phi_p': 1.4150},
]

phi_range = np.linspace(-2, 2, 500)

# Plot for each alpha case
for idx, case in enumerate(alpha_cases):
    alpha = case['alpha']
    phi_m = case['phi_m']
    phi_p = case['phi_p']

    # ====================================================================
    # Subplot 1: Modified Energy with Alpha + Common Tangent
    # ====================================================================
    ax1 = plt.subplot(2, 5, idx + 1)

    psi_alpha = energy_with_alpha(phi_range, alpha)
    ax1.plot(phi_range, psi_alpha, 'b-', linewidth=2.5,
             label=f'ψ(φ, α={alpha:+.1f})')

    # Plot the equilibrium points
    psi_m = energy_with_alpha(phi_m, alpha)
    psi_p = energy_with_alpha(phi_p, alpha)
    ax1.plot([phi_m, phi_p], [psi_m, psi_p], 'ro',
             markersize=8, zorder=3, label='Equilibria')

    # Plot the common tangent line and calculate A as its slope
    tangent = tangent_line(phi_range, phi_m, phi_p, psi_m, psi_p)
    A = (psi_p - psi_m) / (phi_p - phi_m)
    ax1.plot(phi_range, tangent, 'r--', linewidth=2,
             alpha=0.7, label='Common tangent')

    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
    ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
    ax1.set_ylabel('Energy', fontsize=11, fontweight='bold')
    ax1.set_title(f'α = {alpha:+.1f}\n(Common Tangent)',
                  fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.2)
    ax1.set_xlim(-2, 2)
    ax1.legend(loc='upper center', fontsize=9)

    # ====================================================================
    # Subplot 2: Modified Energy with A Parameter
    # ====================================================================
    ax2 = plt.subplot(2, 5, idx + 6)

    # Calculate B such that the modified energy equals the tangent at both equilibria
    B = psi_m - A * phi_m

    psi_2 = modified_energy_with_A(phi_range, alpha, A, B)
    ax2.plot(phi_range, psi_2, 'g-', linewidth=2.5, label=f'ψ₂(φ)')

    # Plot equilibrium points (should be at minima now)
    psi_2_m = modified_energy_with_A(phi_m, alpha, A, B)
    psi_2_p = modified_energy_with_A(phi_p, alpha, A, B)
    ax2.plot([phi_m, phi_p], [psi_2_m, psi_2_p], 'ro',
             markersize=8, zorder=3, label='Equilibria')

    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
    ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.3, linewidth=0.8)
    ax2.set_xlabel('φ', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Energy', fontsize=11, fontweight='bold')
    ax2.set_title(f'α = {alpha:+.1f}\n(With A Parameter)',
                  fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.2)
    ax2.set_xlim(-2, 2)
    ax2.legend(loc='upper center', fontsize=9)

    # Print summary
    print(f"\n{'='*70}")
    print(f"α = {alpha:+.1f}")
    print(f"{'='*70}")
    print(f"Equilibrium points: φ₋ = {phi_m:7.4f}, φ₊ = {phi_p:7.4f}")
    print(f"A parameter: {A:+.4f}, B parameter: {B:+.4f}")
    print(
        f"Energy with α at equilibria: ψ({phi_m:.4f}) = {psi_m:.6f}, ψ({phi_p:.4f}) = {psi_p:.6f}")
    print(
        f"Modified energy ψ₂ at equilibria: ψ₂({phi_m:.4f}) = {psi_2_m:.6f}, ψ₂({phi_p:.4f}) = {psi_2_p:.6f}")
    print(f"Common tangent slope: {(psi_p - psi_m) / (phi_p - phi_m):.4f}")

plt.tight_layout()
plt.savefig('/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/spinodal_point_plot/energy_progression.png',
            dpi=300, bbox_inches='tight')
plt.show()

print(f"\n{'='*70}")
print("Energy Progression Summary")
print(f"{'='*70}")
print("Row 1: Modified energy with α showing common tangent construction")
print("Row 2: Final modified energy ψ₂(φ) = ψ(φ,α) - Aφ - B")
print("The linear shift (Aφ + B) flattens the energy between equilibria")
print(f"{'='*70}")

# %%
