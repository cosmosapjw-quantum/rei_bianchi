define internal fastcc void @_ZN4core5array11try_from_fn17h1448b3e0868a6236E(ptr dead_on_unwind noalias noundef nonnull writable writeonly align 8 captures(none) dereferenceable(128) initializes((0, 128)) %_0, ptr dead_on_return noalias noundef nonnull readonly align 8 captures(none) dereferenceable(40) %cb) unnamed_addr #5 personality ptr @rust_eh_personality {
start:
  tail call void @llvm.experimental.noalias.scope.decl(metadata !706)
  %_18.i.i.i = load ptr, ptr %cb, align 8, !alias.scope !709, !noalias !714, !nonnull !8, !align !39, !noundef !8
  %_6.i.i.i = load double, ptr %_18.i.i.i, align 8, !noalias !716, !noundef !8
  %0 = getelementptr inbounds nuw i8, ptr %cb, i64 8
  %_19.i.i.i = load ptr, ptr %0, align 8, !alias.scope !709, !noalias !714, !nonnull !8, !align !39, !noundef !8
  %1 = getelementptr inbounds nuw i8, ptr %_18.i.i.i, i64 8
  %_10.i.i.i = load double, ptr %1, align 8, !noalias !716, !noundef !8
  %2 = getelementptr inbounds nuw i8, ptr %cb, i64 16
  %_21.i.i.i = load ptr, ptr %2, align 8, !alias.scope !709, !noalias !714, !nonnull !8, !align !39, !noundef !8
  %3 = getelementptr inbounds nuw i8, ptr %_18.i.i.i, i64 16
  %_13.i.i.i = load double, ptr %3, align 8, !noalias !716, !noundef !8
  %4 = getelementptr inbounds nuw i8, ptr %cb, i64 24
  %_23.i.i.i = load ptr, ptr %4, align 8, !alias.scope !709, !noalias !714, !nonnull !8, !align !39, !noundef !8
  %5 = getelementptr inbounds nuw i8, ptr %_18.i.i.i, i64 24
  %_16.i.i.i = load double, ptr %5, align 8, !noalias !716, !noundef !8
  %6 = getelementptr inbounds nuw i8, ptr %cb, i64 32
  %_25.i.i.i = load ptr, ptr %6, align 8, !alias.scope !709, !noalias !714, !nonnull !8, !align !39, !noundef !8
  tail call void @llvm.experimental.noalias.scope.decl(metadata !717)
  tail call void @llvm.experimental.noalias.scope.decl(metadata !718)
  %7 = getelementptr inbounds nuw i8, ptr %_19.i.i.i, i64 64
  %8 = getelementptr inbounds nuw i8, ptr %_21.i.i.i, i64 64
  %9 = getelementptr inbounds nuw i8, ptr %_23.i.i.i, i64 64
  %10 = getelementptr inbounds nuw i8, ptr %_25.i.i.i, i64 64
  %11 = load <8 x double>, ptr %_19.i.i.i, align 8, !noalias !719
  %12 = insertelement <8 x double> poison, double %_6.i.i.i, i64 0
  %13 = shufflevector <8 x double> %12, <8 x double> poison, <8 x i32> zeroinitializer
  %14 = fmul <8 x double> %13, %11
  %15 = load <8 x double>, ptr %_21.i.i.i, align 8, !noalias !719
  %16 = insertelement <8 x double> poison, double %_10.i.i.i, i64 0
  %17 = shufflevector <8 x double> %16, <8 x double> poison, <8 x i32> zeroinitializer
  %18 = fmul <8 x double> %17, %15
  %19 = fadd <8 x double> %14, %18
  %20 = load <8 x double>, ptr %_23.i.i.i, align 8, !noalias !719
  %21 = insertelement <8 x double> poison, double %_13.i.i.i, i64 0
  %22 = shufflevector <8 x double> %21, <8 x double> poison, <8 x i32> zeroinitializer
  %23 = fmul <8 x double> %22, %20
  %24 = fadd <8 x double> %19, %23
  %25 = load <8 x double>, ptr %_25.i.i.i, align 8, !noalias !719
  %26 = insertelement <8 x double> poison, double %_16.i.i.i, i64 0
  %27 = shufflevector <8 x double> %26, <8 x double> poison, <8 x i32> zeroinitializer
  %28 = fmul <8 x double> %27, %25
  %29 = fadd <8 x double> %24, %28
  store <8 x double> %29, ptr %_0, align 8, !alias.scope !720
  %_8.sroa.11.0._0.sroa_idx = getelementptr inbounds nuw i8, ptr %_0, i64 64
  %30 = load <8 x double>, ptr %7, align 8, !noalias !719
  %31 = fmul <8 x double> %13, %30
  %32 = load <8 x double>, ptr %8, align 8, !noalias !719
  %33 = fmul <8 x double> %17, %32
  %34 = fadd <8 x double> %31, %33
  %35 = load <8 x double>, ptr %9, align 8, !noalias !719
  %36 = fmul <8 x double> %22, %35
  %37 = fadd <8 x double> %34, %36
  %38 = load <8 x double>, ptr %10, align 8, !noalias !719
  %39 = fmul <8 x double> %27, %38
  %40 = fadd <8 x double> %37, %39
  store <8 x double> %40, ptr %_8.sroa.11.0._0.sroa_idx, align 8, !alias.scope !720
  ret void
}
