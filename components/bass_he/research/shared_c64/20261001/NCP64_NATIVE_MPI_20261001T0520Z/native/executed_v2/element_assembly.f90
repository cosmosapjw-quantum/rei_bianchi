! BASS_HE: double-precision element contraction with fixed reduction order.
! Memory layouts are specified in native/README.md and code/native_backend.py.
module bass_element_assembly
  use, intrinsic :: iso_c_binding, only: c_int, c_int64_t, c_double
  use omp_lib, only: omp_get_max_threads
  implicit none
  private
  public :: bass_element_blocks, bass_native_abi, bass_native_max_threads
contains
  integer(c_int) function bass_native_abi() bind(C, name='bass_native_abi')
    bass_native_abi = 2_c_int
  end function

  integer(c_int) function bass_native_max_threads() bind(C, name='bass_native_max_threads')
    bass_native_max_threads = omp_get_max_threads()
  end function

  subroutine bass_element_blocks(nq, na, nk, nl, basis, gaunt, vl, weights, kin, cent, ls, blocks) &
      bind(C, name='bass_element_blocks')
    integer(c_int), value, intent(in) :: nq, na, nk, nl
    real(c_double), intent(in) :: basis(na, nq), gaunt(nk, nl, nl), vl(nq, nk)
    real(c_double), intent(in) :: weights(nq), kin(na, na), cent(na, na)
    integer(c_int64_t), intent(in) :: ls(nl)
    real(c_double), intent(out) :: blocks(na, nl, na, nl)
    integer :: i, j

    ! No shared reduction: thread count changes ownership only.
    !$omp parallel default(none) &
    !$omp shared(nq,na,nk,nl,basis,gaunt,vl,weights,kin,cent,ls,blocks) private(i,j)
    block
      ! Allocate once per worker, not once per angular block.
      real(c_double), allocatable :: scratch_vll(:), scratch_acc(:, :)
      allocate(scratch_vll(nq), scratch_acc(na, na))
      !$omp do collapse(2) schedule(static)
      do i = 1, nl
        do j = 1, nl
          call one_angular_block(nq, na, nk, nl, i, j, basis, gaunt, vl, weights, kin, cent, ls, &
                                 blocks, scratch_vll, scratch_acc)
        end do
      end do
      !$omp end do
      deallocate(scratch_vll, scratch_acc)
    end block
    !$omp end parallel
  end subroutine

  recursive subroutine one_angular_block(nq, na, nk, nl, i, j, basis, gaunt, vl, weights, kin, cent, ls, &
                                         blocks, vll, acc)
    integer, intent(in) :: nq, na, nk, nl, i, j
    real(c_double), intent(in) :: basis(na, nq), gaunt(nk, nl, nl), vl(nq, nk)
    real(c_double), intent(in) :: weights(nq), kin(na, na), cent(na, na)
    integer(c_int64_t), intent(in) :: ls(nl)
    real(c_double), intent(inout) :: blocks(na, nl, na, nl)
    real(c_double), intent(out) :: vll(nq), acc(na, na)
    real(c_double) :: g, factor, angular_factor
    integer :: q, k, a, b

    vll = 0.0_c_double
    ! Preserve the increasing-k sum. Exact Gaunt zeros may be skipped;
    ! finite input validation makes 0*NaN/Inf semantics inapplicable.
    do k = 1, nk
      g = gaunt(k, i, j)
      if (g == 0.0_c_double) cycle
      !$omp simd
      do q = 1, nq
        vll(q) = vll(q) + vl(q, k)*g
      end do
      !$omp end simd
    end do
    acc = 0.0_c_double
    ! Preserve increasing-q sums; vector lanes are distinct output entries.
    do q = 1, nq
      do a = 1, na
        factor = (basis(a, q)*vll(q))*weights(q)
        !$omp simd
        do b = 1, na
          acc(b, a) = acc(b, a) + factor*basis(b, q)
        end do
        !$omp end simd
      end do
    end do
    if (i == j) then
      angular_factor = real(ls(i), c_double)*(real(ls(i), c_double) + 1.0_c_double)
      do a = 1, na
        !$omp simd
        do b = 1, na
          blocks(b, j, a, i) = acc(b, a) + (kin(a, b) + angular_factor*cent(a, b))
        end do
        !$omp end simd
      end do
    else
      do a = 1, na
        !$omp simd
        do b = 1, na
          blocks(b, j, a, i) = acc(b, a)
        end do
        !$omp end simd
      end do
    end if
  end subroutine
end module
