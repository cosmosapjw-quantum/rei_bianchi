use rei_microphysics::{
    igm_checkpoint::{decode_checkpoint, encode_checkpoint, sha256_bytes, CheckpointIdentity},
    igm_config::parse_config,
    igm_history::History,
};
const CFG: &str = include_str!("../../../configs/igm_manufactured_v1.cfg");
fn fixture() -> (
    History,
    rei_microphysics::igm_history::HistoryState,
    CheckpointIdentity,
) {
    let text = CFG
        .replace("birth_panels=16", "birth_panels=2")
        .replace("energy_panels=2", "energy_panels=1");
    let (h, s) = History::new(parse_config(&text).unwrap()).unwrap();
    let id = CheckpointIdentity::new(text.as_bytes(), &h).unwrap();
    (h, s, id)
}
// Direct History stepping has no output consumer; these fixtures explicitly
// mark the output epochs traversed before serializing the same numeric state.
fn mark_elapsed_outputs(
    h: &History,
    mut s: rei_microphysics::igm_history::HistoryState,
) -> rei_microphysics::igm_history::HistoryState {
    while s.output_cursor <= h.config.output_panels
        && rei_microphysics::igm_checkpoint::output_coordinate(h, s.output_cursor).unwrap() < s.ln_a
    {
        s.output_cursor += 1;
    }
    s
}
#[test]
fn checkpoint_roundtrip_preserves_every_float_and_controller_bit() {
    let (h, mut s, id) = fixture();
    let first = h.births[0].ln_a;
    s = mark_elapsed_outputs(&h, h.advance_to(&s, first).unwrap());
    assert!(!s.packets.is_empty());
    s.rejected_steps = 17;
    let text = encode_checkpoint(&id, &h, &s, false).unwrap();
    let decoded = decode_checkpoint(&text, &id, &h).unwrap();
    assert!(!decoded.complete);
    assert_eq!(
        text,
        encode_checkpoint(&id, &h, &decoded.state, false).unwrap()
    );
    assert_eq!(format!("{:?}", s), format!("{:?}", decoded.state));
}
#[test]
fn changed_config_bytes_and_source_identity_are_rejected_before_state_parsing() {
    let (h, s, id) = fixture();
    let text = encode_checkpoint(&id, &h, &s, false).unwrap();
    let mut changed = id.clone();
    changed.config_sha256 = sha256_bytes(b"changed config bytes").unwrap();
    assert!(
        decode_checkpoint(&text.replace("ln_a=", "ln_a=INVALID"), &changed, &h)
            .unwrap_err()
            .to_string()
            .contains("IDENTITY_MISMATCH")
    );
    changed = id.clone();
    changed.source_sha256 = sha256_bytes(b"changed source").unwrap();
    assert!(decode_checkpoint(&text, &changed, &h).is_err());
    let with_comment = format!("{CFG}\n# byte identity\n");
    let (same_physics, _) = History::new(parse_config(&with_comment).unwrap()).unwrap();
    let one = CheckpointIdentity::new(CFG.as_bytes(), &same_physics).unwrap();
    let two = CheckpointIdentity::new(with_comment.as_bytes(), &same_physics).unwrap();
    assert_ne!(one.config_sha256, two.config_sha256);
    assert_eq!(one.source_sha256, two.source_sha256);
}
#[test]
fn continuous_and_restarted_histories_have_bit_identical_terminal_state() {
    let (h, s, id) = fixture();
    let mid = h.births[0].ln_a;
    let split = mark_elapsed_outputs(&h, h.advance_to(&s, mid).unwrap());
    let uninterrupted = mark_elapsed_outputs(&h, h.advance_to(&split, h.config.end).unwrap());
    let decoded =
        decode_checkpoint(&encode_checkpoint(&id, &h, &split, false).unwrap(), &id, &h).unwrap();
    let restarted = mark_elapsed_outputs(&h, h.advance_to(&decoded.state, h.config.end).unwrap());
    let terminal = encode_checkpoint(&id, &h, &uninterrupted, true).unwrap();
    assert_eq!(
        terminal,
        encode_checkpoint(&id, &h, &restarted, true).unwrap()
    );
    assert!(uninterrupted
        .packets
        .iter()
        .any(|p| p.log_per_h < f64::MIN_POSITIVE.ln()));
    let decoded_terminal = decode_checkpoint(&terminal, &id, &h).unwrap();
    assert!(decoded_terminal.complete);
    assert_eq!(
        terminal,
        encode_checkpoint(&id, &h, &decoded_terminal.state, true).unwrap()
    );
}
#[test]
fn malformed_or_inadmissible_checkpoints_are_rejected() {
    let (h, s, id) = fixture();
    let text = encode_checkpoint(&id, &h, &s, false).unwrap();
    for bad in [
        text.replace("ln_a=", "ln_a=NaN"),
        format!("{text}unknown=4\n"),
        format!("{text}accepted_steps=0\n"),
        text.replace("birth_cursor=0", "birth_cursor=999999999"),
        text.replace("w=", "w=-"),
        text.replace("complete=false", "complete=true"),
        text.replace("output_cursor=0", "output_cursor=999999999"),
    ] {
        assert!(decode_checkpoint(&bad, &id, &h).is_err(), "accepted {bad}");
    }
    let state = mark_elapsed_outputs(&h, h.advance_to(&s, h.births[0].ln_a).unwrap());
    let text = encode_checkpoint(&id, &h, &state, false).unwrap();
    let packet = text.lines().find(|l| l.starts_with("packet=")).unwrap();
    assert!(decode_checkpoint(&format!("{text}{packet}\n"), &id, &h).is_err());
    let values: Vec<_> = packet.strip_prefix("packet=").unwrap().split(',').collect();
    for log in ["NaN", "inf", "0", "-1e300"] {
        let malformed = text.replacen(
            packet,
            &format!("packet={},{},{log}", values[0], values[1]),
            1,
        );
        assert!(
            decode_checkpoint(&malformed, &id, &h).is_err(),
            "accepted malformed logarithmic packet: {log}"
        );
    }
    let second = text
        .lines()
        .filter(|l| l.starts_with("packet="))
        .nth(1)
        .unwrap();
    assert!(decode_checkpoint(&text.replacen(second, packet, 1), &id, &h).is_err());
    for (key, value) in [
        ("underflow_n_bound", "NaN"),
        ("underflow_n_bound", "1e-10"),
        ("underflow_e_bound", "1e-10"),
    ] {
        assert!(decode_checkpoint(
            &text.replace(&format!("{key}=0"), &format!("{key}={value}")),
            &id,
            &h
        )
        .is_err());
    }
}
#[test]
fn sha256_is_exact_bytes() {
    assert_eq!(
        sha256_bytes(b"abc").unwrap(),
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    );
}

#[test]
fn newborn_subcutoff_outflow_checkpoint_roundtrips_without_active_packets() {
    let text = CFG
        .replace("birth_panels=16", "birth_panels=2")
        .replace("energy_panels=2", "energy_panels=1")
        .replace("energy_min_ev=13.7", "energy_min_ev=10")
        .replace("energy_max_ev=100", "energy_max_ev=12");
    let (h, s) = History::new(parse_config(&text).unwrap()).unwrap();
    let id = CheckpointIdentity::new(text.as_bytes(), &h).unwrap();
    let s = mark_elapsed_outputs(&h, h.advance_to(&s, h.births[0].ln_a).unwrap());
    assert!(s.packets.is_empty());
    assert!(s.ledger.out_n > 0.0);
    assert_eq!(s.ledger.out_n, s.ledger.emitted_n);
    let checkpoint = encode_checkpoint(&id, &h, &s, false).unwrap();
    let decoded = decode_checkpoint(&checkpoint, &id, &h).unwrap();
    assert_eq!(
        checkpoint,
        encode_checkpoint(&id, &h, &decoded.state, false).unwrap()
    );
}

#[test]
fn stale_output_cursor_is_rejected_before_returning_state() {
    let (h, s, id) = fixture();
    let mut s = h.advance_to(&s, h.births[0].ln_a).unwrap();
    while s.output_cursor <= h.config.output_panels
        && rei_microphysics::igm_checkpoint::output_coordinate(&h, s.output_cursor).unwrap()
            < s.ln_a
    {
        s.output_cursor += 1;
    }
    assert!(s.output_cursor > 0);
    let text = encode_checkpoint(&id, &h, &s, false).unwrap();
    let stale = text.replace(
        &format!("output_cursor={}", s.output_cursor),
        "output_cursor=0",
    );
    assert!(decode_checkpoint(&stale, &id, &h).is_err());
}
