import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from mcp_utils import add_numbers, run_cmd, coverage_analyzer
import mcp_utils


def test_add_numbers():
    assert add_numbers(1, 1) == 2
    assert add_numbers(-3, 5) == 2


def test_run_cmd_monkeypatch(monkeypatch):
    class DummyResult:
        def __init__(self, stdout, stderr, returncode=0):
            self.stdout = stdout
            self.stderr = stderr
            self.returncode = returncode

    def fake_run(cmd, capture_output, text):
        assert cmd == ["echo", "hello"]
        return DummyResult("hello\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    out, err, code = run_cmd(["echo", "hello"])
    assert out == "hello"
    assert err == ""
    assert code == 0


def test_coverage_analyzer_tmpfile(tmp_path):
    # craft a small jacoco-like XML with one covered and one uncovered method
    root = ET.Element("report")
    root.set("missed-instructions", "10")
    root.set("covered-instructions", "90")

    pkg = ET.SubElement(root, "package")
    pkg.set("name", "com.example")

    cls = ET.SubElement(pkg, "class")
    cls.set("name", "MyClass")

    m1 = ET.SubElement(cls, "method")
    m1.set("name", "coveredMethod")
    m1.set("desc", "()V")
    m1.set("ci", "10")
    m1.set("line", "10")

    m2 = ET.SubElement(cls, "method")
    m2.set("name", "uncoveredMethod")
    m2.set("desc", "()V")
    m2.set("ci", "0")
    m2.set("line", "20")

    xml_path = tmp_path / "jacoco.xml"
    tree = ET.ElementTree(root)
    tree.write(xml_path)

    res = coverage_analyzer(str(xml_path))
    assert "coverage_pct" in res
    assert res["coverage_pct"] == pytest.approx(90.0, rel=1e-3)
    assert res["total_uncovered"] == 1


def test_test_generator_creates_file(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    java_file = src / "Hello.java"
    java_file.write_text("public class Hello { public int add(int a,int b){return a+b;} }")

    out_dir = tmp_path / "tests"
    res = mcp_utils.test_generator(source_dir=str(src), output_dir=str(out_dir))
    generated = res.get("generated_tests", [])
    assert len(generated) == 1
    gen_path = Path(generated[0])
    assert gen_path.exists()
    content = gen_path.read_text()
    assert "public class HelloTest" in content
