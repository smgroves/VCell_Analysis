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

def analyze_radius_trend(radius_data_file, actual_final_time):
    """Determine if radius is increasing or decreasing for multiple droplets"""
    try:
        data = pd.read_csv(radius_data_file)
        
        # Check if it's the new multi-droplet format (has 'droplet_id' column)
        if 'droplet_id' in data.columns:
            # Group by droplet_id
            droplet_groups = data.groupby('droplet_id')
            
            # Analyze each droplet
            droplet_results = []
            for droplet_id, group in droplet_groups:
                tt = group['time'].values[15:]  # Skip first 15 time points
                rr = group['radius'].values[15:]  # Skip first 15 radius points
                
                if len(rr) == 0:
                    continue

                final_radius, trend, slope, last_time = analyze_single_droplet(tt, rr, actual_final_time)
                droplet_results.append({
                    'droplet_id': droplet_id,
                    'final_radius': final_radius,
                    'trend': trend,
                    'slope': slope,
                    'last_time': last_time
                })
            
            # Return average final radius and most common trend
            if droplet_results:
                avg_final_radius = np.mean([d['final_radius'] for d in droplet_results 
                                           if not np.isnan(d['final_radius'])])
                # Count trends (excluding NaN)
                trends = [d['trend'] for d in droplet_results if d['trend'] is not np.nan]
                if trends:
                    most_common_trend = max(set(trends), key=trends.count)
                else:
                    most_common_trend = np.nan
                avg_slope = np.mean([d['slope'] for d in droplet_results 
                                    if not np.isnan(d['slope'])])
                # Get the maximum last_time (when the last droplet disappeared)
                max_last_time = max([d['last_time'] for d in droplet_results 
                                    if not np.isnan(d['last_time'])])
                return avg_final_radius, most_common_trend, avg_slope, max_last_time
            else:
                return np.nan, np.nan, np.nan, np.nan
        else:
            # Old format: single droplet (time, radius)
            data_array = data.values
            if data_array.size == 0:
                return np.nan, np.nan, np.nan, np.nan
            
            tt = data_array[15:, 0]  # Skip first 15 time points
            rr = data_array[15:, 1]  # Skip first 15 radius points
            
            return analyze_single_droplet(tt, rr, actual_final_time)
    
    except Exception as e:
        print(f"Error analyzing {radius_data_file}: {e}")
        return np.nan, np.nan, np.nan, np.nan

def analyze_single_droplet(tt, rr, actual_final_time, n_points=10):
    """Analyze trend for a single droplet"""
    if len(rr) == 0:
        return np.nan, np.nan, np.nan, np.nan

    # Find the last time at which the droplet existed (non-NaN radius)
    valid_idx = ~np.isnan(rr)
    if np.any(valid_idx):
        last_valid_idx = np.where(valid_idx)[0][-1]
        last_time = tt[last_valid_idx]
    else:
        last_time = np.nan
        return np.nan, np.nan, np.nan, last_time

    # If droplet disappeared before the end, return NaNs
    time_tolerance = (tt[1] - tt[0]) * 0.5
    if abs(last_time - actual_final_time) > time_tolerance:
        return np.nan, np.nan, np.nan, last_time

    # Droplet survived to the end
    final_radius = rr[-1]

    valid_tt = tt[valid_idx]
    valid_rr = rr[valid_idx]

    if len(valid_rr) < 2:
        return final_radius, np.nan, np.nan, last_time

    # Overall linear trend
    coeffs_all = np.polyfit(valid_tt, valid_rr, 1)
    slope_all = coeffs_all[0]

    # Classify initial trend
    if abs(slope_all) < 1e-4:
        trend = 'stable'
        slope = slope_all
    elif slope_all > 0:
        trend = 'increasing'
        slope = slope_all
    else:
        # Negative overall trend — check concavity of last n_points
        if len(valid_rr) >= n_points:
            last_tt = valid_tt[-n_points:]
            last_rr = valid_rr[-n_points:]

            if len(last_tt) >= 3:
                # Normalize time to improve polyfit conditioning
                t_mid = last_tt.mean()
                t_scale = last_tt.std() or 1.0
                last_tt_norm = (last_tt - t_mid) / t_scale

                coeffs_quad = np.polyfit(last_tt_norm, last_rr, 2)
                curvature = coeffs_quad[0]  # a in at^2 + bt + c

                if curvature > 0:
                    trend = 'concave_up'    # dissolution decelerating / recovering
                elif curvature < 0:
                    trend = 'concave_down'  # dissolution accelerating
                else:
                    trend = 'decreasing'
            else:
                trend = 'decreasing'

            slope = slope_all
        else:
            trend = 'decreasing'
            slope = slope_all

    return final_radius, trend, slope, last_time

def create_summary_table(intdir, output_csv, actual_final_time=None):
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
    if actual_final_time:
        print(f"Using actual final time: {actual_final_time}")
    
    # Initialize data structure
    data = []
    
    for radius_file in radius_files:
        # Extract prefix (remove 'radius_data.csv' from filename)
        basename = os.path.basename(radius_file)
        prefix = basename.replace("radius_data.csv", "")
        
        # Extract simulation info
        sim_info = extract_simulation_info(prefix)
        
        # Analyze radius data
        final_radius, trend, slope, last_time = analyze_radius_trend(radius_file, actual_final_time)
        
        # Calculate spinodal point
        spinodal_point = ((3-np.sqrt(3))/6)*(sim_info['max'] - sim_info['min']) + sim_info['min']
        
        # Add to data
        data.append({
            'prefix': prefix,
            'state': sim_info['state'],
            'max': sim_info['max'],
            'min': sim_info['min'],
            'final_radius': final_radius,
            'trend': trend,
            'slope': slope,
            'last_time': last_time,
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
    parser.add_argument('--actual-final-time', type=float, required=False, default=None,
                       help='Actual final time of simulation')
    
    args = parser.parse_args()
    
    create_summary_table(args.intdir, args.output, args.actual_final_time)

if __name__ == '__main__':
    main()