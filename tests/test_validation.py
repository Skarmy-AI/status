import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_upptimerc_schema(upptimerc):
    assert upptimerc.get("owner")
    assert upptimerc.get("repo")
    assert isinstance(upptimerc["sites"], list) and upptimerc["sites"]
    for site in upptimerc["sites"]:
        assert site.get("name")
        assert site.get("url", "").startswith("https://")
    assert isinstance(upptimerc.get("status-website"), dict)


def test_summary_matches_config(upptimerc, history_summary):
    configured = {site["name"] for site in upptimerc["sites"]}
    summarized = {entry["name"] for entry in history_summary}
    assert configured == summarized


def test_summary_schema(history_summary):
    assert isinstance(history_summary, list) and history_summary
    statuses = {"up", "down", "degraded"}
    for entry in history_summary:
        assert entry["name"]
        assert entry["url"].startswith("https://")
        assert entry["slug"]
        assert entry["status"] in statuses
        assert isinstance(entry["time"], int)
        assert isinstance(entry["dailyMinutesDown"], dict)


def test_history_files_match_summary(history_summary):
    for entry in history_summary:
        path = REPO_ROOT / "history" / f"{entry['slug']}.yml"
        assert path.is_file(), f"missing history file for {entry['slug']}"
        data = yaml.safe_load(path.read_text())
        assert data["url"] == entry["url"]
        assert data["status"] in {"up", "down", "degraded"}
        assert isinstance(data["code"], int)
        assert isinstance(data["responseTime"], int)
        assert data["lastUpdated"]
        assert data["startTime"]
        assert "Upptime" in data["generator"]


def test_api_badges_for_each_site(history_summary):
    for entry in history_summary:
        api_dir = REPO_ROOT / "api" / entry["slug"]
        assert api_dir.is_dir(), f"missing api dir for {entry['slug']}"

        suffix_label = {"": "", "-day": " 24h", "-week": " 7d", "-month": " 30d", "-year": " 1y"}
        for suffix in ("", "-day", "-week", "-month", "-year"):
            for metric in ("uptime", "response-time"):
                path = api_dir / f"{metric}{suffix}.json"
                assert path.is_file(), f"missing {path}"
                data = json.loads(path.read_text())
                assert data["schemaVersion"] == 1
                expected_label = (metric.replace("-", " ") + suffix_label[suffix]).strip()
                assert data["label"].lower() == expected_label
                assert "message" in data
                assert "color" in data


def test_github_workflows_are_valid_yaml():
    for workflow in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
        data = yaml.safe_load(workflow.read_text())
        assert data is not None
        assert "name" in data
        assert "jobs" in data
