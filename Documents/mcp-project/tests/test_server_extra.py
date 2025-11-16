import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import server


def test_mcp_tool_is_noop_when_fastmcp_missing():
    # In test env we didn't install fastmcp, so mcp should be None and
    # mcp_tool should be a decorator that returns the original function.
    assert getattr(server, "mcp") is None

    def fn(a, b):
        return a + b

    decorated = server.mcp_tool()(fn)
    assert callable(decorated)
    assert decorated is fn
    assert decorated(2, 3) == 5


def test_server_coverage_analyzer_via_server(tmp_path):
    # reuse the same small jacoco-like xml as in mcp_utils tests
    root = ET.Element("report")
    root.set("missed-instructions", "1")
    root.set("covered-instructions", "9")

    pkg = ET.SubElement(root, "package")
    pkg.set("name", "com.example")

    cls = ET.SubElement(pkg, "class")
    cls.set("name", "X")

    m = ET.SubElement(cls, "method")
    m.set("name", "m")
    m.set("desc", "()V")
    m.set("ci", "9")
    m.set("line", "1")

    xml_path = tmp_path / "c.xml"
    ET.ElementTree(root).write(xml_path)

    res = server.coverage_analyzer(str(xml_path))
    assert res["coverage_pct"] == pytest.approx(90.0, rel=1e-3)


def test_server_test_generator_via_server(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    java_file = src / "C.java"
    java_file.write_text("public class C { public void x(){} }")

    out_dir = tmp_path / "out"
    res = server.test_generator(source_dir=str(src), output_dir=str(out_dir))
    generated = res.get("generated_tests", [])
    assert len(generated) == 1
    p = Path(generated[0])
    assert p.exists()
