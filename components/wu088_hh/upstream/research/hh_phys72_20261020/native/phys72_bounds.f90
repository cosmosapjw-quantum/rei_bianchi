! PHYS72 binary128 arithmetic cross-check of the proved scalar inequalities.
! This program performs no HH integration and issues no interval certificate.
! Exact rational acceptance belongs to ../implementation/bounds.py.
program phys72_bounds
  use iso_fortran_env, only: real128, error_unit
  use ieee_arithmetic, only: ieee_is_finite
  implicit none
  real(real128) :: lam, delta, cstar, q, rho, prefactor, tail
  integer :: n, ios, argc, argument_length
  character(len=256) :: argument, lambda_input
  character(len=64) :: tail_text, lam_text, q_text, rho_text
  character(len=64) :: diagnostic

  lam = 1.0_real128
  lambda_input = '1'
  n = 3
  argc = command_argument_count()
  if (argc > 2) then
    write(error_unit,'(a)') 'Usage: phys72-bounds [nonnegative-decimal-lambda-abs [positive-N]]'
    stop 2
  end if
  if (argc >= 1) then
    call get_command_argument(1, argument, length=argument_length, status=ios)
    if (ios /= 0 .or. argument_length < 1) stop 2
    if (.not. decimal_token(argument(:argument_length))) stop 2
    lambda_input = argument
    read(argument, *, iostat=ios) lam
    if (ios /= 0) stop 2
  end if
  if (argc >= 2) then
    call get_command_argument(2, argument, length=argument_length, status=ios)
    if (ios /= 0 .or. argument_length < 1) stop 2
    if (.not. integer_token(argument(:argument_length))) stop 2
    read(argument, *, iostat=ios) n
    if (ios /= 0) stop 2
  end if
  if (.not. ieee_is_finite(lam)) stop 2
  if (lam < 0.0_real128 .or. n < 1 .or. n > 10000) stop 2

  delta = 3.0_real128 / 10.0_real128**23
  cstar = 253.0_real128 / 1000.0_real128
  q = cstar * 27.0_real128**2 * delta
  prefactor = 5929.0_real128 * delta / 2.0_real128
  rho = lam * q
  if (.not. ieee_is_finite(rho)) stop 2

  write(lam_text,'(es48.37e4)') lam
  write(q_text,'(es48.37e4)') q
  write(rho_text,'(es48.37e4)') rho
  if (rho < 1.0_real128) then
    tail = prefactor * lam * rho**n / (1.0_real128-rho)
    if (.not. ieee_is_finite(tail)) stop 2
    write(tail_text,'(es48.37e4)') tail
    diagnostic = 'FINITE_ROUNDED_CROSSCHECK'
    if (lam > 0.0_real128 .and. tail <= 0.0_real128) then
      diagnostic = 'ROUNDED_TAIL_UNDERFLOW'
    end if
  else
    tail_text = ''
    diagnostic = 'NONPOSITIVE_ROUNDED_DENOMINATOR'
  end if

  write(*,'(a)') '{'
  write(*,'(a)') '  "schema": "PHYS72_FORTRAN_ROUNDED_CROSSCHECK_V1",'
  write(*,'(a)') '  "status": "'//trim(diagnostic)//'",'
  write(*,'(a)') '  "certified": false,'
  write(*,'(a)') '  "certificate_authority": "Python exact Fraction evaluator",'
  write(*,'(a)') '  "q_formula_rounded": "'//trim(adjustl(q_text))//'",'
  write(*,'(a)') '  "lambda_abs_decimal_input": "'//trim(lambda_input)//'",'
  write(*,'(a)') '  "lambda_abs_rounded": "'//trim(adjustl(lam_text))//'",'
  write(*,'(a)') '  "contraction_rounded": "'//trim(adjustl(rho_text))//'",'
  if (len_trim(tail_text) > 0) then
    write(*,'(a)') '  "tail_formula_rounded": "'//trim(adjustl(tail_text))//'",'
  else
    write(*,'(a)') '  "tail_formula_rounded": null,'
  end if
  write(*,'(a,i0,a)') '  "terms_retained": ',n,','
  write(*,'(a,i0,a)') '  "real_significand_bits": ',digits(lam),','
  write(*,'(a,i0,a)') '  "real_decimal_range": ',range(lam),','
  write(*,'(a)') '  "physical_integrations": 0,'
  write(*,'(a)') '  "HH_R10": "OFF"'
  write(*,'(a)') '}'

contains

  logical function digit(c)
    character(len=1), intent(in) :: c
    digit = c >= '0' .and. c <= '9'
  end function digit

  logical function integer_token(token)
    character(len=*), intent(in) :: token
    integer :: i
    integer_token = .false.
    if (len(token) == 0) return
    do i = 1, len(token)
      if (.not. digit(token(i:i))) return
    end do
    integer_token = .true.
  end function integer_token

  ! List-directed READ alone accepts separators and an early slash. Validate
  ! the entire token before using READ only for conversion/range checking.
  logical function decimal_token(token)
    character(len=*), intent(in) :: token
    integer :: i, length, mantissa_digits, exponent_digits
    decimal_token = .false.
    length = len(token)
    if (length == 0) return
    i = 1
    if (token(i:i) == '+') i = i + 1
    mantissa_digits = 0
    do while (i <= length)
      if (.not. digit(token(i:i))) exit
      mantissa_digits = mantissa_digits + 1
      i = i + 1
    end do
    if (i <= length) then
      if (token(i:i) == '.') then
        i = i + 1
        do while (i <= length)
          if (.not. digit(token(i:i))) exit
          mantissa_digits = mantissa_digits + 1
          i = i + 1
        end do
      end if
    end if
    if (mantissa_digits == 0) return
    if (i <= length) then
      if (token(i:i) /= 'e' .and. token(i:i) /= 'E') return
      i = i + 1
      if (i <= length) then
        if (token(i:i) == '+' .or. token(i:i) == '-') i = i + 1
      end if
      exponent_digits = 0
      do while (i <= length)
        if (.not. digit(token(i:i))) return
        exponent_digits = exponent_digits + 1
        i = i + 1
      end do
      if (exponent_digits == 0) return
    end if
    decimal_token = i == length + 1
  end function decimal_token
end program phys72_bounds
