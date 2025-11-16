# server.py
try:
    from fastmcp import FastMCP
except Exception:
    FastMCP = None

from mcp_utils import run_cmd, add_numbers, coverage_analyzer, test_generator
import os
import subprocess
import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Initialize MCP if available; otherwise provide a no-op decorator so the
# module can be imported in test environments that don't have fastmcp's
# compiled dependencies (for example, pydantic_core wheels for new Python
# versions).
if FastMCP is not None:
    mcp = FastMCP("SE333 Test Agent Server")
    def mcp_tool(*args, **kwargs):
        return mcp.tool(*args, **kwargs)
else:
    mcp = None
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# Note: pure-Python helpers are implemented in `mcp_utils.py` and imported
# above so this module remains importable in environments without fastmcp.

# -------------------------------------------------------
# 1. git_status()
# -------------------------------------------------------
@mcp_tool()
def git_status() -> dict:
    out, err, code = run_cmd(["git", "status", "--porcelain"])
    lines = out.split("\n")
    staged, unstaged, conflicts = [], [], []

    for line in lines:
        if not line.strip():
            continue
        status = line[0:2]
        file = line[3:].strip()
        if "U" in status:
            conflicts.append(file)
        elif status[0] != " ":
            staged.append(file)
        else:
            unstaged.append(file)

    clean = (not staged and not unstaged and not conflicts)

    return {
        "clean": clean,
        "staged": staged,
        "unstaged": unstaged,
        "conflicts": conflicts
    }

# -------------------------------------------------------
# 2. git_add_all()
# -------------------------------------------------------
@mcp_tool()
def git_add_all() -> dict:
    exclusions = ["target/", "*.class", "*.log", "*.iml", ".idea", ".vscode"]
    run_cmd(["git", "add", "--all"])
    out, err, code = run_cmd(["git", "diff", "--cached", "--name-only"])
    staged_files = out.split("\n") if out else []

    return {"staged_files": staged_files, "errors": err}

# -------------------------------------------------------
# 3. git_commit(message)
# -------------------------------------------------------
@mcp_tool()
def git_commit(message: str, coverage: float = None, tests_added: int = None) -> dict:
    commit_msg = f"[test-agent] {message}"
    if coverage is not None:
        commit_msg += f"\nCoverage: {coverage}%"
    if tests_added is not None:
        commit_msg += f"\nTests Added: {tests_added}"

    out, err, code = run_cmd(["git", "commit", "-m", commit_msg])
    return {"commit_message": commit_msg, "stdout": out, "stderr": err, "code": code}

# -------------------------------------------------------
# 4. git_push(remote="origin")
# -------------------------------------------------------
@mcp_tool()
def git_push(remote: str = "origin", branch: str = None) -> dict:
    if branch is None:
        out, err, code = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        branch = out.strip()

    if branch in ["main", "master"]:
        return {"error": "Direct push to protected branch is not allowed.", "branch": branch}

    out, err, code = run_cmd(["git", "push", "-u", remote, branch])
    return {"remote": remote, "branch": branch, "stdout": out, "stderr": err, "code": code}

# -------------------------------------------------------
# 5. git_pull_request()
# -------------------------------------------------------
@mcp_tool()
def git_pull_request(base: str = "main", title: str = "", body: str = "") -> dict:
    result = subprocess.run(
        ["gh", "pr", "create", "--base", base, "--title", title, "--body", body],
        capture_output=True,
        text=True
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return {"pull_request_url": stdout, "stderr": stderr, "success": result.returncode == 0}

# -------------------------------------------------------
# 6. test_execution MCP TOOL
# -------------------------------------------------------
@mcp_tool()
def test_execution() -> dict:
    out, err, code = run_cmd(["mvn", "-q", "clean", "test"])
    surefire = "target/surefire-reports"
    jacoco_xml = "target/site/jacoco/jacoco.xml"
    jacoco_html = "target/site/jacoco/index.html"
    return {"maven_output": out, "errors": err, "exit_code": code,
            "surefire_reports": surefire, "jacoco_xml": jacoco_xml, "jacoco_html": jacoco_html}

# -------------------------------------------------------
# 7. coverage_analyzer MCP TOOL
# -------------------------------------------------------
@mcp_tool()
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

# -------------------------------------------------------
# 8. test_generator MCP TOOL
# -------------------------------------------------------
@mcp_tool()
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

# -------------------------------------------------------
# Start the MCP Server
# -------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="sse")
