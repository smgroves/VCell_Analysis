%% 
indir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/IC/11_25_2025";
outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/5_vcell_to_ch/output/11_25_2025";

n_relax = 4;
%h = 1/GridSize;
% m = 8
% epsilon = m * h/ (2 * sqrt(2) * atanh(0.9));
epsilon = 0.0089; %10A
% epsilon = 0.0067; %HeLa
epsilon2 = epsilon^2;

dt = 2.5e-5;
max_it = 2000;
boundary = 'neumann';
myFiles = dir(fullfile(indir,'*15max_*min.csv')); %gets all csv files in struct
% print("Found %d files to process\n", length(myFiles));
for k = 1:length(myFiles)
    baseFileName = myFiles(k).name;
    folder_name = regexp(baseFileName, '^(.*?)(?=\d+x\d+)', 'tokens', 'once');
    prefix = folder_name{1};
    pathname = sprintf("%s/%s/%s", outdir, prefix, baseFileName(1:end-4));
    output_movie_file = fullfile(sprintf("%smovie.mp4", pathname));
    % Check if output file already exists
    if exist(output_movie_file, 'file')
        fprintf('Skipping %s (already processed)\n', baseFileName);
        continue;
    end

    fprintf("Processing file %s (%d of %d)\n", baseFileName, k, length(myFiles));

    init_file = sprintf("%s/%s",indir,baseFileName);
    phi0 = readmatrix(init_file);
    print_phi = true;
    dt_out = 10;
    ny = size(phi0,2);
    % % #################################################
    % % RUN SAV SOLVER 
    % % #################################################

    if ~exist(sprintf("%s/%s", outdir, prefix), 'dir')
        mkdir(sprintf("%s/%s", outdir, prefix));
    end
    fprintf("Running SAV solver with parameters: %s\n", pathname);
    tStart_NMG = tic;
    [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0,...
                                        t_iter = max_it,...
                                        dt = dt,...
                                        epsilon2= epsilon2,...
                                        boundary = boundary,...
                                        printphi=print_phi,...
                                        pathname=pathname,...
                                        dt_out = dt_out);
    elapsedTime = toc(tStart_NMG);

    writematrix(phi_t(:,:,end),sprintf('%sfinal_phi.csv', pathname));
    writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
    writematrix(E_t,sprintf('%senergy.csv', pathname));
    filename = strcat(pathname, "movie");
    fprintf("Creating movie\n");
    ch_movie_from_file_fast(strcat(pathname,"phi.csv"), t_out, ny,filename = filename, dtframes = 1)

end
