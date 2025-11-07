indir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC";
outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/output";

n_relax = 4;
GridSize = 256;
%h = 1/GridSize;
%epsilon = m * h/ (2 * sqrt(2) * atanh(0.9));
epsilon = 0.0089; %10A
epsilon2 = epsilon^2;
%epsilon = 0.0067; %HeLa
%D = GridSize^2;
dt = 2.5e-5;
max_it = 2000;
boundary = 'neumann';
init_file = sprintf("%s/_09_16_25_CPC_metacentric_relaxed_model_09_16_25_metacentric_relaxed_model_120_256x256_5max.csv",indir);
phi0 = readmatrix(init_file);
print_phi = true;
dt_out = 1;
ny = GridSize;

% % #################################################
% % RUN NMG SOLVER 
% % #################################################

pathname = sprintf("%s/_09_16_25_CPC_metacentric_relaxed_model_09_16_25_metacentric_relaxed_model_120_256x256_5max", outdir);
fprintf("Running NMG solver with parameters: %s\n", pathname);
tStart_NMG = tic;
[t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_NMG(phi0,...
                                    t_iter = max_it,...
                                    dt = dt,...
                                    epsilon2= epsilon2,...
                                    boundary = boundary,...
                                    printphi=print_phi,...
                                    pathname=pathname,...
                                    dt_out = dt_out,...
                                    tol = 1e-6);
elapsedTime = toc(tStart_NMG);

% writematrix(phi_t(:,:,end),sprintf('%sfinal_phi.csv', pathname));
writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
writematrix(E_t,sprintf('%senergy.csv', pathname));
filename = strcat(pathname, "movie");
fprintf("Creating movie\n");
if print_phi
    ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename)
else
    ch_movie(phi_t,t_out, filename = filename);
end

