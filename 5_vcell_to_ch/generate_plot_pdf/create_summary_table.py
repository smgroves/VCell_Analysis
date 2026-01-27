import argparse
import os
import glob
import re
import numpy as np
import pandas as pd

def extract_simulation_info(prefix):
    """Extract relaxed/tensed, max, and min values from simulation prefix"""
    info = {
        'state': None,
        'max': None,
        'min': None
    }
    
    # Extract relaxed or tensed
    if 'relaxed' in prefix.lower():
        info['state'] = 'relaxed'
    elif 'tensed' in prefix.lower():
        info['state'] = 'tensed'
    
    # Extract number before 'max' (e.g., "10max" -> 10)
    max_match = re.search(r'(\d+\.?\d*)max', prefix)
    if max_match:
        info['max'] = float(max_match.group(1))
    
    # Extract number before 'min' (e.g., "4.25min" -> 4.25)
    min_match = re.search(r'(\d+\.?\d*)min', prefix)
    if min_match:
        info['min'] = float(min_match.group(1))
    
    return info

def analyze_radius_trend(radius_data_file):
    """Determine if radius is increasing or decreasing"""
    try:
        data = np.loadtxt(radius_data_file, delimiter=',')
        if data.size == 0:
            return np.nan, np.nan
        
        tt = data[:, 0]
        rr = data[:, 1]
        
        # Get final radius (even if NaN)
        final_radius = rr[-1]
        
        # If final radius is NaN, trend is also NaN
        if np.isnan(final_radius):
            return final_radius, np.nan
        
        # For trend calculation, only use non-NaN values
        valid_idx = ~np.isnan(rr)
        if not np.any(valid_idx) or np.sum(valid_idx) < 2:
            return final_radius, np.nan
        
        rr_valid = rr[valid_idx]
        tt_valid = tt[valid_idx]
        
        # Determine trend using linear regression on valid points
        if len(rr_valid) > 1:
            # Fit linear trend
            coeffs = np.polyfit(tt_valid, rr_valid, 1)
            slope = coeffs[0]
            
            # Classify trend based on slope
            if abs(slope) < 1e-6:  # Essentially flat
                trend = 'stable'
            elif slope > 0:
                trend = 'increasing'
            else:
                trend = 'decreasing'
        else:
            trend = np.nan
        
        return final_radius, trend
    
    except Exception as e:
        print(f"Error analyzing {radius_data_file}: {e}")
        return np.nan, np.nan

def create_summary_table(intdir, output_csv):
    """Create summary table from all radius_data files"""
    
    # Find all radius_data.csv files recursively
    radius_files = []
    for root, dirs, files in os.walk(intdir):
        for file in files:
            if file.endswith("radius_data.csv"):
                radius_files.append(os.path.join(root, file))
    
    if not radius_files:
        print(f"No radius_data.csv files found in {intdir}")
        return
    
    print(f"Found {len(radius_files)} radius data files")
    
    # Initialize data structure
    data = []
    
    for radius_file in radius_files:
        # Extract prefix (remove 'radius_data.csv' from filename)
        basename = os.path.basename(radius_file)
        prefix = basename.replace("radius_data.csv", "")
        
        # Extract simulation info
        sim_info = extract_simulation_info(prefix)
        
        # Analyze radius data
        final_radius, trend = analyze_radius_trend(radius_file)
        
        # calculate spinodal point
        spinodal_point = ((3-np.sqrt(3))/6)*(sim_info['max'] - sim_info['min']) + sim_info['min']

        # Add to data
        data.append({
            'prefix': prefix,
            'state': sim_info['state'],
            'max': sim_info['max'],
            'min': sim_info['min'],
            'final_radius': final_radius,
            'trend': trend,
            'spinodal_point': spinodal_point
        })
        
        print(f"Processed: {prefix[:50]}...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df = df.set_index('prefix')
    
    # Sort by state, max, min
    df = df.sort_values(['state', 'max', 'min'], na_position='last')
    
    # Save to CSV
    df.to_csv(output_csv)
    print(f"\nSummary table saved to: {output_csv}")
    print(f"\nPreview:")
    print(df.head(10))
    print(f"\nTotal simulations: {len(df)}")
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Create summary table from simulation results')
    parser.add_argument('--intdir', required=True, help='Path to int directory')
    parser.add_argument('--output', required=True, help='Output CSV filename')
    
    args = parser.parse_args()
    
    create_summary_table(args.intdir, args.output)

if __name__ == '__main__':
    main()