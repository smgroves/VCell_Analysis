function calculate_level_set_radius(phi_file, dt, dt_out, output_file)
    % Calculate radius at level 0 contour for all timesteps in phi file
    % Tracks multiple droplets across time
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
    
    % Initialize tracking structure
    dropletData = cell(n_frames, 1);
    trackedDroplets = {};
    contour_level = 0;
    threshold = 10; % Distance threshold for matching droplets
    
    % Create coordinate grid
    h = 1/ny;
    x = h*(0:ny-1);
    y = h*(0:ny-1);
    
    fprintf('Processing %d frames and tracking multiple droplets...\n', n_frames);
    
    % Loop over each time point
    for t = 1:n_frames
        currentData = phi(:,:,t);
        
        try
            % Find the 0-level contour
            fig = figure('visible', 'off');
            contourMatrix = contourc(x, y, currentData, [contour_level, contour_level]);
            close(fig);
            
            % Initialize list to store droplets for current time point
            droplets = [];
            startIdx = 1;
            
            % Parse the contour matrix
            while startIdx < size(contourMatrix, 2)
                numPoints = contourMatrix(2, startIdx);
                if numPoints > 0
                    dropletContour = contourMatrix(:, startIdx+1:startIdx+numPoints);
                    
                    % Calculate center and radius
                    centerX = mean(dropletContour(1, :));
                    centerY = mean(dropletContour(2, :));
                    distances = sqrt((dropletContour(1, :) - centerX).^2 + ...
                                   (dropletContour(2, :) - centerY).^2);
                    radius = mean(distances);
                    
                    % Store droplet information
                    droplet.center = [centerX, centerY];
                    droplet.radius = radius;
                    droplet.id = 0;
                    droplets = [droplets, droplet];
                end
                
                % Move to next contour
                startIdx = startIdx + numPoints + 1;
            end
            
            % Store droplet data for current time point
            dropletData{t} = droplets;
            
            % Track droplets across time points
            if t == 1
                % Initialize tracked droplets with first time point
                for i = 1:length(droplets)
                    trackedDroplets{i}.radius = droplets(i).radius;
                    trackedDroplets{i}.time = (t-1) * dt_out * dt;
                    trackedDroplets{i}.center = droplets(i).center;
                    trackedDroplets{i}.id = i;
                    dropletData{t}(i).id = i;
                end
            else
                % Match droplets to previous time point
                if ~isempty(dropletData{t-1})
                    previousDroplets = dropletData{t-1};
                    
                    for i = 1:length(droplets)
                        currentCenter = droplets(i).center;
                        
                        % Calculate distances to all previous droplets
                        distances_to_prev = zeros(1, length(previousDroplets));
                        for j = 1:length(previousDroplets)
                            distances_to_prev(j) = norm(previousDroplets(j).center - currentCenter);
                        end
                        
                        [minDist, minIdx] = min(distances_to_prev);
                        match_id = previousDroplets(minIdx).id;
                        
                        % Check if same droplet based on threshold
                        if minDist < threshold
                            % Match found, update tracked droplet
                            trackedDroplets{match_id}.radius = ...
                                [trackedDroplets{match_id}.radius, droplets(i).radius];
                            trackedDroplets{match_id}.time = ...
                                [trackedDroplets{match_id}.time, (t-1) * dt_out * dt];
                            dropletData{t}(i).id = match_id;
                        else
                            % New droplet, add to tracked droplets
                            newIdx = length(trackedDroplets) + 1;
                            trackedDroplets{newIdx}.radius = droplets(i).radius;
                            trackedDroplets{newIdx}.time = (t-1) * dt_out * dt;
                            trackedDroplets{newIdx}.center = droplets(i).center;
                            trackedDroplets{newIdx}.id = newIdx;
                            dropletData{t}(i).id = newIdx;
                        end
                    end
                end
            end
            
        catch ME
            warning('Error processing frame %d: %s', t, ME.message);
        end
        
        if mod(t, 10) == 0
            fprintf('Processed %d/%d frames\n', t, n_frames);
        end
    end
    
    % Save results for each tracked droplet
    % Format: one CSV with columns: droplet_id, time, radius
    results = [];
    for i = 1:length(trackedDroplets)
        if ~isempty(trackedDroplets{i})
            num_points = length(trackedDroplets{i}.time);
            droplet_ids = repmat(i, num_points, 1);
            times = trackedDroplets{i}.time(:);
            radii = trackedDroplets{i}.radius(:);
            results = [results; droplet_ids, times, radii];
        end
    end
    
    % Sort by time, then droplet_id
    if ~isempty(results)
        results = sortrows(results, [2, 1]);
        
        % Save to file with header
        fid = fopen(output_file, 'w');
        fprintf(fid, 'droplet_id,time,radius\n');
        fclose(fid);
        writematrix(results, output_file, 'WriteMode', 'append');
        
        fprintf('Radius data saved to %s\n', output_file);
        fprintf('Found %d droplets total\n', length(trackedDroplets));
    else
        warning('No droplets found in any frame');
        % Save empty file with header
        fid = fopen(output_file, 'w');
        fprintf(fid, 'droplet_id,time,radius\n');
        fclose(fid);
    end
end