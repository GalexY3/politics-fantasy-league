from politics_fantasy.source_eligibility import policy_status

def test_public_policy_lists_unattested_privacy_work_without_granting_release():
    status = policy_status()
    assert "lawful purpose and processing basis review" in status["requires"]
    assert "privacy risk and EIPD screening" in status["requires"]
    assert status["release_ready"] is False
    assert status["real_person_scoring"] is False
