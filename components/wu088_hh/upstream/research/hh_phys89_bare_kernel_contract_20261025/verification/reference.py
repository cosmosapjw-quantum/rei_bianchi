"""Independent Decimal/Fraction audit. Never imports production parser/kernel.

Shared evidence.py performs only metadata identity/serialization; all scientific
decoding and fixture arithmetic below are independently written.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'source'))
import json
from decimal import Decimal
from fractions import Fraction as R
from evidence import UNIT, REPO, encode, identity, main_args, publish, resume, sha


def parse_number(text):
    text = text.strip()
    if not text:
        raise ValueError('BLANK_FIELD')
    exponent = next((i for i in range(len(text)-1, 0, -1) if text[i] in '+-'), None)
    number = Decimal(text if exponent is None else text[:exponent]+'e'+text[exponent:])
    if not number.is_finite():
        raise ValueError('NONFINITE')
    return number


def independent_table(path):
    raw = path.read_bytes()
    if len(raw) != 671232 or sha(raw) != '3024d8f0db604b074e33ed8b05027eb9f5a738614041ba44c83f048e0d0bc1af':
        raise ValueError('INPUT_IDENTITY')
    selected = []
    for record in raw.decode('ascii').splitlines():
        if len(record) >= 75 and (int(record[66:70]), int(record[70:72]), int(record[72:75])) == (125, 33, 102):
            selected.append(record)
    controls = [[parse_number(s[i*11:(i+1)*11]) for i in range(6)] for s in selected[:3]]
    assert controls[0][5] == 1
    assert controls[1][2:] == [0, 102, 0, 1]
    assert controls[2][2:] == [1, 5, 11935, 154]
    tokens = [s[i*11:(i+1)*11] for s in selected[3:] for i in range(6)]
    values = [parse_number(t) for t in tokens[:11935]]
    assert len(values) == 11935
    assert all(parse_number(t) == 0 for t in tokens[11935:] if t.strip())
    edge = values[:154]
    packed = values[154:]
    assert len(edge) == 154 and len(packed) == 11781
    assert all(edge[i] < edge[i+1] for i in range(153))
    rows = []
    cursor = 0
    for i in range(153):
        upper = packed[cursor:cursor+153-i]
        cursor += 153-i
        rows.append([rows[j][i] for j in range(i)]+upper)
    assert cursor == 11781
    return edge, packed, rows, tokens[:11935]


def independent_fixture():
    weights = [R(2), R(3), R(5)]
    covariance = [[R(1,100), R(1,200), R(0)], [R(1,200), R(1,80), R(1,200)],
                  [R(0), R(1,200), R(1,80)]]
    energies, counts, caloric = [], [], []
    for kinetic, fraction in [(R(1), R(0)), (R(2), R(1,2)), (R(3), R(1))]:
        recoil = kinetic/2
        photon = 4+recoil
        energies.append([fraction*recoil-kinetic, recoil-fraction*recoil, R(-4), R(0), fraction*photon, photon-fraction*photon])
        counts.append({'thermal': fraction-2, 'fast': 1-fraction, 'electron': 0})
        caloric.append(3-kinetic+fraction*(recoil-R(3,2)))
    rewards = [[weights[g]*energies[g][a] for g in range(3)] for a in range(6)]
    z = sum(weights)
    means = [sum(row)/z for row in rewards]
    derivative = [[(rewards[a][g]-means[a]*weights[g])/z for g in range(3)] for a in range(6)]
    def bilinear(rows):
        out = []
        for left in rows:
            row = []
            for right in rows:
                value = R(0)
                for i in range(3):
                    for j in range(3):
                        value += left[i]*covariance[i][j]*right[j]
                row.append(value)
            out.append(row)
        return out
    statistics = {'Z': z, 'A': [sum(row) for row in rewards], 'M': means, 'B': derivative,
                  'linear_covariance': bilinear([weights]+rewards), 'delta_covariance': bilinear(derivative)}
    eta = [R(1,100), R(-1,200), R(1,300)]
    dz = sum(weights[g]*eta[g] for g in range(3))
    da = sum(rewards[0][g]*eta[g] for g in range(3))
    first = sum(derivative[0][g]*eta[g] for g in range(3))
    exact = (sum(rewards[0])+da)/(z+dz)-means[0]
    ratio = {'deltaZ': dz, 'deltaA': da, 'linear': first, 'exact': exact,
             'remainder': exact-first, 'bound': R(1,9)*abs(first)}
    clock = {'Y_proper': R(12,2000000), 'Y_coordinate': R(2,3)*R(12,2000000),
             'packet': R(60,2000000), 'energy_density_J_m3': R(7)*2000000*R('1.602176634e-19'),
             'density_m3': R(2000000)}
    assert all(sum(row) == 0 for row in energies)
    assert all(sum(row) == 0 for row in statistics['delta_covariance'])
    assert abs(ratio['remainder']) <= ratio['bound']
    return {'label': 'MANUFACTURED_NOT_SOURCE_OR_PHYSICAL_RATE', 'r': weights, 'F': covariance,
            'energy_per_event': energies, 'reward_rows': rewards, 'statistics': statistics,
            'counts': counts, 'caloric': caloric, 'ratio': ratio, 'clock': clock}


def run(primary_output):
    contract = json.loads((UNIT/'CONTRACT.json').read_text())
    edges, packed, matrix, tokens = independent_table(REPO/contract['source']['path'])
    raw = json.loads((primary_output/'SOURCE_TABLE.json').read_text())
    assert [R(x) for x in raw['boundaries']] == [R(x) for x in edges]
    assert [R(x) for x in raw['packed']] == [R(x) for x in packed]
    assert [[R(x) for x in row] for row in raw['matrix']] == [[R(x) for x in row] for row in matrix]
    assert raw['raw_tokens'] == tokens
    fixture = independent_fixture()
    observed = json.loads((primary_output/'FIXTURE.json').read_text())
    assert observed == encode(fixture)
    float_fixture = json.loads((primary_output/'FLOAT_FIXTURE.json').read_text())
    float_comparisons = 0
    def compare_float(observed, exact):
        nonlocal float_comparisons
        if isinstance(exact, dict):
            assert set(observed) == set(exact)
            for key in exact:
                compare_float(observed[key], exact[key])
        elif isinstance(exact, list):
            assert len(observed) == len(exact)
            for left, right in zip(observed, exact):
                compare_float(left, right)
        else:
            assert abs(R(observed)-exact) <= R('5e-15')+R('5e-13')*abs(exact)
            float_comparisons += 1
    compare_float(float_fixture, {'statistics': fixture['statistics'], 'capture_dotT': R(12)/(R(2)*R(3,2)+R(3)*R(3,2))})
    diag = json.loads((primary_output/'MATRIX_DIAGNOSTIC.json').read_text())
    witness = diag['exact_witness']
    check = 'NO_EXACT_WITNESS_REPORTED'
    if witness and witness['kind'] == 'EXACT_NEGATIVE_2X2_PRINCIPAL_MINOR':
        i, j = witness['indices']
        entries = [R(matrix[i][i]), R(matrix[i][j]), R(matrix[j][j])]
        determinant = entries[0]*entries[2]-entries[1]**2
        assert entries == [R(x) for x in witness['entries']]
        assert determinant == R(witness['determinant']) and determinant < 0
        check = 'EXACT_NEGATIVE_MINOR_CONFIRMED'
    elif witness and witness['kind'] in ('RATIONAL_QUADRATIC_WITNESS', 'RATIONALIZATION_NOT_NEGATIVE'):
        v = [R(x) for x in witness['vector']]
        assert len(v) == 153
        quadratic = sum((v[i]*R(matrix[i][j])*v[j] for i in range(153) for j in range(153)), R(0))
        assert quadratic == R(witness['quadratic'])
        if witness['kind'] == 'RATIONAL_QUADRATIC_WITNESS':
            assert quadratic < 0
        check = 'EXACT_QUADRATIC_RECALCULATED'
    return {'REFERENCE.json': {'status': 'PASS_EXACT', 'boundaries_compared': len(edges),
        'packed_tokens_compared': len(packed), 'matrix_entries_compared': 153*153,
        'all_raw_token_bytes_equal': True, 'fixture_all_exact_values_equal': True,
        'float_vs_exact_comparisons': float_comparisons,
        'witness_check': check, 'production_kernel_imports': 0, 'eigenvalue_calls': 0,
        'integrals': 0, 'old_science_calls': 0, 'strong_no_go': 'NOT_CLAIMED'},
        'INDEPENDENT_FIXTURE.json': fixture}


def main():
    args = main_args('reference')
    binding = identity()
    if args.resume:
        print(json.dumps(resume(args.output, 'reference', binding)))
        return
    if args.output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS_BEFORE_SCIENCE')
    # Verify complete primary payloads before any independent arithmetic.
    resume(args.primary_output, 'primary', binding)
    publish(args.output, 'reference', binding, run(args.primary_output))
    print(json.dumps({'status': 'COMPLETE', 'kind': 'reference', 'identity': binding['sha256']}))


if __name__ == '__main__':
    main()
