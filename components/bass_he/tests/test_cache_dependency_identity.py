import importlib.util
from pathlib import Path


def runner():
    path=Path(__file__).resolve().parents[1]/'scripts'/'run_research.py'
    spec=importlib.util.spec_from_file_location('run_research_dep',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def test_scientific_cache_dependencies_are_granular():
    m=runner()
    ep=set(m.source_dependencies('ep'))
    geom=set(m.source_dependencies('geometry'))
    assert 'src/bass_he/spectral.py' in ep
    assert 'src/bass_he/rotation.py' not in ep
    assert 'src/bass_he/geometry.py' in geom
    assert 'src/bass_he/rotation.py' not in geom
    assert 'src/bass_he/transport.py' not in geom
    assert m.dependency_source_identity('ep') != m.dependency_source_identity('geometry')
