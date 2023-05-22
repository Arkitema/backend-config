from arkitema_config import config


def test_config(settings_env):
    settings = config.Settings()

    assert settings
    for env_key in settings_env.keys():
        assert hasattr(settings, env_key)
