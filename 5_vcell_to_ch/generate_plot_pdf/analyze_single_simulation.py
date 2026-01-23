import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

def create_redblue_colormap():
    """Create red-white-blue colormap matching MATLAB's redbluecmap"""
    colors = [
        (0.0, 0.0, 1.0),   # Blue
        (1.0, 1.0, 1.0),   # White
        (1.0, 0.0, 0.0)    # Red
    ]
    n_bins = 1000
    cmap = LinearSegmentedColormap.from_list('redblue', colors, N=n_bins)
    return cmap

def plot_phi_snapshot(phi_file, title):
    """Create phi snapshot with red-blue colormap"""
    phi = np.loadtxt(phi_file, delimiter=',')
    
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = create_redblue_colormap()
    
    im = ax.imshow(phi, cmap=cmap, vmin=-1, vmax=1, origin='lower', 
                   extent=[0, 1, 0, 1], aspect='equal')
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('φ', rotation=0, fontsize=12)
    
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    return fig

def get_initial_phi(phi_file, ny):
    """Extract initial phi from the phi.csv file"""
    phi_all = np.loadtxt(phi_file, delimiter=',')
    # First ny rows are the initial state
    phi_initial = phi_all[:ny, :]
    return phi_initial

def get_final_phi(phi_file, ny):
    """Extract final phi from the phi.csv file"""
    phi_all = np.loadtxt(phi_file, delimiter=',')
    # Last ny rows are the final state
    phi_final = phi_all[-ny:, :]
    return phi_final

def plot_radius_evolution(radius_data_file, sim_name):
    """Create radius vs time plot"""
    data = np.loadtxt(radius_data_file, delimiter=',')
    tt = data[:, 0]
    rr = data[:, 1]
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    ax.plot(tt, rr, 'b-', linewidth=2)
    ax.set_xlabel('Time (t)', fontsize=12)
    ax.set_ylabel('Radius (R)', fontsize=12)
    ax.set_title('Droplet Radius at Level 0', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    return fig

def main():
    parser = argparse.ArgumentParser(description='Analyze single CH simulation')
    parser.add_argument('--final-phi', required=True, help='Path to final_phi.csv')
    parser.add_argument('--phi', required=True, help='Path to phi.csv')
    parser.add_argument('--radius-data', required=True, help='Path to radius_data.csv')
    parser.add_argument('--dt', type=float, required=True, help='Timestep size')
    parser.add_argument('--dt-out', type=float, required=True, help='Output interval')
    parser.add_argument('--sim-name', required=True, help='Simulation name/prefix')
    parser.add_argument('--output', required=True, help='Output .npz file')
    
    args = parser.parse_args()
    
    # Use provided simulation name
    sim_name = args.sim_name
    
    # Determine grid size from final_phi file
    phi_sample = np.loadtxt(args.final_phi, delimiter=',')
    ny = phi_sample.shape[0]
    
    # Get initial and final phi from phi.csv
    phi_initial = get_initial_phi(args.phi, ny)
    phi_final = get_final_phi(args.phi, ny)
    
    # Save to temporary files for plotting
    initial_phi_temp = args.output.replace('.npz', '_initial_temp.csv')
    final_phi_temp = args.output.replace('.npz', '_final_temp.csv')
    np.savetxt(initial_phi_temp, phi_initial, delimiter=',')
    np.savetxt(final_phi_temp, phi_final, delimiter=',')
    
    # Create plots
    fig1 = plot_phi_snapshot(initial_phi_temp, 'Initial State')
    fig2 = plot_phi_snapshot(final_phi_temp, 'Final State')
    fig3 = plot_radius_evolution(args.radius_data, sim_name)
    
    # Save figures as temporary files
    fig1.savefig(args.output.replace('.npz', '_initial.png'), 
                 dpi=150, bbox_inches='tight')
    fig2.savefig(args.output.replace('.npz', '_final.png'), 
                 dpi=150, bbox_inches='tight')
    fig3.savefig(args.output.replace('.npz', '_radius.png'), 
                 dpi=150, bbox_inches='tight')
    
    # Clean up temp files
    if os.path.exists(initial_phi_temp):
        os.remove(initial_phi_temp)
    if os.path.exists(final_phi_temp):
        os.remove(final_phi_temp)
    
    # Save metadata
    np.savez(args.output, 
             sim_name=sim_name,
             initial_plot=args.output.replace('.npz', '_initial.png'),
             final_plot=args.output.replace('.npz', '_final.png'),
             radius_plot=args.output.replace('.npz', '_radius.png'))
    
    plt.close('all')
    print(f"Analysis complete for {sim_name}")

if __name__ == '__main__':
    main()