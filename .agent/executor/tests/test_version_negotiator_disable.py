from sovereignai.shared.config import Config


def test_config_default_version_negotiation_enabled():
    config = Config()
    assert config.version_negotiation_enabled is True


def test_config_version_negotiation_disabled():
    config = Config(version_negotiation_enabled=False)
    assert config.version_negotiation_enabled is False


def test_config_version_negotiation_enabled_explicit():
    config = Config(version_negotiation_enabled=True)
    assert config.version_negotiation_enabled is True
