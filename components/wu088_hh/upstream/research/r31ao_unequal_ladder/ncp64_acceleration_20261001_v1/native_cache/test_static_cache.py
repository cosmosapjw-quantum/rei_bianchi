"""Static/exact-model checks only. Passing is not native Arb equivalence."""
from fractions import Fraction as Q
from pathlib import Path
import json
import re
import tempfile
import unittest
from unittest.mock import patch
import verify_inputs

HERE = Path(__file__).resolve().parent
OLD = HERE.parent.parent/'gap_closure_20261001_g0_g6_v1/validated_callback'


def quantize(interval, bits=7):
    scale = 1 << bits
    lo, hi = interval
    return Q((lo*scale).__floor__(), scale), Q((hi*scale).__ceil__(), scale)


def add(a, b):
    return quantize((a[0]+b[0], a[1]+b[1]))


def multiply(a, b):
    products = [x*y for x in a for y in b]
    return quantize((min(products), max(products)))


def expression_model(cached):
    slots = [{}, {}, {}]
    counts = [0, 0, 0]
    def helper(which, degree):
        if not cached or degree not in slots[which]:
            counts[which] += 1
            value = quantize((Q((which+1)*(degree-3), 17), Q((which+1)*(degree-3), 17)+Q(1, 53)))
            slots[which][degree] = value
        return slots[which][degree]
    total = (Q(0), Q(0))
    trace = []
    for n in range(107):
        coefficient = Q((-1)**n*(n%7+1), n%5+2)
        value = multiply(multiply(multiply((coefficient, coefficient), helper(0, n%9)),
                                  helper(1, (n//9)%9)), helper(2, (5*n+3)%9))
        total = add(total, value)
        trace.append((value, total))
    return total, trace, counts


class CacheStaticTests(unittest.TestCase):
    def test_imports_exact_original_helpers_once(self):
        src = (HERE/'cached_callback.cpp').read_text()
        self.assertEqual(src.count('#include "../../gap_closure_20261001_g0_g6_v1/validated_callback/callback.cpp"'), 1)
        self.assertNotIn('Ball density(', src)
        self.assertNotIn('Ball spatial(', src)
        script = (HERE/'build_host.sh').read_text()
        self.assertNotRegex(script, r'"\$script_dir/[^"\n]*callback\.cpp"[^\n]*"[^\n]*callback\.cpp"')

    def test_term_expression_and_sum_tree_preserved(self):
        original = (OLD/'callback.cpp').read_text().split('int polynomial_field(', 1)[1]
        candidate = (HERE/'cached_callback.cpp').read_text()
        before = re.search(r'Ball value=Ball\(c.precision,term.coefficient\)(.*?);', original, re.S).group(0)
        before = before.replace('density(term.i,bt,par.mu,c.margin)', 'get_left(term.i)')
        before = before.replace('density(term.j,bu,par.mu,c.margin)', 'get_right(term.j)')
        before = before.replace('spatial(term.k,ell,field,bt,bu,par,c.margin)', 'get_spatial(term.k)')
        after = re.search(r'Ball value=Ball\(c.precision,term.coefficient\)(.*?);', candidate, re.S).group(0)
        self.assertEqual(re.sub(r'\s+', '', before), re.sub(r'\s+', '', after))
        self.assertIn('sum=sum+value;', candidate)
        self.assertIn('for (const auto &term:terms)', candidate)

    def test_cache_is_local_full_box_and_precision_preserved(self):
        src = (HERE/'cached_callback.cpp').read_text()
        self.assertIn('std::array<std::optional<Ball>,9> left{},right{},space{};', src)
        self.assertNotRegex(src, r'\bstatic\s+')
        self.assertIn('Ball bt(c.precision,t,true),bu(c.precision,u,true)', src)
        self.assertNotIn('get_mid', src)
        self.assertNotIn('midref', src)
        self.assertIn('stats=CacheStats{};', src)

    def test_exact_rounded_expression_model_and_counts(self):
        baseline = expression_model(False)
        cached = expression_model(True)
        self.assertEqual(baseline[:2], cached[:2])
        self.assertEqual(baseline[2], [107, 107, 107])
        self.assertEqual(cached[2], [9, 9, 9])

    def test_reassociation_can_change_outward_interval(self):
        a, b, c = ((Q(1, 9), Q(1, 9)), (Q(1, 9), Q(1, 9)), (Q(4, 7), Q(4, 7)))
        self.assertNotEqual(multiply(multiply(a, b), c), multiply(a, multiply(b, c)))

    def test_cache_invalid_degree_uses_original_failure_path(self):
        src = (HERE/'cached_callback.cpp').read_text()
        self.assertIn('(void)density(i,bt,par.mu,c.margin)', src)
        self.assertIn('(void)density(j,bu,par.mu,c.margin)', src)
        self.assertIn('(void)spatial(k,ell,field,bt,bu,par,c.margin)', src)
        self.assertIn('check(c);', src)
        self.assertIn('invalidate_requested_coefficients(out,order)', src)

    def test_native_fixture_requires_exact_equality_and_dump(self):
        src = (HERE/'native_cache_synthetic.cpp').read_text()
        self.assertIn('acb_equal(baseline,cached)', src)
        self.assertIn('dump(baseline)==dump(cached)', src)
        self.assertNotIn('acb_overlaps', src)
        self.assertIn('arb_dump_str(x)', src)
        self.assertIn('O_WRONLY|O_CREAT|O_EXCL', src)
        self.assertIn('flint_set_num_threads(1)', src)
        self.assertIn('flint_get_num_threads()==1', src)
        self.assertIn('same(first_value.v,cached.v,true)', src)
        for case in ('point107', 'complex_point107', 'complex_box107', 'errors'):
            self.assertIn('"'+case+'"', src)

    def test_build_flags_and_compile_only_contract(self):
        src = (HERE/'build_host.sh').read_text()
        for flag in ('-fno-fast-math', '-fno-associative-math', '-fno-unsafe-math-optimizations', '-ffp-contract=off'):
            self.assertIn(flag, src)
        self.assertNotRegex(src, r'(^|\s)-(?:ffast-math|Ofast)(\s|$)')
        self.assertIn('Native equality and benchmark have NOT run.', src)
        self.assertIn('--ldd-report', src)

    def test_source_lock_exact_dependencies(self):
        checked = verify_inputs.verify_sources()
        self.assertEqual(len(checked), 8)

    def test_incomplete_lock_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path/'SOURCE_LOCK.json').write_text(json.dumps({'schema': 'WU088_NATIVE_CACHE_SOURCE_LOCK_V1', 'files': []}))
            with patch.object(verify_inputs, 'HERE', path), self.assertRaises(ValueError):
                verify_inputs.verify_sources()


if __name__ == '__main__':
    unittest.main(verbosity=2)
