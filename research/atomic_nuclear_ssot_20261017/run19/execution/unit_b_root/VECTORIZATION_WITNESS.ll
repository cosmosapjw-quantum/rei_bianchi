define internal fastcc void @_ZN11coeff_bench21vectorization_witness17h1328181081196f09E(ptr dead_on_unwind noalias noundef nonnull writable writeonly align 8 captures(none) dereferenceable(128) initializes((0, 128)) %_0, ptr noalias noundef nonnull readonly align 8 captures(address, read_provenance) dereferenceable(128) %a, ptr noalias noundef nonnull readonly align 8 captures(address, read_provenance) dereferenceable(128) %b, ptr noalias noundef nonnull readonly align 8 captures(address, read_provenance) dereferenceable(128) %c, ptr noalias noundef nonnull readonly align 8 captures(address, read_provenance) dereferenceable(128) %d, ptr dead_on_return noalias noundef nonnull readonly align 8 captures(none) dereferenceable(32) %w) unnamed_addr #0 {
start:
  %_10 = alloca [40 x i8], align 8
  %_6 = alloca [32 x i8], align 8
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %_6)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %_6, ptr noundef nonnull align 8 dereferenceable(32) %w, i64 32, i1 false)
  call void @llvm.lifetime.start.p0(i64 40, ptr nonnull %_10)
  store ptr %_6, ptr %_10, align 8
  %_7.sroa.4.0._10.sroa_idx = getelementptr inbounds nuw i8, ptr %_10, i64 8
  store ptr %a, ptr %_7.sroa.4.0._10.sroa_idx, align 8
  %_7.sroa.5.0._10.sroa_idx = getelementptr inbounds nuw i8, ptr %_10, i64 16
  store ptr %b, ptr %_7.sroa.5.0._10.sroa_idx, align 8
  %_7.sroa.6.0._10.sroa_idx = getelementptr inbounds nuw i8, ptr %_10, i64 24
  store ptr %c, ptr %_7.sroa.6.0._10.sroa_idx, align 8
  %_7.sroa.7.0._10.sroa_idx = getelementptr inbounds nuw i8, ptr %_10, i64 32
  store ptr %d, ptr %_7.sroa.7.0._10.sroa_idx, align 8
; call core::array::try_from_fn
  call fastcc void @_ZN4core5array11try_from_fn17h1448b3e0868a6236E(ptr noalias noundef align 8 captures(address) dereferenceable(128) %_0, ptr noalias noundef align 8 captures(address) dereferenceable(40) %_10) #32
  call void @llvm.lifetime.end.p0(i64 40, ptr nonnull %_10)
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %_6)
  ret void
}
