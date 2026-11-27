# R10L literature notes

CPC 2023 Eq.(52)는 rho <= Re(Rc)+Im(Rc)를 인쇄하고 Im(Rc)를 nonadiabatic-coupling matrix element의 semi-width로 설명한다. R10J/K는 distributed program과 Appendix-A가 rho <= Re(Rc)를 쓴다는 것을 별도로 확정했다.

SciSpace 검색에서 Grozdanov & Solov'ev PRA90 032706 (2014), Solov'ev JPB38 review (2005), Richter & Solov'ev PRA48 432 (1993), Janev-Pop-Jordanov-Solov'ev JPB30 L353 (1997)을 확인했다. 검색된 abstract들은 impact-parameter-dependent branch-point transition physics를 지지하지만 REAL support를 universal theorem으로 정립하지 않는다. add-column methodology/conclusions는 해당 고전 논문들에 추가 데이터를 반환하지 않았다.

Independent benchmarks:
- Stolterfoht et al., PRA81 052704 (2010), DOI 10.1103/PhysRevA.81.052704. Library full PDF. Ab initio TDSE shell-selective n=1,2,3 cross sections from 30 eV/u upward. Figure 8 includes 0.5 and 5 keV/u. The paper states n=2 dominates, n=2/n=3 differ roughly 10--100, n=1 is orders smaller, >1 keV/u radial coupling dominates, lower energies are more rotation-sensitive. It notes Minami's straight-line trajectory can affect low-energy data.
- Liu et al., PRA67 052705 (2003), DOI 10.1103/PhysRevA.67.052705. HSCC n=2, Ecm=10 eV..4 keV; Ecm=0.8 EkeV/u for He2+ on H.
- Minami et al., JPB41 135201 (2008), DOI 10.1088/0953-4075/41/13/135201. State-selective CTMC/AOCC/lattice TDSE benchmark about 1--1000 keV/u.

Implication: author REAL support is an implementation convention, not physical validation. Next test is a no-fit A/B/C comparison against independent calculations.
