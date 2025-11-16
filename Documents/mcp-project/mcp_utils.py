"""Pure-Python helper functions extracted from server.py to improve testability.
"""
import subprocess
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import re


def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


def run_cmd(cmd):
    """Run a shell command and return stdout, stderr, and return code.

    Args:
        cmd: list or str command to run.

    Returns:
        tuple(stdout:str, stderr:str, returncode:int)
    """
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def coverage_analyzer(xml_path: str = "target/site/jacoco/jacoco.xml") -> dict:
    if not os.path.exists(xml_path):
        return {"error": f"Coverage XML not found at {xml_path}"}

    tree = ET.parse(xml_path)
    root = tree.getroot()

    missed_instr = int(root.get("missed-instructions", 0))
    covered_instr = int(root.get("covered-instructions", 0))
    total_instr = missed_instr + covered_instr
    coverage_pct = round((covered_instr / total_instr * 100), 2) if total_instr > 0 else 0

    uncovered_methods = []
    for pkg in root.findall("package"):
        pkgname = pkg.get("name")
        for cls in pkg.findall("class"):
            classname = cls.get("name")
            for method in cls.findall("method"):
                if method.get("line") and int(method.get("ci", 0)) == 0:
                    uncovered_methods.append(f"{pkgname}.{classname}::{method.get('name')} {method.get('desc')}")

    return {"coverage_pct": coverage_pct, "uncovered_methods": uncovered_methods, "total_uncovered": len(uncovered_methods)}


def test_generator(source_dir: str = "src/main/java", output_dir: str = "src/test/java") -> dict:
    generated = []
    for java_file in Path(source_dir).rglob("*.java"):
        text = java_file.read_text()
        class_match = re.search(r"class\s+(\w+)", text)
        if not class_match:
            continue
        class_name = class_match.group(1)
        methods = re.findall(r"public\s+(\w[\w<>\[\]]*)\s+(\w+)\s*\(([^)]*)\)", text)
        test_class_path = Path(output_dir) / f"{class_name}Test.java"
        test_code = "import org.junit.Test;\nimport static org.junit.Assert.*;\n\n"
        test_code += f"public class {class_name}Test {{\n\n"
        for return_type, method_name, params in methods:
            param_list = params.split(",") if params.strip() else []
            args = ", ".join(["TODO"] * len(param_list))
            test_code += f"""
    @Test
    public void test_{method_name}() {{
        {class_name} obj = new {class_name}();
        // TODO: Replace default values
        // assertEquals(expected, obj.{method_name}({args}));
    }}\n"""
        test_code += "}\n"
        test_class_path.parent.mkdir(parents=True, exist_ok=True)
        test_class_path.write_text(test_code)
        generated.append(str(test_class_path))
    return {"generated_tests": generated}
