"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Use proactively to explore the workspace, inspect data files, read docstrings, README, or logs, and report initial findings without modifying any files.",
            "system_prompt": "You are an exploratory assistant. Your responsibility is to thoroughly inspect files, analyze requirements and data structures, and report exact facts to the main agent. Do not modify any files.",
        },
        {
            "name": "implementer",
            "description": "Use to perform code modifications, data transformations, log parsing, or run tests and scripts, and report the execution results.",
            "system_prompt": "You are an implementation assistant. Your responsibility is to write and edit files, run scripts and tests using the shell, verify changes, and report the results and any errors to the main agent.",
        },
        {
            "name": "reviewer",
            "description": "Use after making changes or generating outputs to independently verify compliance with all task requirements, edge cases, and output formatting without making modifications.",
            "system_prompt": "You are a quality assurance reviewer. Your responsibility is to inspect the final outputs, verify edge cases, format constraints, and ensure all specifications are satisfied. Report any discrepancy or confirmation to the main agent. Do not modify files.",
        },
    ]
