"""Plugin-side glue for the shared update check: persisted state, announcing, lifecycle."""

import domoticz_stub as stub
import pytest

import plugin
import update_check
from update_check import UpdateResult


@pytest.fixture
def lux():
    stub.reset()
    p = plugin.LuxtronikPlugin()
    p._plugin_version = "2.3.0"
    return p


def test_load_state_without_blob_is_migrating(lux):
    lux._load_state()
    assert lux._migrating is True
    assert lux._names_persisted is False
    assert lux._update_notified is None


def test_load_state_with_only_update_notified_stays_migrating(lux):
    stub.Configuration({"v": 1, "update_notified": "2.4.0"})
    lux._load_state()
    assert lux._migrating is True
    assert lux._update_notified == "2.4.0"


def test_load_state_with_auto_names_is_not_migrating(lux):
    stub.Configuration({"v": 1, "auto_names": {"d:1": {"name": "N"}}})
    lux._load_state()
    assert lux._migrating is False
    assert lux._auto_names == {"d:1": {"name": "N"}}


def test_persist_omits_auto_names_until_something_was_claimed(lux):
    lux._update_notified = "2.4.0"
    lux._persist()
    assert stub.Configuration() == {"v": 1, "update_notified": "2.4.0"}


def test_persist_merges_names_and_update_notified(lux):
    stub.Configuration({"v": 1, "auto_names": {"d:1": {"name": "N"}}})
    lux._load_state()
    lux._update_notified = "2.4.0"
    lux._persist()
    assert stub.Configuration() == {
        "v": 1,
        "auto_names": {"d:1": {"name": "N"}},
        "update_notified": "2.4.0",
    }


def test_announce_once_per_version(lux):
    url = "https://github.com/Rouzax/luxtronik-domoticz-plugin-v2/releases/tag/v2.4.0"
    lux._updates.put(UpdateResult("2.4.0", url))
    lux._announce_updates()
    assert len(stub.calls["notification"]) == 1
    subject, body = stub.calls["notification"][0][:2]
    assert "2.4.0" in subject
    assert url in body and "2.3.0" in body
    assert any("2.4.0" in m and url in m for m in stub.calls["status"])
    assert stub.Configuration()["update_notified"] == "2.4.0"

    lux._updates.put(UpdateResult("2.4.0", url))
    lux._announce_updates()
    assert len(stub.calls["notification"]) == 1


def test_announce_skips_errors_and_up_to_date(lux):
    lux._updates.put(UpdateResult(None, error="URLError"))
    lux._updates.put(UpdateResult(None))
    lux._announce_updates()
    assert stub.calls["notification"] == []
    assert stub.Configuration() == {}


def test_announce_failure_does_not_skip_update_all(lux, monkeypatch):
    def boom():
        raise RuntimeError("announce boom")

    polled = []
    monkeypatch.setattr(lux, "_announce_updates", boom)
    monkeypatch.setattr(lux, "update_all", lambda: polled.append(True))
    lux.onHeartbeat()
    assert polled == [True]
    assert any("announce boom" in m for m in stub.calls["error"])


class _FakeChecker:
    def __init__(self, repo, current, channel, results, *, user_agent):
        self.args = (repo, current, channel, results, user_agent)
        self.started = self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


def test_start_update_check_starts_checker(lux, monkeypatch):
    monkeypatch.setattr(update_check, "UpdateChecker", _FakeChecker)
    lux._start_update_check("auto")
    assert isinstance(lux._checker, _FakeChecker)
    assert lux._checker.started
    assert lux._checker.args[:3] == (plugin.REPOSITORY, "2.3.0", "auto")
    assert lux._checker.args[4] == "luxtronikex/2.3.0 update-check"


@pytest.mark.parametrize("channel, version", [("off", "2.3.0"), ("auto", "")])
def test_start_update_check_skipped(lux, monkeypatch, channel, version):
    monkeypatch.setattr(update_check, "UpdateChecker", _FakeChecker)
    lux._plugin_version = version
    lux._start_update_check(channel)
    assert lux._checker is None


def test_on_stop_stops_checker(lux, monkeypatch):
    monkeypatch.setattr(update_check, "UpdateChecker", _FakeChecker)
    lux._start_update_check("stable")
    checker = lux._checker
    lux.onStop()
    assert checker.stopped
    assert lux._checker is None


def test_repository_is_a_valid_owner_name():
    # UpdateChecker refuses anything else, which would silently disable the check.
    update_check.UpdateChecker(plugin.REPOSITORY, "2.3.0", "auto", None, user_agent="t")


def test_pump_compensation_from_separate_values(lux):
    lux._configure_pump_compensation(True, ("2", "60", " 3", "140"))
    assert lux._pump_power_ranges == {
        "hup_min": 2.0,
        "hup_max": 60.0,
        "vbo_min": 3.0,
        "vbo_max": 140.0,
    }


def test_pump_compensation_rejects_wrong_count(lux):
    lux._configure_pump_compensation(True, ("2", "60", "3"))
    assert lux._pump_compensation_enabled is False
    assert any("2,60,3" in m for m in stub.calls["error"])


def test_pump_compensation_names_the_pump_when_min_above_max(lux):
    lux._configure_pump_compensation(True, ("2", "60", "200", "140"))
    assert lux._pump_compensation_enabled is False
    assert any("Brine pump min 200 W is above max 140 W" in m for m in stub.calls["error"])


def test_pump_compensation_names_a_field_that_is_not_a_number(lux):
    lux._configure_pump_compensation(True, ("2", "", "3", "140"))
    assert lux._pump_compensation_enabled is False
    assert any("Heating pump max '' is not a number" in m for m in stub.calls["error"])


def test_carry_over_notice_logged_every_start_notified_once(lux):
    lux._load_state()
    lux._announce_carry_over("Settings moved ...")
    assert stub.calls["status"] == ["Settings moved ..."]
    assert len(stub.calls["notification"]) == 1
    assert stub.Configuration() == {"v": 1, "settings_notice_sent": True}

    restarted = plugin.LuxtronikPlugin()
    restarted._load_state()
    restarted._announce_carry_over("Settings moved ...")
    assert stub.calls["status"] == ["Settings moved ..."] * 2
    assert len(stub.calls["notification"]) == 1
    # Notifying must not end the device-name migration bootstrap.
    assert restarted._migrating is True


def test_no_carry_over_announcement_for_named_settings(lux):
    lux._announce_carry_over(None)
    assert stub.calls["status"] == []
    assert stub.calls["notification"] == []
