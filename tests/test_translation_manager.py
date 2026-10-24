import pytest

from translation_manager import TranslationManager
from translations import Language


@pytest.mark.parametrize(
    "code, language",
    [
        ("en", Language.ENGLISH),
        ("pl", Language.POLISH),
        ("nl", Language.DUTCH),
        ("de", Language.GERMAN),
        ("fr", Language.FRENCH),
    ],
)
def test_set_language_by_code(code, language):
    tm = TranslationManager()
    tm.set_language(code)
    assert tm._current_language is language


def test_unknown_code_falls_back_to_english():
    tm = TranslationManager()
    tm.set_language("9")
    assert tm._current_language is Language.ENGLISH


def test_every_device_text_exists_in_every_language():
    from translations import DEVICE_TRANSLATIONS

    missing = [
        f"{spec_id}.{kind}: {sorted(lang.name for lang in set(Language) - set(texts))}"
        for spec_id, kinds in DEVICE_TRANSLATIONS.items()
        for kind, texts in kinds.items()
        if set(texts) != set(Language)
    ]
    assert missing == []


def test_every_translation_belongs_to_a_device():
    from device_specs_table import build_device_specs
    from translations import DEVICE_TRANSLATIONS

    live = {spec.spec_id for spec in build_device_specs()}
    # Old spec ids stay so names written under them are still recognised and renamed.
    renamed = set(TranslationManager._RENAMED_SPECS.values())
    assert set(DEVICE_TRANSLATIONS) - live - renamed == set()
    assert live - set(DEVICE_TRANSLATIONS) == set()
