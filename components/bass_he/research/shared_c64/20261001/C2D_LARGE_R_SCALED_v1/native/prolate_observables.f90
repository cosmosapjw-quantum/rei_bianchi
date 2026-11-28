module prolate_observables
  use iso_c_binding, only: c_int, c_double
  implicit none
contains
  integer(c_int) function bass_prolate_abi() bind(C)
    bass_prolate_abi = 1
  end function

  subroutine bass_direct(n, np, counts, xi, eta, w, g, a, ax, ae, r, za, zb, out) bind(C)
    integer(c_int), value :: n, np
    integer(c_int), intent(in) :: counts(np)
    real(c_double), intent(in) :: xi(n), eta(n), w(n), g(n), a(n), ax(n), ae(n)
    real(c_double), value :: r, za, zb
    real(c_double), intent(out) :: out(6)
    real(c_double) :: patches(6,np), c, midpoint, p, q, rho, z, rx, re, zx, ze
    real(c_double) :: det, ar, az, measure, common, px, terms(6), local(6)
    integer :: starts(np), k, i, j
    starts(1)=1
    do k=2,np
      starts(k)=starts(k-1)+counts(k-1)
    end do
    c=r/2.0_c_double
    midpoint=(za-zb)*r/(2.0_c_double*(za+zb))
    !$omp parallel do default(none) schedule(static) &
    !$omp shared(np,starts,counts,xi,eta,w,g,a,ax,ae,r,c,midpoint,patches) &
    !$omp private(k,i,j,p,q,rho,z,rx,re,zx,ze,det,ar,az,measure,common,px,terms,local)
    do k=1,np
      local=0.0_c_double
      do i=starts(k),starts(k)+counts(k)-1
        p=xi(i)*xi(i)-1.0_c_double
        q=1.0_c_double-eta(i)*eta(i)
        rho=c*sqrt(p*q)
        z=c*xi(i)*eta(i)+midpoint
        rx=c*xi(i)*sqrt(q/p)
        re=-c*eta(i)*sqrt(p/q)
        zx=c*eta(i)
        ze=c*xi(i)
        det=rx*ze-re*zx
        ar=(ze*ax(i)-zx*ae(i))/det
        az=(-re*ax(i)+rx*ae(i))/det
        measure=w(i)*r**3/8.0_c_double*(xi(i)*xi(i)-eta(i)*eta(i))
        common=measure*g(i)/sqrt(2.0_c_double)
        px=ar+a(i)/rho
        terms(1)=common*(z*px-rho*az)
        terms(2)=common*((c*xi(i)*eta(i)-c)*px-rho*az)
        terms(3)=common*px
        terms(4)=common*rho*a(i)
        terms(5)=measure*g(i)*g(i)
        terms(6)=measure*a(i)*a(i)
        !$omp simd
        do j=1,6
          local(j)=local(j)+terms(j)
        end do
      end do
      patches(:,k)=local
    end do
    !$omp end parallel do
    out=0.0_c_double
    do k=1,np
      !$omp simd
      do j=1,6
        out(j)=out(j)+patches(j,k)
      end do
    end do
  end subroutine

  subroutine bass_torque(n, np, counts, xi, eta, w, g, a, r, out) bind(C)
    integer(c_int), value :: n, np
    integer(c_int), intent(in) :: counts(np)
    real(c_double), intent(in) :: xi(n), eta(n), w(n), g(n), a(n)
    real(c_double), value :: r
    real(c_double), intent(out) :: out(2)
    real(c_double) :: patches(2,np), rho, ra, rb, common, terms(2), local(2)
    integer :: starts(np), k, i, j
    starts(1)=1
    do k=2,np
      starts(k)=starts(k-1)+counts(k-1)
    end do
    !$omp parallel do default(none) schedule(static) &
    !$omp shared(np,starts,counts,xi,eta,w,g,a,r,patches) &
    !$omp private(k,i,j,rho,ra,rb,common,terms,local)
    do k=1,np
      local=0.0_c_double
      do i=starts(k),starts(k)+counts(k)-1
        rho=r/2.0_c_double*sqrt((xi(i)*xi(i)-1.0_c_double)*(1.0_c_double-eta(i)*eta(i)))
        ra=r/2.0_c_double*(xi(i)+eta(i))
        rb=r/2.0_c_double*(xi(i)-eta(i))
        common=w(i)*r**3/8.0_c_double*(xi(i)*xi(i)-eta(i)*eta(i))*rho*g(i)*a(i)/sqrt(2.0_c_double)
        terms(1)=common/ra**3
        terms(2)=common/rb**3
        !$omp simd
        do j=1,2
          local(j)=local(j)+terms(j)
        end do
      end do
      patches(:,k)=local
    end do
    !$omp end parallel do
    out=0.0_c_double
    do k=1,np
      !$omp simd
      do j=1,2
        out(j)=out(j)+patches(j,k)
      end do
    end do
  end subroutine
end module
