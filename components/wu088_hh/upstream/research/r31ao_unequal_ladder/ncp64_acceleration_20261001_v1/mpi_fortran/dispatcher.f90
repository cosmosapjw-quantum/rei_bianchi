program ncp64_dispatch
  use, intrinsic :: iso_c_binding, only: c_char, c_int, c_null_char
  use, intrinsic :: iso_fortran_env, only: int64
  use mpi_f08
  implicit none
  integer, parameter :: task_tag=100, stop_tag=101, done_tag=102, max_tasks=100000
  integer :: ierr, rank, ranks, n, next, active, completed, dispatched, failures
  integer :: i, p, ios, unit, rc, prepared, signal_result, message(2), arg_length
  integer, allocatable :: ids(:), deadlines(:), job_state(:), running(:), rank_done(:)
  logical, allocatable :: seen(:)
  integer(int64) :: total_timeout_budget
  character(len=4096) :: python, worker, manifest, worklist
  character(kind=c_char), allocatable :: cp(:), cw(:), cm(:)
  type(MPI_Status) :: status
  interface
    function run_worker(py, script, path, task, seconds) bind(C,name='ncp64_run_worker') result(code)
      import :: c_char, c_int
      character(kind=c_char), intent(in) :: py(*), script(*), path(*)
      integer(c_int), value :: task, seconds
      integer(c_int) :: code
    end function
  end interface

  call MPI_Init(ierr)
  if (ierr /= MPI_SUCCESS) stop 2
  call MPI_Comm_set_errhandler(MPI_COMM_WORLD, MPI_ERRORS_RETURN, ierr); call checked(ierr)
  call MPI_Comm_rank(MPI_COMM_WORLD, rank, ierr); call checked(ierr)
  call MPI_Comm_size(MPI_COMM_WORLD, ranks, ierr); call checked(ierr)
  if (command_argument_count() /= 4) call abort_run('four absolute positional paths required')
  do i=1,4
    call get_command_argument(i,length=arg_length,status=ios)
    if (ios /= 0 .or. arg_length < 1 .or. arg_length > 4096) call abort_run('invalid path length')
  end do
  call get_command_argument(1,python); call get_command_argument(2,worker)
  call get_command_argument(3,manifest); call get_command_argument(4,worklist)
  if (python(1:1)/='/' .or. worker(1:1)/='/' .or. manifest(1:1)/='/' .or. worklist(1:1)/='/') &
    call abort_run('absolute paths required')
  cp=c_string(trim(python)); cw=c_string(trim(worker)); cm=c_string(trim(manifest))
  failures=0; completed=0; dispatched=0

  if (rank==0) then
    open(newunit=unit,file=trim(worklist),status='old',action='read',iostat=ios)
    if (ios/=0) call abort_run('cannot open worklist')
    read(unit,*,iostat=ios) n
    if (ios/=0) call abort_run('missing task count')
    if (n<0 .or. n>max_tasks) call abort_run('task count outside bounded domain')
    allocate(ids(n),deadlines(n),job_state(n),seen(n)); seen=.false.
    do i=1,n
      read(unit,*,iostat=ios) ids(i),deadlines(i)
      if (ios/=0) call abort_run('malformed worklist row')
      if (ids(i)<0 .or. ids(i)>=n) call abort_run('task index outside permutation')
      if (seen(ids(i)+1)) call abort_run('duplicate task index')
      seen(ids(i)+1)=.true.
      if (deadlines(i)<1 .or. deadlines(i)>86410) call abort_run('invalid supervisor deadline')
    end do
    read(unit,*,iostat=ios) p
    if (ios>=0) call abort_run('unexpected trailing worklist data')
    close(unit)
    ! Only integer scheduling bookkeeping is eligible for SIMD. No scientific reduction.
    prepared=0; total_timeout_budget=0_int64
    !$omp simd reduction(+:prepared,total_timeout_budget)
    do i=1,n
      job_state(i)=0
      prepared=prepared+1
      total_timeout_budget=total_timeout_budget+int(deadlines(i),int64)
    end do
    !$omp end simd
    if (prepared/=n) call abort_run('integer bookkeeping mismatch')
    if (ranks==1) then
      do i=1,n
        dispatched=dispatched+1
        rc=int(run_worker(cp,cw,cm,int(ids(i),c_int),int(deadlines(i),c_int)))
        job_state(ids(i)+1)=rc; completed=completed+1
        if (rc/=0) then
          failures=failures+1
          exit
        end if
      end do
    else
      allocate(running(0:ranks-1),rank_done(0:ranks-1)); running=-1; rank_done=0
      next=1; active=0
      do p=1,ranks-1
        call dispatch_or_stop(p)
      end do
      do while(active>0)
        call MPI_Recv(message,2,MPI_INTEGER,MPI_ANY_SOURCE,done_tag,MPI_COMM_WORLD,status,ierr)
        call checked(ierr)
        p=status%MPI_SOURCE
        if (p<1 .or. p>=ranks) call abort_run('invalid completion source')
        if (running(p)<0 .or. message(1)/=running(p)) call abort_run('unexpected completion task')
        rc=message(2); job_state(message(1)+1)=rc
        completed=completed+1; rank_done(p)=rank_done(p)+1; active=active-1; running(p)=-1
        if (rc/=0) failures=failures+1
        call dispatch_or_stop(p)
      end do
      do p=1,ranks-1
        write(*,'(a,i0,a,i0,a)') '{"rank":',p,',"completed_tasks":',rank_done(p),'}'
      end do
    end if
    write(*,'(a,i0,a,i0,a,i0,a,i0,a,i0,a)') '{"tasks":',n,',"dispatched":',dispatched, &
      ',"completed":',completed,',"failed":',failures,',"not_dispatched":',n-dispatched,'}'
    write(*,'(a,i0,a)') '{"integer_supervisor_budget_seconds":',total_timeout_budget,'}'
  else
    do
      call MPI_Recv(message,2,MPI_INTEGER,0,MPI_ANY_TAG,MPI_COMM_WORLD,status,ierr); call checked(ierr)
      if (status%MPI_TAG==stop_tag) exit
      if (status%MPI_TAG/=task_tag) call abort_run('unknown control tag')
      rc=int(run_worker(cp,cw,cm,int(message(1),c_int),int(message(2),c_int)))
      message(2)=rc
      call MPI_Send(message,2,MPI_INTEGER,0,done_tag,MPI_COMM_WORLD,ierr); call checked(ierr)
    end do
  end if
  signal_result=0
  if (rank==0 .and. failures/=0) signal_result=2
  call MPI_Bcast(signal_result,1,MPI_INTEGER,0,MPI_COMM_WORLD,ierr); call checked(ierr)
  call MPI_Finalize(ierr)
  if (ierr/=MPI_SUCCESS .or. signal_result/=0) stop 2

contains
  subroutine checked(code)
    integer,intent(in)::code
    if(code/=MPI_SUCCESS) call abort_run('MPI operation failed')
  end subroutine

  subroutine abort_run(reason)
    character(len=*),intent(in)::reason
    integer::abort_error
    write(*,'(a)') 'NCP64_ABORT: '//reason
    call MPI_Abort(MPI_COMM_WORLD,2,abort_error)
    stop 2
  end subroutine

  subroutine dispatch_or_stop(destination)
    integer,intent(in)::destination
    integer::tag
    message=0; tag=stop_tag
    if(failures==0 .and. next<=n) then
      message=[ids(next),deadlines(next)]; tag=task_tag
      running(destination)=ids(next); next=next+1
      active=active+1; dispatched=dispatched+1
    end if
    call MPI_Send(message,2,MPI_INTEGER,destination,tag,MPI_COMM_WORLD,ierr); call checked(ierr)
  end subroutine

  function c_string(text) result(chars)
    character(len=*),intent(in)::text
    character(kind=c_char),allocatable::chars(:)
    integer::j
    allocate(chars(len(text)+1))
    do j=1,len(text)
      chars(j)=text(j:j)
    end do
    chars(len(text)+1)=c_null_char
  end function
end program
