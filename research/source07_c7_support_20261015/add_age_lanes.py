"""Expand C7 diagnostic example to compare pooled vs TWO source-age lanes.
Source physics unchanged; fresh/old age lanes are a bounded comparison oracle,
not a solution of perpetual source-age accumulation.
"""
from pathlib import Path
p=Path(__file__).resolve().parents[2]/"rust/rei_microphysics/examples/axbi_q_support_pilot.rs"
s=p.read_text()
old="reference_state_bytes,clipped_populated_cells,count_residual,energy_residual"
new="reference_state_bytes,clipped_populated_cells,count_residual,energy_residual,two_age_HI,two_age_HeI,two_age_heat,two_age_ms,two_age_payload_bytes"
assert s.count(old)==1;s=s.replace(old,new)
old="            let mut original = source_grid.clone();"
new="""            let mut old_age = QFixedGrid::new(&source, g0, nenergy, 433.)?;
            let mut late_age = QFixedGrid::new(&source, g0, nenergy, 433.)?;
            old_age.inject(&g0, 20., dt0, 1)?;
            late_age.inject(&gf, 4., dt4, 1)?;
            let t_age = Instant::now();
            let old_reaction=old_age.absorb_reconstructed_support(&gf,neutral,absorption_dt,4)?;
            let fresh_reaction=late_age.absorb_reconstructed_support(&gf,neutral,absorption_dt,4)?;
            let age_elapsed_ms=t_age.elapsed().as_secs_f64()*1000.;
            let age_hi=old_reaction.absorbed_per_h[0]+fresh_reaction.absorbed_per_h[0];
            let age_hei=old_reaction.absorbed_per_h[1]+fresh_reaction.absorbed_per_h[1];
            let age_heat=old_reaction.heat_ev_per_h+fresh_reaction.heat_ev_per_h;
            let age_bytes=old_age.buffer_capacity_bytes()+late_age.buffer_capacity_bytes();
            let mut original = source_grid.clone();"""
assert s.count(old)==1;s=s.replace(old,new)
old="{:.6},{:.6},{},{},{:.17e},{:.17e}\","
new="{:.6},{:.6},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6},{}\","
assert s.count(old)==1;s=s.replace(old,new)
old="source_grid.buffer_capacity_bytes(),clipped,count_res,energy_res);"
new="source_grid.buffer_capacity_bytes(),clipped,count_res,energy_res,age_hi,age_hei,age_heat,age_elapsed_ms,age_bytes);"
assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s)
print("AGE_LANE_DIAGNOSTIC_ADDED")
