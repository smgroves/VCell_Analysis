indir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/IC";
outdir = "/Users/smgroves/Documents/GitHub/VCell_Analysis/4_vcell_to_ch/output";

n_relax = 4;
%h = 1/GridSize;
% m = 8
% epsilon = m * h/ (2 * sqrt(2) * atanh(0.9));
% epsilon = 0.0089; %10A
epsilon = 0.0067; %HeLa
epsilon2 = epsilon^2;

dt = 2.5e-5;
max_it = 3000;
boundary = 'neumann';
init_file = sprintf("%s/_09_16_25_CPC_metacentric_relaxed_model_09_16_25_metacentric_relaxed_model_120_128x128__20max.csv",indir);
% "10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_256x256_5max.csv"
% "09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_256x256_5max.csv"
phi0 = readmatrix(init_file);
print_phi = true;
dt_out = 10;
ny = 128;
% % #################################################
% % RUN NMG SOLVER 
% % #################################################

pathname = sprintf("%s/_09_16_25_CPC_metacentric_relaxed_model_09_16_25_metacentric_relaxed_model_120_128x128__20max", outdir);
fprintf("Running NMG solver with parameters: %s\n", pathname);
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

% writematrix(phi_t(:,:,end),sprintf('%sfinal_phi.csv', pathname));
writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
writematrix(E_t,sprintf('%senergy.csv', pathname));
filename = strcat(pathname, "movie");
fprintf("Creating movie\n");
if print_phi
    ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename, dtframes = 1)
else
    ch_movie(phi_t,t_out, filename = filename);
end


% init_file = sprintf("%s/10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_128x128__20max.csv",indir);
% % "10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_256x256_5max.csv"
% % "09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_256x256_5max.csv"
% phi0 = readmatrix(init_file);
% pathname = sprintf("%s/10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_128x128__20max", outdir);
% fprintf("Running NMG solver with parameters: %s\n", pathname);
% [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0,...
%                                     t_iter = max_it,...
%                                     dt = dt,...
%                                     epsilon2= epsilon2,...
%                                     boundary = boundary,...
%                                     printphi=print_phi,...
%                                     pathname=pathname,...
%                                     dt_out = dt_out);
% writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
% writematrix(E_t,sprintf('%senergy.csv', pathname));
% filename = strcat(pathname, "movie");
% fprintf("Creating movie\n");
% ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename, dtframes = 1)

% init_file = sprintf("%s/10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_14_128x128__20max.csv",indir);
% % "10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_256x256_5max.csv"
% % "09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_256x256_5max.csv"
% phi0 = readmatrix(init_file);
% pathname = sprintf("%s/10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_14_128x128__20max", outdir);
% fprintf("Running NMG solver with parameters: %s\n", pathname);
% [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0,...
%                                     t_iter = max_it,...
%                                     dt = dt,...
%                                     epsilon2= epsilon2,...
%                                     boundary = boundary,...
%                                     printphi=print_phi,...
%                                     pathname=pathname,...
%                                     dt_out = dt_out);
% writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
% writematrix(E_t,sprintf('%senergy.csv', pathname));
% filename = strcat(pathname, "movie");
% fprintf("Creating movie\n");
% ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename, dtframes = 1)

% init_file = sprintf("%s/09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_128x128__20max.csv",indir);
% % "10_30_25 CPC_metacentric_transition_model_11_06_2025_transition_model_2ummin_KTmovement_NDC80avail_0.1_fixed_delT_18s_18_256x256_5max.csv"
% % "09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_256x256_5max.csv"
% phi0 = readmatrix(init_file);
% pathname = sprintf("%s/09_16_25_CPC_metacentric_tensed_model_v2_09_16_25_metacentric_tensed_model_120_128x128__20max", outdir);
% fprintf("Running NMG solver with parameters: %s\n", pathname);
% [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0,...
%                                     t_iter = max_it,...
%                                     dt = dt,...
%                                     epsilon2= epsilon2,...
%                                     boundary = boundary,...
%                                     printphi=print_phi,...
%                                     pathname=pathname,...
%                                     dt_out = dt_out);
% writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
% writematrix(E_t,sprintf('%senergy.csv', pathname));
% filename = strcat(pathname, "movie");
% fprintf("Creating movie\n");
% ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename, dtframes = 1)


