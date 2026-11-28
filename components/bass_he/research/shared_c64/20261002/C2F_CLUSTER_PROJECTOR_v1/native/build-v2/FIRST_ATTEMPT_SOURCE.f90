! Strict binary64 overlap: U^dagger diag(w) V. No scientific eigenproblem.
! Eight independent compensated lanes are SIMD; fixed compensated final merge.
module bass_weighted_overlap
  use, intrinsic :: iso_c_binding
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use omp_lib, only: omp_get_max_threads, omp_get_num_threads, omp_get_dynamic, omp_get_thread_limit
  implicit none
  private
  public :: bass_overlap, bass_overlap_contract
  integer, parameter :: tile_rows = 8
contains
  subroutine bass_overlap_contract(info, source_hash) bind(C, name='bass_overlap_contract')
    integer(c_int), intent(out) :: info(7)
    character(kind=c_char), intent(out) :: source_hash(65)
    character(len=64), parameter :: source_digest = BASS_OVERLAP_SOURCE_SHA
    integer :: i
    info = [1_c_int, int(storage_size(0.0_c_double), c_int), &
            int(storage_size(cmplx(0.0_c_double, 0.0_c_double, c_double_complex)), c_int), &
            int(tile_rows, c_int), int(omp_get_max_threads(), c_int), &
            merge(1_c_int, 0_c_int, omp_get_dynamic()), int(omp_get_thread_limit(), c_int)]
    do i = 1, 64
      source_hash(i) = source_digest(i:i)
    end do
    source_hash(65) = c_null_char
  end subroutine bass_overlap_contract

  subroutine bass_overlap(n, k, l, threads, u, v, w, result, status, actual_threads) bind(C, name='bass_overlap')
    integer(c_int64_t), value, intent(in) :: n, k, l
    integer(c_int), value, intent(in) :: threads
    complex(c_double_complex), intent(in) :: u(n,k), v(n,l)
    real(c_double), intent(in) :: w(n)
    complex(c_double_complex), intent(out) :: result(k,l)
    integer(c_int), intent(out) :: status, actual_threads
    integer(c_int64_t) :: pair, a, b, start, row, length, j
    real(c_double) :: sr(tile_rows), si(tile_rows), cr(tile_rows), ci(tile_rows)
    real(c_double) :: xr, xi, tr, ti, final_r, final_i, correction_r, correction_i
    status = 1_c_int
    actual_threads = 0_c_int
    if (n <= 0 .or. k <= 0 .or. l <= 0 .or. threads <= 0) return
    if (k > huge(k) / l) return
    if (threads > omp_get_thread_limit() .or. omp_get_dynamic()) then
      status = 3_c_int
      return
    end if
    !$omp parallel do default(none) schedule(static) num_threads(threads) &
    !$omp shared(n,k,l,u,v,w,result,actual_threads) &
    !$omp private(pair,a,b,start,row,length,j,sr,si,cr,ci,xr,xi,tr,ti,final_r,final_i,correction_r,correction_i)
    do pair = 0_c_int64_t, k*l-1_c_int64_t
      if (pair == 0) actual_threads = int(omp_get_num_threads(), c_int)
      a = modulo(pair,k) + 1_c_int64_t
      b = pair/k + 1_c_int64_t
      sr = 0.0_c_double
      si = 0.0_c_double
      cr = 0.0_c_double
      ci = 0.0_c_double
      do start = 1_c_int64_t, n, int(tile_rows,c_int64_t)
        length = min(int(tile_rows,c_int64_t), n-start+1_c_int64_t)
        !$omp simd private(row,xr,xi,tr,ti)
        do j = 1_c_int64_t, length
          row = start+j-1_c_int64_t
          xr = (real(u(row,a),c_double)*real(v(row,b),c_double) + aimag(u(row,a))*aimag(v(row,b))) * w(row)
          xi = (real(u(row,a),c_double)*aimag(v(row,b)) - aimag(u(row,a))*real(v(row,b),c_double)) * w(row)
          tr = sr(j) + xr
          cr(j) = cr(j) + merge((sr(j)-tr)+xr, (xr-tr)+sr(j), abs(sr(j)) >= abs(xr))
          sr(j) = tr
          ti = si(j) + xi
          ci(j) = ci(j) + merge((si(j)-ti)+xi, (xi-ti)+si(j), abs(si(j)) >= abs(xi))
          si(j) = ti
        end do
      end do
      ! Merge sums and compensations as separate terms. Pre-rounding sr+cr
      ! would lose small compensation before cancellation between lanes.
      final_r = 0.0_c_double
      final_i = 0.0_c_double
      correction_r = 0.0_c_double
      correction_i = 0.0_c_double
      do j = 1_c_int64_t, int(tile_rows,c_int64_t)
        tr = final_r + sr(j)
        correction_r = correction_r + merge((final_r-tr)+sr(j), (sr(j)-tr)+final_r, abs(final_r) >= abs(sr(j)))
        final_r = tr
        tr = final_r + cr(j)
        correction_r = correction_r + merge((final_r-tr)+cr(j), (cr(j)-tr)+final_r, abs(final_r) >= abs(cr(j)))
        final_r = tr
        ti = final_i + si(j)
        correction_i = correction_i + merge((final_i-ti)+si(j), (si(j)-ti)+final_i, abs(final_i) >= abs(si(j)))
        final_i = ti
        ti = final_i + ci(j)
        correction_i = correction_i + merge((final_i-ti)+ci(j), (ci(j)-ti)+final_i, abs(final_i) >= abs(ci(j)))
        final_i = ti
      end do
      result(a,b) = cmplx(final_r+correction_r,final_i+correction_i,kind=c_double_complex)
    end do
    !$omp end parallel do
    if (actual_threads /= threads) then
      status = 3_c_int
      return
    end if
    status = 0_c_int
    do b = 1_c_int64_t, l
      do a = 1_c_int64_t, k
        if (.not. ieee_is_finite(real(result(a,b),c_double)) .or. .not. ieee_is_finite(aimag(result(a,b)))) then
          status = 2_c_int
          return
        end if
      end do
    end do
  end subroutine bass_overlap
end module bass_weighted_overlap
