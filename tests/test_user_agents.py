from vinted_api_kit.client.user_agents import USER_AGENTS, get_random_user_agent


def test_random_user_agent_returns_know_value():
    ua = get_random_user_agent()

    assert isinstance(ua, str)
    assert ua in USER_AGENTS


def test_user_agents_not_empty():
    assert len(USER_AGENTS) > 0
