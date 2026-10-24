"""Tell a Domoticz plugin when GitHub has a newer release of it.

Self-contained, so the same file can be copied unchanged into any plugin: standard library only,
no Domoticz import and no import from the plugin. The plugin starts an UpdateChecker with its
repository and its own version; the checker's thread asks GitHub a few minutes after start and
then once a day, and puts an UpdateResult on a queue the plugin reads on its own thread (Domoticz
must only be called from there). What to do with a result, and remembering which version was
already reported, is up to the plugin.

update_check v2
"""

# Annotations stay strings, so the `X | None` unions also load on Python 3.9, the oldest floor
# among the plugins that copy this file.
from __future__ import annotations

import json
import queue
import re
import ssl
import threading
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

# auto: betas when the running version is a beta, else stable releases only.
CHANNELS = ("auto", "stable", "beta", "off")
FIRST_DELAY_S = 300.0
INTERVAL_S = 24 * 3600.0
TIMEOUT_S = 30.0
# The releases list is small; a larger answer is not GitHub's and is not parsed.
MAX_BODY = 1_000_000
_VERSION = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")

Key = tuple[tuple[int, ...], tuple]


@dataclass(frozen=True)
class UpdateResult:
    """One check. `version` is the newer release, or None when the running one is the newest;
    `url` is its release page. `error` names what went wrong (an exception type), else ""."""

    version: str | None
    url: str = ""
    error: str = ""


def version_key(text: str) -> Key | None:
    """A sortable key for a semantic version, or None. A pre-release sorts before its release
    (0.1.0-beta.4 < 0.1.0-beta.5 < 0.1.0), and numeric identifiers compare as numbers."""
    match = _VERSION.fullmatch(text.strip())
    if match is None:
        return None
    core = tuple(int(part) for part in match.group(1, 2, 3))
    pre = match.group(4)
    if pre is None:
        return core, (1,)
    # Semantic versioning: a numeric identifier sorts below an alphanumeric one.
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0, *parts)


def is_prerelease(key: Key) -> bool:
    return key[1][0] == 0


def newest(releases: object, current: str, channel: str, repo: str) -> tuple[str, str] | None:
    """(version, release page) of the newest release above `current` that `channel` allows, or
    None. Drafts and tags that are not a version are skipped; a release page that is not this
    repository's on GitHub is replaced by its releases page, so a notification never links
    elsewhere."""
    mine = version_key(current)
    if mine is None or channel not in CHANNELS or channel == "off":
        return None
    betas = channel == "beta" or (channel == "auto" and is_prerelease(mine))
    best: tuple[Key, str, str] | None = None
    for release in releases if isinstance(releases, list) else []:
        if not isinstance(release, dict) or release.get("draft"):
            continue
        tag = release.get("tag_name")
        key = version_key(tag) if isinstance(tag, str) else None
        if key is None or key <= mine:
            continue
        if (release.get("prerelease") or is_prerelease(key)) and not betas:
            continue
        if best is None or key > best[0]:
            page = release.get("html_url")
            if not isinstance(page, str) or not page.startswith(f"https://github.com/{repo}/"):
                page = f"https://github.com/{repo}/releases"
            assert isinstance(tag, str)
            best = (key, tag.strip().removeprefix("v"), page)
    return (best[1], best[2]) if best else None


def fetch_releases(repo: str, user_agent: str, timeout: float = TIMEOUT_S) -> object:
    """GitHub's list of the repository's releases, newest first, as parsed JSON."""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases?per_page=30",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": user_agent,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        body = response.read(MAX_BODY + 1)
    if len(body) > MAX_BODY:
        raise ValueError("releases answer too large")
    return json.loads(body)


class UpdateChecker(threading.Thread):
    """Checks `FIRST_DELAY_S` after start, then every `INTERVAL_S`, until stop(). A daemon
    thread, so a Domoticz that stops without calling stop() is never held up by it."""

    def __init__(
        self,
        repo: str,
        current: str,
        channel: str,
        results: queue.Queue[UpdateResult],
        *,
        user_agent: str,
        first_delay_s: float = FIRST_DELAY_S,
        interval_s: float = INTERVAL_S,
        fetch: Callable[[str, str], object] = fetch_releases,
    ) -> None:
        if not _REPO.fullmatch(repo):
            raise ValueError(f"not an owner/name repository: {repo!r}")
        super().__init__(name="update-check", daemon=True)
        self._repo, self._current, self._channel = repo, current, channel
        self._results, self._user_agent, self._fetch = results, user_agent, fetch
        self._first_delay_s, self._interval_s = first_delay_s, interval_s
        self._stopped = threading.Event()

    def stop(self) -> None:
        self._stopped.set()

    def run(self) -> None:
        delay = self._first_delay_s
        while not self._stopped.wait(delay):
            self._results.put_nowait(self.check_once())
            delay = self._interval_s

    def check_once(self) -> UpdateResult:
        try:
            releases = self._fetch(self._repo, self._user_agent)
        # Never let the thread die: a failed check is reported and the next one is a day later.
        except Exception as exc:  # noqa: BLE001
            return UpdateResult(None, error=type(exc).__name__)
        found = newest(releases, self._current, self._channel, self._repo)
        return UpdateResult(*found) if found else UpdateResult(None)
