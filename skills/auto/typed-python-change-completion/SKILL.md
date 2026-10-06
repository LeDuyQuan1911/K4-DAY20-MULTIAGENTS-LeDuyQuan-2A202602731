---
name: typed-python-change-completion
description: Use when fixing or extending a Python package governed by typing, regression-test, and changelog rules.
---
- Inspect all affected public functions, including callers and package exports.
- Add annotations to every parameter and return value of each public function.
- Use accurate container, optional, union, and scalar types rather than vague placeholders.
- Preserve existing tests unless the task explicitly authorizes their modification.
- Add a dedicated regression test for each independently fixed defect.
- Give every regression test a focused name and one clear expected behavior.
- Exercise boundary cases implicated by the defect, not just the happy path.
- Record every fix under the required unreleased changelog heading.
- Use the mandated changelog syntax and reference the corrected function.
- Run the full test suite and a type-annotation compliance check before delivery.
