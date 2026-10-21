"""Failure-only instrumentation of the exact frozen task transport copy."""
import hashlib


ORIGINAL_BLOB = '9915d05a00f9c2ad9e0346a1e61ba1d2f37822d3'
ANCHOR = b'        return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));'
INJECTION = r'''
        static REI_MOMENT_REPORTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
        if !REI_MOMENT_REPORTED.swap(true, std::sync::atomic::Ordering::Relaxed) {
            let (diagnostic_weights, diagnostic_mean, diagnostic_variance) = eval(lambda);
            let diagnostic_nodes = base.iter().zip(diagnostic_weights.iter()).zip(result.iter())
                .map(|((&(q, _), w), &(_, number))| format!("[{:.17e},{:.17e},{:.17e}]", q, w / norm, number))
                .collect::<Vec<_>>().join(",");
            let diagnostic_zero = diagnostic_weights.iter().zip(result.iter())
                .filter(|(w, (_, number))| **w > 0.0 && *number == 0.0).count();
            let diagnostic_subnormal = result.iter().filter(|(_, number)| number.is_subnormal()).count();
            eprintln!("REI_MOMENT_DIAGNOSTIC {{\"lo\":{:.17e},\"hi\":{:.17e},\"n\":{:.17e},\"u\":{:.17e},\"r\":{:.17e},\"mean\":{:.17e},\"gap\":{:.17e},\"beta\":{:.17e},\"lambda\":{:.17e},\"normalized_mean_residual\":{:.17e},\"variance\":{:.17e},\"count_defect\":{:.17e},\"count_tolerance\":{:.17e},\"energy_defect\":{:.17e},\"energy_tolerance\":{:.17e},\"energy_scale\":{:.17e},\"node_lo\":{:.17e},\"node_hi\":{:.17e},\"node_count\":{},\"positive_to_zero_nodes\":{},\"subnormal_nodes\":{},\"nodes_q_probability_number\":[{}]}}", lo, hi, n, u, r, mean, gap, beta, lambda, diagnostic_mean, diagnostic_variance, count_defect, 64.0 * f64::EPSILON * n, energy_defect, 128.0 * f64::EPSILON * energy_scale, energy_scale, node_lo, node_hi, result.len(), diagnostic_zero, diagnostic_subnormal, diagnostic_nodes);
        }
'''.encode()


def diagnostic_identity():
    return hashlib.sha256(INJECTION).hexdigest()


def instrument(original: bytes) -> bytes:
    blob=hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()
    if blob != ORIGINAL_BLOB or original.count(ANCHOR) != 1:
        raise ValueError('MOMENT_DIAGNOSTIC_ORIGINAL_IDENTITY_MISMATCH')
    return original.replace(ANCHOR, INJECTION+ANCHOR, 1)
