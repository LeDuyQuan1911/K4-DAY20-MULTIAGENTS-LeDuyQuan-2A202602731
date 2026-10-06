"""Bonus Challenge 6d: Subagents with Skills.

Demonstrates and evaluates equipping subagents (explorer, implementer, reviewer)
with access to the skills directory ("skills": ["/skills/"]), comparing
behavior, house rule adherence, and token overhead against standard subagents.
"""

from pathlib import Path
import json
import shutil
import time

from lab.agent import BASE_PROMPT, PATHS_NOTE, SKILLS_NOTE, SUBAGENTS_NOTE, make_backend
from lab.grading import grade
from lab.model import make_model
from lab.runner import UsageMetadataCallbackHandler, render_trace
from lab.subagents import get_subagents
from lab.tasks import ROOT, get_task, hash_dir, prepare_sandbox
from deepagents import create_deep_agent


def build_subagent_with_skills_agent(sandbox: Path, model=None):
    """Build a multi-agent system where subagents also inherit skill access."""
    subagents_config = []
    for sub in get_subagents():
        subagents_config.append({
            **sub,
            "system_prompt": f"{sub['system_prompt']} {PATHS_NOTE} {SKILLS_NOTE}",
            "skills": ["/skills/"],
        })

    prompt = BASE_PROMPT + SUBAGENTS_NOTE + SKILLS_NOTE
    return create_deep_agent(
        model=model or make_model(),
        system_prompt=prompt,
        backend=make_backend(sandbox),
        subagents=subagents_config,
        skills=["/skills/"],
    )


def run_bonus_experiment(task_id: str = "code-eval", results_dir: str = "results/bonus-subagents-skills"):
    out_dir = ROOT / results_dir / task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    task = get_task(task_id)
    sandbox = ROOT / "scratch" / f"sandbox_bonus_{task_id}"

    shutil.rmtree(sandbox, ignore_errors=True)
    prepare_sandbox(task, sandbox, skills_dir=ROOT / "skills" / "auto")

    agent = build_subagent_with_skills_agent(sandbox)
    instruction = (task.dir / "instruction.md").read_text(encoding="utf-8")
    cb = UsageMetadataCallbackHandler()

    t0 = time.time()
    try:
        res = agent.invoke(
            {"messages": [{"role": "user", "content": instruction}]},
            config={"callbacks": [cb], "recursion_limit": 50},
        )
        final_msg = res["messages"][-1].content if res.get("messages") else ""
        err = None
    except Exception as exc:
        final_msg = ""
        err = f"{type(exc).__name__}: {exc}"
    dt = time.time() - t0

    g = grade(task, sandbox / "workspace")
    record = {
        "task": task_id,
        "condition": "subagents-skills",
        "seconds": round(dt, 2),
        "tokens": {"input": cb.input_tokens, "output": cb.output_tokens, "total": cb.total_tokens},
        "score": g.get("score", 0.0),
        "passed": g.get("passed", 0),
        "total": g.get("total", 0),
        "checks": g.get("checks", []),
        "error": err,
        "final_message": final_msg,
    }

    (out_dir / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    if "messages" in res:
        (out_dir / "trace.md").write_text(render_trace(res["messages"]), encoding="utf-8")

    shutil.rmtree(sandbox, ignore_errors=True)
    print(f"Bonus 6d complete: {task_id} score={record['passed']}/{record['total']} tokens={record['tokens']['total']}")
    return record


if __name__ == "__main__":
    print("Bonus 6d Subagents with Skills script ready.")
