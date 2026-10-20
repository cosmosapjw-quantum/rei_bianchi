_ZN4core5array11try_from_fn17h1448b3e0868a6236E:
	.cfi_startproc
	movq	(%rsi), %rax
	movq	8(%rsi), %rcx
	movq	16(%rsi), %rdx
	movq	24(%rsi), %r8
	movq	32(%rsi), %rsi
	vbroadcastsd	(%rax), %zmm0
	vbroadcastsd	8(%rax), %zmm2
	vbroadcastsd	16(%rax), %zmm3
	vbroadcastsd	24(%rax), %zmm5
	vmulpd	(%rcx), %zmm0, %zmm1
	vmulpd	(%rdx), %zmm2, %zmm4
	vmulpd	(%r8), %zmm3, %zmm7
	vmulpd	(%rsi), %zmm5, %zmm6
	vaddpd	%zmm4, %zmm1, %zmm1
	vaddpd	%zmm7, %zmm1, %zmm1
	vaddpd	%zmm6, %zmm1, %zmm1
	vmovupd	%zmm1, (%rdi)
	vmulpd	64(%rdx), %zmm2, %zmm1
	vmulpd	64(%rcx), %zmm0, %zmm0
	vmulpd	64(%r8), %zmm3, %zmm3
	vmulpd	64(%rsi), %zmm5, %zmm2
	vaddpd	%zmm1, %zmm0, %zmm0
	vaddpd	%zmm3, %zmm0, %zmm0
	vaddpd	%zmm2, %zmm0, %zmm0
	vmovupd	%zmm0, 64(%rdi)
	vzeroupper
	retq
