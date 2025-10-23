function g = g_fun_CN(phi0,r0,b,dt,hx,hy,epsilon2,gamma0,Beta,C0,k2,boundary)
    Lap_phi0 = Lap_SAV(phi0,k2,boundary);
    Lap_Lap_phi0 = Lap_SAV(Lap_phi0,k2,boundary);

    bphi0 = fft2(b.*phi0);
    bphi0 = hx*hy*bphi0(1,1);

    E1 = fft2(f_SAV(phi0,gamma0));
    g = phi0 - dt/2*epsilon2*Lap_Lap_phi0 + dt/2*gamma0*Lap_phi0 ...
        + dt*Lap_SAV(b,k2,boundary)*(r0 - 1/4*bphi0 - 1/2*Beta*dt*r0*(r0 - sqrt(E1(1,1)*hx*hy + C0)));
end