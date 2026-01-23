function calculate_level_set_radius(phi_file, dt, dt_out, output_file)
    % Calculate radius at level 0 contour for all timesteps in phi file
    %
    % INPUTS:
    %   phi_file - path to phi.csv file
    %   dt - timestep size
    %   dt_out - output interval
    %   output_file - path to save radius_data.csv
    
    % Read the phi data
    phi = readmatrix(phi_file);
    
    % Determine dimensions
    ny = sqrt(size(phi, 2)); % Assuming square grid
    n_frames = size(phi, 1) / ny;
    
    % Initialize arrays
    tt = zeros(1, n_frames);
    rr = zeros(1, n_frames);
    
    % Create coordinate grid
    h = 1/ny;
    x = h*(0:ny-1);
    y = h*(0:ny-1);
    
    fprintf('Processing %d frames...\n', n_frames);
    
    for i = 1:n_frames
        % Extract frame
        row_start = (i-1)*ny + 1;
        row_end = i*ny;
        phi_frame = phi(row_start:row_end, :);
        
        % Calculate time
        tt(i) = (i-1) * dt_out * dt;
        
        try
            % Find and extract the 0 contour
            [C, ~] = contour(x, y, phi_frame, [0 0]);
            
            % Extract contour coordinates
            col = 1;
            x_contour = [];
            y_contour = [];
            
            while col < size(C, 2)
                num_points = C(2, col);
                cols = col + (1:num_points);
                
                x_contour = [x_contour, C(1, cols)];
                y_contour = [y_contour, C(2, cols)];
                
                col = col + num_points + 1;
            end
            
            if isempty(x_contour)
                rr(i) = NaN;
                warning('No contour found for frame %d', i);
                continue;
            end
            
            % Calculate center and radius
            x_center = mean(x_contour);
            y_center = mean(y_contour);
            
            distances = sqrt((x_contour - x_center).^2 + (y_contour - y_center).^2);
            rr(i) = mean(distances);
            
        catch ME
            warning('Error processing frame %d: %s', i, ME.message);
            rr(i) = NaN;
        end
        
        if mod(i, 10) == 0
            fprintf('Processed %d/%d frames\n', i, n_frames);
        end
    end
    
    % Save results
    results = [tt; rr]';
    writematrix(results, output_file);
    fprintf('Radius data saved to %s\n', output_file);
end
