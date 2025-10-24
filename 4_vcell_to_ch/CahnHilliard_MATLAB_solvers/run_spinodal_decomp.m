 % FIGURE 1
indir = "/Users/catalinaalvarez/Documents/cpc_ch_data_2025";
outdir = "/Users/catalinaalvarez/Documents/cpc_ch_data_2025/output_MATLAB";

n_relax = 4;
m = 8;
GridSize = 256;
%h = 1/GridSize;
%epsilon = m * h/ (2 * sqrt(2) * atanh(0.9));
epsilon = 0.0089; %10A
%epsilon = 0.0067; %HeLa
%D = GridSize^2;
dt = 2.5e-5;
max_it = 2000;
boundary = 'neumann';
init_file = sprintf("%s/09_30_25_metacentric_relaxed_model_HeLa_CPC_Sgo1low_pH2Ainh_1_2_5.xlsx",indir);
phi0 = readmatrix(init_file);
print_phi = true;
dt_out = 1;
ny = GridSize;
% #################################################
% RUN SAV SOLVER 
% #################################################

% pathname = sprintf("%s/tensed_state_mod_SAV_output",outdir);
% fprintf("Running SAV solver with parameters: %s\n", pathname);
% tStart_SAV = tic;
% [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_SAV(phi0,...
%                                     t_iter = max_it,...
%                                     dt = dt,...
%                                     m = m,...
%                                     boundary = boundary,...
%                                     printphi=print_phi,...
%                                     pathname=pathname,...
%                                     dt_out = dt_out);
% elapsedTime = toc(tStart_SAV);
% 
% % fid = fopen('../Job_specs.csv', 'a+');
% % v = [string(datetime) "SAV_spinodal_decomp_smoothed_periodic_dtout_10_relaxation" "MATLAB" "SAV" GridSize epsilon dt 'NaN' max_it 'NaN' pathname elapsedTime "NaN" boundary];
% % fprintf(fid, '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n', v);
% % fclose(fid);
% 
% % writematrix(phi_t(:,:,end),sprintf('%sfinal_phi.csv', pathname));
% writematrix(delta_mass_t,sprintf('%smass_uncentered.csv', pathname));
% writematrix(E_t,sprintf('%senergy.csv', pathname));
% 
% fprintf("Creating movie\n");
% filename = strcat(pathname, "movie");
% if print_phi
%     ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename)
% else
%     ch_movie(phi_t,t_out, filename = filename);
% end

% % #################################################
% % RUN NMG SOLVER 
% % #################################################

pathname = sprintf("%s/09_30_25_metacentric_relaxed_model_HeLa_CPC_Sgo1low_pH2Ainh_1_2_5_10Ae_10x_output", outdir);
fprintf("Running NMG solver with parameters: %s\n", pathname);
tStart_NMG = tic;
[t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_NMG(phi0,...
                                    t_iter = max_it,...
                                    dt = dt,...
                                    m = m,...
                                    boundary = boundary,...
                                    printphi=print_phi,...
                                    pathname=pathname,...
                                    dt_out = dt_out,...
                                    tol = 1e-6);
elapsedTime = toc(tStart_NMG);

fid = fopen('../Job_specs.csv', 'a+');
v = [string(datetime) "NMG_spinodal_decomp_smoothed_dtout_10" "MATLAB" "NMG" GridSize epsilon dt 'NaN' max_it  pathname elapsedTime 'NaN' "periodic"];
fprintf(fid, '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n', v);
fclose(fid);

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



% % #################################################
% % RUN FD SOLVER 
% % #################################################

% pathname = sprintf("%s/FD_MATLAB_%d_dt_%.2e_Nx_%d_n_relax_%d_",outdir,max_it,dt, GridSize, n_relax);
% tStart_FD = tic;
% [t_out, phi_t, delta_mass_t, E_t] = CahnHilliard_FD_SMG(phi0,...
%                                     t_iter = max_it,...
%                                     dt = dt,...
%                                     m = m,...
%                                     boundary = boundary,...
%                                     printphi=print_phi,...
%                                     pathname=pathname,...
%                                     dt_out = dt_out);
% elapsedTime = toc(tStart_FD);

% fid = fopen('../Job_specs.csv', 'a+');
% v = [string(datetime) "FD_spinodal_decomp_smoothed_print" "MATLAB" "FD" GridSize epsilon dt 'NaN' max_it 'NaN' elapsedTime, pathname];
% fprintf(fid, '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n', v);
% fclose(fid);

% % writematrix(phi_t(:,:,end),sprintf('%sfinal_phi.csv', pathname));
% writematrix(delta_mass_t,sprintf('%smass.csv', pathname));
% writematrix(E_t,sprintf('%senergy.csv', pathname));
% t_out = 0:10*dt:max_it*dt;
% filename = strcat(pathname, "movie_long");
% phi_file = strcat(pathname, "phi.csv");
% fprintf("Creating movie\n");
% if print_phi
%     ch_movie_from_file(strcat(pathname,"phi.csv"), t_out, ny,filename = filename)
% else
%     ch_movie(phi_t,t_out, filename = filename);
% end
