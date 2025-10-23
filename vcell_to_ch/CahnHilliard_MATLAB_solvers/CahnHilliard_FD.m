function [t_out,phi_t,delta_mass_t,E_t] = CahnHilliard_FD(phi0,varargin)
%This function uses the finite difference (Euler) method to solve the 
%Cahn-Hilliard equation for a specified number of time steps of size dt.
% 
%INPUTS
    %phi0 = Initial field of chemical states in the domain, created by ch_initialization.
%
%NAME-VALUE PAIRS
    %t_iter = Number of time steps simulated. Default = 1e3.
    %dt = Time step. Default = 2.5e-5 characteristic times.
    %dt_out = Spacing of time steps output to phi_t as a multidimensional
    %   array (if less than 1e9 elements) or printed file (if greater than
    %   1e9 elements). Default = 1, to output every time step. 
    %m = Number of mesh points over which the interface exists. Default = 4. 
    %epsilon2 = Squared interfacial transition distance; if specified,
    %   m will be overwritten. Default = nan (do not overwrite m).
    %boundary = Boundary conditions for the simulation:
    %   'periodic' (default) - flux on one domain border equals negative flux on the opposite border.
    %   'neumann' - zero flux on the domain borders.
    %c_relax = Number of smoothing relaxations done at the start of the
    %   finite difference method. Default = 2.  **DO WE WANT TO MAKE THIS THE DEFAULT**
    %domain = Vector of rightmost and leftmost grid points in x and y.
    %   Format: [xright xleft yright yleft]. Default = [1 0 1 0].
    %printres = Logical to print solver residuals to a file. Default = false.
    %printphi = Logical to print phi to a file regardless of whether or 
    %   not it can be saved as a multidimensional array. Default = false.
    % pathname = Name of the path to which phi is printed. Default = 'cd'. May include a prefix for the filename.
    %presmooth = Optional smoothing before the solver. Default = false.

%
%OUTPUT
    %t_out = Time corresponding to the dt time step outputs.
    %phi_t = Multidimensional array of phi over t_out.
    %delta_mass_t = Vector of mass change over t_out.
    %E_t = Vector of relative energy over t_out.

%% Set option defaults and parse inputs

%Set parameter defaults
default_t_iter = 1e3;
default_dt = 2.5e-5;
default_dt_out = 10;
default_m = 4;
default_epsilon2 = nan;
default_boundary = 'periodic';
default_c_relax = 2;
default_domain = [1 0 1 0];
default_printres = false;
default_printphi = false;
default_pathname = 'cd';
default_presmooth = false;

CahnHilliard_FD_parser = inputParser;

%Set general criteria for inputs and name-value pairs
valid_matrix = @(x) ismatrix(x);
valid_integer = @(x) x-floor(x) == 0;
valid_pos_num = @(x) isnumeric(x) && (x > 0);
valid_boundary_type = @(x) strcmpi(x,'periodic') || strcmpi(x,'neumann');
valid_domain_vector = @(x) length(x) == 4;
valid_logical = @(x) islogical(x) || x == 1 || x == 0;

%Set parser options and valid input criteria
addRequired(CahnHilliard_FD_parser,'phi0',valid_matrix);
   
addParameter(CahnHilliard_FD_parser,'t_iter',default_t_iter,valid_integer);
addParameter(CahnHilliard_FD_parser,'dt',default_dt,valid_pos_num);
addParameter(CahnHilliard_FD_parser,'dt_out',default_dt_out,valid_integer);
addParameter(CahnHilliard_FD_parser,'m',default_m,valid_integer);
addParameter(CahnHilliard_FD_parser,'epsilon2',default_epsilon2,valid_pos_num);
addParameter(CahnHilliard_FD_parser,'boundary',default_boundary,valid_boundary_type);
addParameter(CahnHilliard_FD_parser,'c_relax',default_c_relax,valid_integer);
addParameter(CahnHilliard_FD_parser,'domain',default_domain,valid_domain_vector);
addParameter(CahnHilliard_FD_parser,'printres',default_printres,valid_logical);
addParameter(CahnHilliard_FD_parser,'printphi',default_printphi,valid_logical);
addParameter(CahnHilliard_FD_parser,'pathname',default_pathname);
addParameter(CahnHilliard_FD_parser,'presmooth',default_presmooth,valid_logical);


parse(CahnHilliard_FD_parser,phi0,varargin{:});

%Extract parsed inputs
phi0 = CahnHilliard_FD_parser.Results.phi0;
t_iter = CahnHilliard_FD_parser.Results.t_iter;
dt = CahnHilliard_FD_parser.Results.dt;
dt_out = CahnHilliard_FD_parser.Results.dt_out;
m = CahnHilliard_FD_parser.Results.m;
epsilon2 = CahnHilliard_FD_parser.Results.epsilon2;
boundary = CahnHilliard_FD_parser.Results.boundary;
c_relax = CahnHilliard_FD_parser.Results.c_relax;
xright = CahnHilliard_FD_parser.Results.domain(1);
xleft = CahnHilliard_FD_parser.Results.domain(2);
yright = CahnHilliard_FD_parser.Results.domain(3);
yleft = CahnHilliard_FD_parser.Results.domain(4);
printres = CahnHilliard_FD_parser.Results.printres;
printphi = CahnHilliard_FD_parser.Results.printphi;
pathname = CahnHilliard_FD_parser.Results.pathname;
presmooth = CahnHilliard_FD_parser.Results.presmooth;

%% Define and initialize key simulation parameters

[nx,ny] = size(phi0); %Define number of grid points in x and y
h2 = ((xright-xleft)/nx)*((yright-yleft)/ny); %Define mesh size
if isnan(epsilon2)
    epsilon2 = h2*m^2/(2*sqrt(2)*atanh(0.9))^2; %Define ϵ^2 if not prespecified
else
    m = sqrt((epsilon2*(2*sqrt(2)*atanh(0.9))^2)/h2); %Else overwrite m
end

if presmooth
    [phi_old,~] = ch_smooth(phi0,zeros(nx,ny),phi0/dt- ...
    ch_laplace(phi0,nx,ny,xright,xleft,yright,yleft,boundary),zeros(nx,ny), ...
    c_relax,nx,ny,xright,xleft,yright,yleft,dt,epsilon2,boundary); %Smooth phi0 c_relax times
else
    phi_old = phi0;
end
downsampled = nx*ny*t_iter/dt_out > 1e9; %Logical index for the need to downsample
n_timesteps = floor(t_iter/dt_out);
if printphi %print to file
    mass_t = zeros(n_timesteps+1,1);
    E_t = zeros(n_timesteps+1,1);
    t_out = 0:dt_out*dt:(n_timesteps)*dt*dt_out;
    %do not make a phi_t variable but save the phi0 to a file
    if pathname == "cd"
        pathname = pwd;
    end
    Filename = strcat(pathname, 'phi.csv');
    %note that this will overwrite the file if it already exists
    writematrix(phi0, Filename, 'WriteMode', 'overwrite'); 
    phi_t = phi0; %if printing out, just save the initial phi as phi_t so you don't get an error of ouput argument not assigned
else %save to variable phi_t
    if downsampled
        new_dt_out = ceil(nx*ny*t_iter/1e9); %we need to round up to ensure we have enough space
        fprintf("Variable phi_t is too large with dt_out = %4.0f. Downsampling to every %4.0f time steps\n", dt_out, new_dt_out)
        dt_out = new_dt_out;
        n_timesteps = floor(t_iter/dt_out);
    end
    mass_t = zeros(n_timesteps+1,1);
    E_t = zeros(n_timesteps+1,1);
    t_out = 0:dt_out*dt:(n_timesteps)*dt*dt_out;
    phi_t = zeros(nx,ny,n_timesteps+1);
    phi_t(:,:,1) = phi0;
end

mass_t(1) = sum(sum(phi0))/(h2*nx*ny);
E_t(1) = ch_discrete_energy(phi0,h2,epsilon2);

%% Run finite difference solver

if printres
    fprintf('Saving squared residuals per iteration to file in the working directory\n')
end
for i = 1:t_iter
    phi_new = fd_solver(phi_old,nx,ny,xright,xleft,yright,yleft, ...
        dt,epsilon2,boundary,printres);
    phi_old = phi_new;
    if mod(i/t_iter*100,5) == 0
        fprintf('%3.0f percent complete\n',i/t_iter*100)
    end
    % save or print every dt_out
    if mod(i,dt_out) == 0
        t_index = floor(i/dt_out)+1;

        if printphi
            % Path = strcat(pwd, '/', Filename);
            writematrix(phi_new, Filename, 'WriteMode', 'append'); 
        else
            phi_t(:,:,t_index) = phi_old;
        end
        mass_t(t_index) = sum(sum(phi_old))/(h2*nx*ny);
        E_t(t_index) = ch_discrete_energy(phi_old,h2,epsilon2);
    end
end

%Center mass and normalize energy to t == 0
delta_mass_t = mass_t - mass_t(1);
E_t = E_t/E_t(1);

end
