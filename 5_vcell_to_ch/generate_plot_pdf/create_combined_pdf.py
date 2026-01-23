import argparse
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

def create_combined_pdf(outdir, output_pdf):
    """Create single PDF with all simulation analyses"""
    
    # Find all analysis_plots.npz files both in outdir and subdirectories
    npz_files = []
    
    # Search in the main directory
    npz_files.extend(glob.glob(os.path.join(outdir, "*analysis_plots.npz")))
    
    # Search in all subdirectories
    for root, dirs, files in os.walk(outdir):
        for file in files:
            if file.endswith("analysis_plots.npz"):
                full_path = os.path.join(root, file)
                # Avoid duplicates (in case we already found it in main dir)
                if full_path not in npz_files:
                    npz_files.append(full_path)
    
    if not npz_files:
        print(f"No analysis files found in {outdir} or its subdirectories!")
        print("Looking for files matching: *analysis_plots.npz")
        return
    
    # Sort by simulation name for consistent ordering
    npz_files.sort()
    
    print(f"Found {len(npz_files)} simulations to combine")
    
    with PdfPages(output_pdf) as pdf:
        for i, npz_path in enumerate(npz_files):
            # Load metadata
            data = np.load(npz_path, allow_pickle=True)
            sim_name = str(data['sim_name'])
            initial_plot_path = str(data['initial_plot'])
            final_plot_path = str(data['final_plot'])
            radius_plot_path = str(data['radius_plot'])
            
            print(f"Processing {i+1}/{len(npz_files)}: {sim_name}")
            
            # Create figure with 3 subplots in a row
            fig = plt.figure(figsize=(18, 5))
            
            # Add simulation name as suptitle
            fig.suptitle(sim_name, fontsize=16, fontweight='bold', y=0.98)
            
            # Load and display initial phi plot
            ax1 = fig.add_subplot(1, 3, 1)
            if os.path.exists(initial_plot_path):
                img1 = Image.open(initial_plot_path)
                ax1.imshow(img1)
                ax1.axis('off')
            else:
                ax1.text(0.5, 0.5, 'Initial phi plot not found', 
                        ha='center', va='center')
                ax1.axis('off')
            
            # Load and display final phi plot
            ax2 = fig.add_subplot(1, 3, 2)
            if os.path.exists(final_plot_path):
                img2 = Image.open(final_plot_path)
                ax2.imshow(img2)
                ax2.axis('off')
            else:
                ax2.text(0.5, 0.5, 'Final phi plot not found', 
                        ha='center', va='center')
                ax2.axis('off')
            
            # Load and display radius plot
            ax3 = fig.add_subplot(1, 3, 3)
            if os.path.exists(radius_plot_path):
                img3 = Image.open(radius_plot_path)
                ax3.imshow(img3)
                ax3.axis('off')
            else:
                ax3.text(0.5, 0.5, 'Radius plot not found', 
                        ha='center', va='center')
                ax3.axis('off')
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            pdf.savefig(fig, dpi=150)
            plt.close(fig)
    
    print(f"\nCombined PDF saved to: {output_pdf}")
    print(f"Total pages: {len(npz_files)}")

def main():
    parser = argparse.ArgumentParser(description='Combine all simulation plots into single PDF')
    parser.add_argument('--outdir', required=True, help='Output directory containing simulations')
    parser.add_argument('--output', required=True, help='Output PDF filename')
    
    args = parser.parse_args()
    
    create_combined_pdf(args.outdir, args.output)

if __name__ == '__main__':
    main()