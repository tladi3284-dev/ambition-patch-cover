import pytest

from NOBU_ToolHub.launcher.config_manager import ConfigManager
from NOBU_ToolHub.launcher.version_resolver import (
    AmbiguousVersionError,
    UnknownSeriesError,
    VersionResolver,
)


def _resolver(tmp_path):
    config = ConfigManager(config_path=tmp_path / "toolhub_config.json")
    return VersionResolver(config), config


def test_variants_for_series_returns_both_nobu14_editions(tmp_path):
    resolver, _ = _resolver(tmp_path)
    variants = resolver.variants_for_series("NOBU14")
    assert {v.key for v in variants} == {
        "NOBU14_SPHERE_OF_INFLUENCE",
        "NOBU14_SPHERE_OF_INFLUENCE_ASCENSION",
    }


def test_variants_for_unknown_series_raises(tmp_path):
    resolver, _ = _resolver(tmp_path)
    with pytest.raises(UnknownSeriesError):
        resolver.variants_for_series("NOBU99")


def test_resolve_returns_none_when_nothing_configured(tmp_path):
    resolver, _ = _resolver(tmp_path)
    assert resolver.resolve("NOBU14") is None


def test_resolve_returns_single_configured_variant(tmp_path):
    resolver, config = _resolver(tmp_path)
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE", tmp_path / "souzou")

    resolved = resolver.resolve("NOBU14")

    assert resolved.key == "NOBU14_SPHERE_OF_INFLUENCE"
    assert resolved.path == tmp_path / "souzou"


def test_resolve_raises_when_ambiguous_without_prefer_key(tmp_path):
    resolver, config = _resolver(tmp_path)
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE", tmp_path / "souzou")
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE_ASCENSION", tmp_path / "ascension")

    with pytest.raises(AmbiguousVersionError):
        resolver.resolve("NOBU14")


def test_resolve_uses_prefer_key_to_disambiguate(tmp_path):
    resolver, config = _resolver(tmp_path)
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE", tmp_path / "souzou")
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE_ASCENSION", tmp_path / "ascension")

    resolved = resolver.resolve("NOBU14", prefer_key="NOBU14_SPHERE_OF_INFLUENCE_ASCENSION")

    assert resolved.key == "NOBU14_SPHERE_OF_INFLUENCE_ASCENSION"


def test_resolve_prefer_key_not_configured_raises(tmp_path):
    resolver, config = _resolver(tmp_path)
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE", tmp_path / "souzou")
    config.set_game_path("NOBU14_SPHERE_OF_INFLUENCE_ASCENSION", tmp_path / "ascension")

    with pytest.raises(UnknownSeriesError):
        resolver.resolve("NOBU14", prefer_key="NOT_A_VARIANT")
