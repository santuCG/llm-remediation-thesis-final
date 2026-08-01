import os
import yaml

def test_js08_profile_exists_and_valid():
    profile_path = "profiles/JS-08.yaml"
    assert os.path.exists(profile_path)
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
    assert profile["scenario_id"] == "JS-08"
    assert "expected" in profile
    assert profile["expected"]["strategy"] == "direct_upgrade"
