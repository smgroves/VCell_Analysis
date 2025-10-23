function phi_new = fd_solver(phi_old,nx,ny,xright,xleft,yright,yleft, ...
    dt,epsilon2,boundary,printres)
%This function uses the finite difference (Euler) method to solve the 
%Cahn-Hilliard equation for the next time step.
%
%INPUTS
    %phi_old = Prior chemical state.
    %nx = Number of grid points in x.
    %ny = Number of grid points in y.
    %xright = Rightmost grid point in x.
    %xleft = Leftmost grid point in x.
    %yright = Rightmost gridpoint in y.
    %yleft = Leftmost gridpoint in y.
    %dt = Time step.
    %epsilon2 = Squared interfacial transition distance (see ϵ^2 term in Lee et al., Mathematics 2020)
    %boundary = 'periodic' or 'neumann' boundary conditions.
    %printres = Logical to print residuals to file.
%
%OUTPUT
    %phi_new = Next chemical state.

%Calculate source terms
s_mu = zeros(nx,ny);
phi_lap = ch_laplace(phi_old,nx,ny,xright,xleft,yright,yleft,boundary);
mu = phi_old.^3 - phi_old - epsilon2*phi_lap;
mu_lap = ch_laplace(mu,nx,ny,xright,xleft,yright,yleft,boundary);
phi_new = phi_old + mu_lap*dt; %Propagate forward to first order with a mobility of one
resid2 = ch_error2(phi_old,phi_new,mu,nx,ny,xright,xleft,yright,yleft,dt,boundary);
if printres
    writematrix(resid2,strcat(pwd,'/phi_res2.csv'),'WriteMode','append');
end

end