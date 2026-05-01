function ch_movie_from_file_fast(phi_file,t_out,ny,varargin)
% Fast + MATLAB R2025b-safe version

%% Parse inputs
default_dtframes = 10;
default_filename = 'ch_movie';
default_filetype = 'MPEG-4';
default_colorbar = 'default';

p = inputParser;
addRequired(p,'phi_file');
addRequired(p,'t_out');
addRequired(p,'ny');
addParameter(p,'dtframes',default_dtframes);
addParameter(p,'filename',default_filename);
addParameter(p,'filetype',default_filetype);
addParameter(p,'colorbar_type',default_colorbar);
parse(p,phi_file,t_out,ny,varargin{:});

dtframes     = p.Results.dtframes;
filename     = p.Results.filename;
filetype     = p.Results.filetype;
colorbarType = p.Results.colorbar_type;

%% Read entire file at once (much faster)
phi = readmatrix(phi_file);
nx = size(phi,2);                % number of x grid points
nt = numel(t_out);
phi = reshape(phi.', nx, ny, []); % reshape into (nx,ny,t)

%% Prepare video
v = VideoWriter(filename,filetype);
if strcmpi(filetype,'MPEG-4') || strcmpi(filetype,'Motion JPEG AVI')
    v.Quality = 100;
end
open(v);

%% Prepare figure once
fig = figure('visible','off');
set(fig,'Renderer','opengl');   % Stable in MATLAB 2025b

ax = axes(fig);
imgHandle = imagesc(phi(:,:,1), 'Parent', ax);
axis(ax,'square');
colormap(interp1(1:100:1100,redbluecmap,1:1001)); %Expand redbluecmap to 1000 elements

% colormap(ax, redbluecmap(1000));
colorbar(ax);

% Fix color limits
switch colorbarType
    case "default"
        clim(ax, [-1 1]);
    case "initial_range"
        initial_min = min(phi(:,:,1),[],'all');
        initial_max = max(phi(:,:,1),[],'all');
        clim(ax,[initial_min initial_max]);
    case "variable"
        % do nothing — will adjust each frame
end

title(ax, sprintf('t = %g', t_out(1)));

%% Movie loop (FAST)
for i = 1:dtframes:nt
    frameData = transpose(phi(:,:,i));

    % Update image without recreating anything
    set(imgHandle, 'CData', frameData);

    if colorbarType == "variable"
        clim(ax, [min(frameData,[],'all') max(frameData,[],'all')]);
    end

    title(ax, sprintf('t = %g', t_out(i)));

    % Capture frame safely in 2025b
    frame = getframe(fig);
    writeVideo(v, frame);

    if mod(i, floor(nt/20)) == 0
        fprintf("%3.0f%% complete\n", i/nt*100);
    end
end

close(v);
end
