import io
import json
import queue
import urllib.request

import pytest

import update_check

REPO = "Rouzax/example-plugin"


def release(tag, prerelease=False, draft=False, url=None):
    page = url if url is not None else f"https://github.com/{REPO}/releases/tag/{tag}"
    return {"tag_name": tag, "prerelease": prerelease, "draft": draft, "html_url": page}


def test_versions_sort_like_semantic_versioning():
    ordered = [
        "0.1.0-alpha",
        "0.1.0-beta.2",
        "0.1.0-beta.10",
        "0.1.0-rc.1",
        "0.1.0",
        "v0.1.1",
        "0.2.0",
        "1.0.0",
    ]
    keys = [update_check.version_key(v) for v in ordered]
    assert None not in keys
    assert keys == sorted(keys)  # type: ignore[type-var]
    # Fewer identifiers sort first when the rest is equal.
    assert update_check.version_key("0.1.0-beta") < update_check.version_key("0.1.0-beta.1")  # type: ignore[operator]
    for bad in ("", "latest", "1.2", "1.2.3.4", "v1.x.0", "1.2.3-"):
        assert update_check.version_key(bad) is None, bad


def test_auto_follows_the_running_version_and_stable_skips_betas():
    releases = [release("v0.2.0-beta.1", prerelease=True), release("v0.1.1"), release("v0.1.0")]
    beta = update_check.newest(releases, "0.1.0-beta.4", "auto", REPO)
    assert beta == ("0.2.0-beta.1", f"https://github.com/{REPO}/releases/tag/v0.2.0-beta.1")
    assert update_check.newest(releases, "0.1.0", "auto", REPO)[0] == "0.1.1"  # type: ignore[index]
    assert update_check.newest(releases, "0.1.0-beta.4", "stable", REPO)[0] == "0.1.1"  # type: ignore[index]
    assert update_check.newest(releases, "0.1.0", "beta", REPO)[0] == "0.2.0-beta.1"  # type: ignore[index]
    assert update_check.newest(releases, "0.1.0", "off", REPO) is None
    assert update_check.newest(releases, "0.1.0", "nightly", REPO) is None


def test_nothing_newer_drafts_and_junk_report_nothing():
    junk = [release("v9.0.0", draft=True), release("latest"), {"tag_name": 5}, "x", None]
    assert update_check.newest([*junk, release("v0.1.0")], "0.1.0", "beta", REPO) is None
    assert update_check.newest({"message": "rate limited"}, "0.1.0", "beta", REPO) is None
    assert update_check.newest([release("v1.0.0")], "not a version", "beta", REPO) is None


def test_a_tag_named_like_a_beta_counts_as_one_even_when_not_marked():
    unmarked = [release("v0.2.0-beta.1", prerelease=False)]
    assert update_check.newest(unmarked, "0.1.0", "stable", REPO) is None


def test_a_link_outside_the_repository_is_replaced_by_its_releases_page():
    found = update_check.newest(
        [release("v1.0.0", url="https://evil.example/x")], "0.1.0", "stable", REPO
    )
    assert found == ("1.0.0", f"https://github.com/{REPO}/releases")
    other = update_check.newest(
        [release("v1.0.0", url="https://github.com/someone/else/releases")],
        "0.1.0",
        "stable",
        REPO,
    )
    assert other == ("1.0.0", f"https://github.com/{REPO}/releases")


def checker(fetch, **kw):
    results = queue.Queue()
    base = dict(user_agent="test", first_delay_s=0.0, interval_s=3600.0, fetch=fetch)
    base.update(kw)
    return update_check.UpdateChecker(REPO, "0.1.0", "stable", results, **base), results


def test_a_check_reports_the_newer_release_or_none_and_never_raises():
    found, _ = checker(lambda *_: [release("v0.2.0")])
    assert found.check_once() == update_check.UpdateResult(
        "0.2.0", f"https://github.com/{REPO}/releases/tag/v0.2.0"
    )
    current, _ = checker(lambda *_: [release("v0.1.0")])
    assert current.check_once() == update_check.UpdateResult(None)

    def offline(*_):
        raise OSError("no route")

    failing, _ = checker(offline)
    assert failing.check_once() == update_check.UpdateResult(None, error="OSError")


def test_the_thread_checks_after_its_delay_and_stops_on_request():
    seen = []

    def fetch(repo, user_agent):
        seen.append((repo, user_agent))
        return [release("v0.3.0")]

    thread, results = checker(fetch)
    thread.start()
    result = results.get(timeout=5)
    thread.stop()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert result.version == "0.3.0" and seen == [(REPO, "test")]


def test_a_stop_before_the_first_check_sends_nothing():
    thread, results = checker(lambda *_: [release("v0.3.0")], first_delay_s=60.0)
    thread.start()
    thread.stop()
    thread.join(timeout=5)
    assert results.empty()


def test_only_an_owner_and_name_repository_is_accepted():
    with pytest.raises(ValueError):
        update_check.UpdateChecker(
            "https://github.com/x/y", "0.1.0", "auto", queue.Queue(), user_agent="t"
        )


def test_fetch_asks_github_for_the_releases_and_bounds_the_answer(monkeypatch):
    asked = {}

    class Answer(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def urlopen(request, timeout, context):
        asked.update(url=request.full_url, ua=request.get_header("User-agent"), timeout=timeout)
        return Answer(json.dumps([release("v0.2.0")]).encode())

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert update_check.fetch_releases(REPO, "plugin-check")[0]["tag_name"] == "v0.2.0"
    assert asked == {
        "url": f"https://api.github.com/repos/{REPO}/releases?per_page=30",
        "ua": "plugin-check",
        "timeout": update_check.TIMEOUT_S,
    }
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda request, timeout, context: Answer(b" " * (update_check.MAX_BODY + 1)),
    )
    with pytest.raises(ValueError):
        update_check.fetch_releases(REPO, "plugin-check")
