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
    phidims = size(phi);
    ny = phidims(2); % Number of columns = grid size
    n_frames = phidims(1) / ny; % Number of frames
    
    fprintf('Grid size: %d x %d\n', ny, ny);
    fprintf('Number of frames: %d\n', n_frames);
    
    % Reshape to 3D array: [ny, ny, n_frames]
    phi = reshape(phi, ny, n_frames, ny);
    phi = shiftdim(phi, 2); % Shift to [ny, ny, n_frames]
    
    % Initialize arrays
    tt = zeros(1, n_frames);
    rr = zeros(1, n_frames);
    
    % Create coordinate grid
    h = 1/ny;
    x = h*(0:ny-1);
    y = h*(0:ny-1);
    
    fprintf('Processing %d frames...\n', n_frames);
    
    for i = 1:n_frames
        % Calculate time
        tt(i) = (i-1) * dt_out * dt;
        
        % Extract frame
        phi_tmp = phi(:,:,i);
        
        try
            % Find and plot the 0 contour
            figure('visible', 'off');
            [~, h_contour] = contour(x, y, phi_tmp, [0 0]);
            
            % Extract the x and y coordinates of the 0 contour
            contour_data = h_contour.ContourMatrix;
            col = 1;
            x_contour = [];
            y_contour = [];
            
            while col < size(contour_data, 2)
                num_points = contour_data(2, col);
                cols = col + (1:num_points);
                
                x_contour = [x_contour, contour_data(1, cols)];
                y_contour = [y_contour, contour_data(2, cols)];
                
                col = col + num_points + 1;  % Move to next segment
            end
            
            close;
            
            if isempty(x_contour)
                rr(i) = NaN;
                warning('No contour found for frame %d', i);
                continue;
            end
            
            % Calculate center (necessary when droplet isn't centered)
            x_center = mean(x_contour);
            y_center = mean(y_contour);
            
            % Calculate radius
            distances = sqrt((x_contour - x_center).^2 + (y_contour - y_center).^2);
            rr(i) = mean(distances);
            
        catch ME
            warning('Error processing frame %d: %s', i, ME.message);
            rr(i) = NaN;
            close all;
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
