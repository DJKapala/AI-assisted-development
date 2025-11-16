import subprocess
from pathlib import Path

import pytest

import server


def test_git_status_clean(monkeypatch):
    monkeypatch.setattr(server, "run_cmd", lambda cmd: ("", "", 0))
    res = server.git_status()
    assert res["clean"] is True
    assert res["staged"] == []
    assert res["unstaged"] == []
    assert res["conflicts"] == []


def test_git_status_mixed(monkeypatch):
    out = "A  file1\n M file2\nUU file3"
    monkeypatch.setattr(server, "run_cmd", lambda cmd: (out, "", 0))
    res = server.git_status()
    assert res["staged"] == ["file1"]
    assert res["unstaged"] == ["file2"]
    assert res["conflicts"] == ["file3"]


def test_git_add_all(monkeypatch):
    responses = [("", "", 0), ("file1\nfile2", "", 0)]

    def fake(cmd):
        return responses.pop(0)

    monkeypatch.setattr(server, "run_cmd", fake)
    res = server.git_add_all()
    assert res["staged_files"] == ["file1", "file2"]


def test_git_commit(monkeypatch):
    def fake(cmd):
        return ("commit-ok", "", 0)

    monkeypatch.setattr(server, "run_cmd", fake)
    out = server.git_commit("my message", coverage=55.5, tests_added=3)
    assert "Coverage: 55.5" in out["commit_message"]
    assert "Tests Added: 3" in out["commit_message"]
    assert out["stdout"] == "commit-ok"


def test_git_push_and_protected(monkeypatch):
    # first simulate feature branch push
    responses = [("feature\n", "", 0), ("pushed", "", 0)]

    def fake(cmd):
        return responses.pop(0)

    monkeypatch.setattr(server, "run_cmd", fake)
    res = server.git_push()
    assert res["branch"] == "feature"
    assert res["stdout"] == "pushed"

    # now simulate protected branch
    monkeypatch.setattr(server, "run_cmd", lambda cmd: ("main\n", "", 0))
    res2 = server.git_push()
    assert "error" in res2


def test_git_pull_request(monkeypatch):
    class Dummy:
        def __init__(self):
            self.stdout = "https://example/pr/1\n"
            self.stderr = ""
            self.returncode = 0

    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Dummy())
    res = server.git_pull_request(title="T", body="B")
    assert "https://example/pr/1" in res["pull_request_url"]


def test_test_execution(monkeypatch):
    monkeypatch.setattr(server, "run_cmd", lambda cmd: ("mvn out", "", 0))
    res = server.test_execution()
    assert "maven_output" in res
    assert res["maven_output"] == "mvn out"
