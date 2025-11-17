# MCP Project — tests & helper utilities
![CI](https://github.com/DJKapala/AI-assisted-development/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey)

SE333 Final Project — Autonomous Test-Improvement Agent
AI-Assisted Software Engineering with Model Context Protocol (MCP)

This project implements an intelligent autonomous agent that automatically:

Generates JUnit test cases

Runs Maven test suites

Analyzes JaCoCo coverage reports

Identifies uncovered code

Improves test coverage over multiple iterations

Detects bugs via failing tests

Automatically fixes bugs in Java source code

Commits improvements to GitHub using MCP Git tools

The agent uses the Model Context Protocol (MCP) and VS Code's built-in AI integration to orchestrate a full feedback-driven development loop.

Project Structure
mcp-project/
│
├── server.py                     # MCP server with Git, Maven, JaCoCo, test generation tools
├── src/
│   ├── main/java/                # Java source code (your codebase)
│   └── test/java/                # Auto-generated JUnit tests
│
├── target/                       # Maven build output (ignored by Git)
│
├── .github/
│   └── prompts/
│        └── tester.prompt.md     # Autonomous agent behavior specification
│
├── README.md
└── requirements.txt (optional)

1. Environment Setup
Install Python 3.10+ and Java 17+

Ensure you have:

Python: python --version

Java: java -version

Maven: mvn -version

Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

Install FastMCP
pip install fastmcp


Verify installation:

pip show fastmcp

2. Starting the MCP Server

Run:

python server.py


You should see:

MCP server running (transport=sse)


Leave this window open while using VS Code.

3. Connect the MCP Server in VS Code

Open VS Code

Press: CTRL+SHIFT+P

Search: MCP: Add Server

Enter your server URL (usually):

http://localhost:8000


Name it:
SE333 Test Agent Server

Confirm that the new server appears in VS Code's Chat sidebar.

4. Agent Prompt Setup

Create:

.github/prompts/tester.prompt.md


This file defines:

How the agent generates tests

How it analyzes coverage

How it fixes bugs

When it commits changes

When it pushes to GitHub

Example contents:

---
mode: "agent"
tools: ["git_status", "git_add_all", "git_commit", "git_push",
        "test_generation", "test_execution", "coverage_analyzer"]
description: "Autonomous testing & bug-fixing agent"
model: "gpt-5-mini"
---

# Autonomous Test Improvement Agent

You generate, run, and improve tests automatically…


(Replace with your full version.)

5. Running Tests Manually (Optional)

To manually run the Java test suite:

mvn -q test


This generates:

JUnit test results → target/surefire-reports/

JaCoCo coverage reports → target/site/jacoco/jacoco.xml

6. The Automated Test-Improvement Cycle

The agent performs:

Iteration Loop

test_execution() → run Maven tests

coverage_analyzer() → parse JaCoCo

Identify uncovered classes/methods

test_generator() → generate new tests

Re-run tests

If failures → detect bug → patch Java source

git_add_all()

git_commit()

git_push()

Stop when coverage plateaus or 100% reached

Commit Format Example:
[test-agent] Added new tests for MathUtils.divide
Coverage: 72.4%
Tests Added: 4
Uncovered remaining: 6
Bug Fixes: 1

7. Bug Detection & Fixing

The provided SE333 codebase contains at least one hidden bug.

Your agent should:

Run tests

Observe a failure (from Jacoco or Surefire output)

Inspect the Java source under src/main/java/

Propose + apply a patch

Re-run tests

Commit and push the fix

Example failure:

ArithmeticException: / by zero
at com.project.utils.MathUtil.divide(MathUtil.java:17)


Example fix:

if (b == 0) {
    throw new IllegalArgumentException("Divider cannot be zero.");
}


The agent should generate such patches autonomously.

8. Reporting & Quality Metrics

The agent tracks:

Test coverage percentage

Number of tests generated

Assertions per test

Detected bugs

Fixed bugs

Lines changed

Uncovered methods remaining

These metrics are automatically inserted into commit messages.

9. GitHub Integration
Required:

Enable GitHub CLI (gh) authentication:

gh auth login


Your MCP server supports:

git_status()

git_add_all()

git_commit(message, coverage)

git_push()

git_pull_request()

Auto-protection

Pushing to main or master is blocked

Agent must use feature branches

10. Running the Autonomous Agent

Open VS Code Chat → select:

“tester” agent

Then type:

Begin test improvement cycle.


The agent will:

Run tests

Generate tests

Improve coverage

Fix bugs

Commit changes

Push to GitHub

Repeat until coverage is maximized
