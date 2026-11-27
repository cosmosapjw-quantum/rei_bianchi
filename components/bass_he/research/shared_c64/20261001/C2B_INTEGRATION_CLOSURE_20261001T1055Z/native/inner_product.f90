module bass_inner_product
  use iso_c_binding
  implicit none
contains
  integer(c_int) function bass_inner_abi() bind(C)
    bass_inner_abi=1
  end function
  subroutine bass_inner(n,np,counts,w,a,b,result) bind(C)
    integer(c_int),value::n,np
    integer(c_int),intent(in)::counts(np)
    real(c_double),intent(in)::w(n),a(n),b(n)
    real(c_double),intent(out)::result
    real(c_double),allocatable::products(:),partial(:)
    integer,allocatable::starts(:)
    integer::i,j,k
    real(c_double)::s
    allocate(products(n),partial(np),starts(np))
    k=1
    do j=1,np
      starts(j)=k
      k=k+counts(j)
    end do
    !$omp parallel do simd schedule(static)
    do i=1,n
      products(i)=(w(i)*a(i))*b(i)
    end do
    !$omp end parallel do simd
    !$omp parallel do private(i,s) schedule(static)
    do j=1,np
      s=0.0_c_double
      do i=starts(j),starts(j)+counts(j)-1
        s=s+products(i)
      end do
      partial(j)=s
    end do
    !$omp end parallel do
    result=0.0_c_double
    do j=1,np
      result=result+partial(j)
    end do
    deallocate(products,partial,starts)
  end subroutine
end module
