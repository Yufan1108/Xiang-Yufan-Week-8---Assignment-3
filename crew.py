import json
import os
from datetime import datetime

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from langchain_core.tools import Tool

load_dotenv()

# ---------- Assignment meta ----------
BUSINESS_PROBLEM = "Increase 90-day repurchase rate for a B2C e-commerce business without significantly increasing acquisition cost"
TASK1_DESC = (
    f"Business context: {BUSINESS_PROBLEM}. Output a Research Dossier that must include: "
    "Problem Statement; Metric Chain (Activation->Repeat); "
    "Customer Segments (>=3); Benchmark Signals; Validation Questions (>=5)."
)
TASK2_DESC = (
    "You will receive Task1 output as context. Output Analysis & Hypotheses that must include: "
    "Root Cause Hypotheses; Top 3 Prioritized Opportunities (each with target KPI/validation/risk); "
    "KPI Targets (>=3); ROI Rationale (formula + assumptions); Risks & Mitigations."
)
TASK3_DESC = (
    "You will receive Task2 output as context. Output a Business Analysis Report with required headers: "
    "# Executive Summary # Key Insights # Recommendations & Implementation Steps "
    "# Roadmap (0-30/31-90/91-180 days) # KPI Measurement Plan # Risks & Next Actions"
)


def get_retention_benchmarks() -> str:
    data = {
        "repurchase_rate_90d": 0.18,
        "churn_rate_30d": 0.12,
        "activation_rate": 0.62,
        "recommendation_uplift": 0.08,
        "avg_order_value": 88.0,
        "gross_margin_rate": 0.32,
    }
    return json.dumps(data, ensure_ascii=False)


def calculate_roi(incremental_orders: float, gross_margin_rate: float) -> str:
    revenue = incremental_orders * 88.0
    gross_profit = revenue * gross_margin_rate
    cost = gross_profit * 0.35
    roi = (gross_profit - cost) / cost
    return json.dumps(
        {"incremental_revenue": revenue, "incremental_gross_profit": gross_profit, "annual_cost_assumption": cost, "roi": roi},
        ensure_ascii=False,
    )


def build_agents_and_tasks():
    tools = [
        Tool(name="get_retention_benchmarks", description="Return offline benchmarks for repurchase/churn metrics (JSON).", func=lambda _=None: get_retention_benchmarks()),
        Tool(
            name="calculate_roi",
            description="Calculate ROI from incremental orders and gross margin rate (JSON).",
            func=lambda x=None: calculate_roi(
                float(x.get("incremental_orders", 4500)) if isinstance(x, dict) else 4500,
                float(x.get("gross_margin_rate", 0.32)) if isinstance(x, dict) else 0.32,
            ),
        ),
    ]
    researcher = Agent(
        role="Researcher",
        goal="Deliver a verifiable research dossier with at least 3 customer segments and 5 validation questions, including the repurchase metric chain.",
        backstory="You are a growth researcher specialized in retention postmortems who always defines metric logic before forming conclusions.",
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )
    analyst = Agent(
        role="Analyst",
        goal="Produce Top 3 opportunities and a reproducible ROI framework to improve 90-day repurchase rate from 18% to 22%.",
        backstory="You are a business analyst who requires every recommendation to include KPI targets, validation method, and risk mitigation.",
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )
    writer = Agent(
        role="Writer",
        goal="Produce an executive-ready report with summary, roadmap, KPI plan, and next actions.",
        backstory="You are a strategy writer skilled at translating complex analysis into practical action plans.",
        verbose=True,
        allow_delegation=False,
    )
    t1 = Task(agent=researcher, description=TASK1_DESC)
    t2 = Task(agent=analyst, description=TASK2_DESC)  # uses Task1 context in sequential process
    t3 = Task(agent=writer, description=TASK3_DESC)   # uses Task2 context in sequential process
    return [researcher, analyst, writer], [t1, t2, t3]


def write_prompt_log(t1: str, t2: str, t3: str, used_mock: bool) -> None:
    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "used_mock": used_mock,
        "task_descriptions": {"task1": TASK1_DESC, "task2": TASK2_DESC, "task3": TASK3_DESC},
        "outputs": {"task1": t1, "task2": t2, "task3": t3},
    }
    with open("crew-run-log.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))


def run_mock_sequential():
    print("[Mock Mode] OPENAI_API_KEY not found. Running offline sequential flow.")
    bmk = get_retention_benchmarks()
    t1 = f"Research Dossier\n- Problem Statement: 90-day repurchase rate is below target, putting pressure on LTV.\n- Metric Chain: Weak activation -> timing mismatch in engagement -> lower repurchase conversion.\n- Customer Segments: New users not activated / Activated but no repeat purchase / High-value dormant users.\n- Benchmark Signals: {bmk}\n- Validation Questions: activation drop-off, causal timing, segment differences, engagement effectiveness, recommendation effectiveness."
    print("[Researcher] Completed Task1 and called get_retention_benchmarks.")
    roi = calculate_roi(4500, 0.32)
    t2 = f"Analysis & Hypotheses\n- Root Cause Hypotheses: activation funnel weakness; engagement timing mismatch; weak high-value recall strategy.\n- Prioritized Opportunities Top3: activation-first engagement / recommendation window operations / high-value reactivation.\n- KPI Targets: 90-day repurchase rate 18%->22%; Activation +3~5pp; Recommendation conversion +8%.\n- ROI Rationale: {roi}\n- Risks & Mitigations: margin erosion, attribution bias, content homogenization -> frequency control + experiments + template iteration."
    print("[Analyst] Completed Task2 and called calculate_roi.")
    t3 = "Business Analysis Report\n# Executive Summary\nImprove repurchase through three priority initiatives while controlling margin risk.\n# Key Insights\nThe main breakpoints are activation path quality and engagement timing windows.\n# Recommendations & Implementation Steps\nExecute activation-first engagement, recommendation-window operations, and high-value reactivation by segment.\n# Roadmap(0-30/31-90/91-180 days)\nStart with instrumentation and experiments, then scale.\n# KPI Measurement Plan\nTrack funnel and repurchase weekly; update ROI monthly.\n# Risks & Next Actions\nValidate with small traffic before wider rollout."
    print("[Writer] Completed Task3 and produced final report.")
    print("\n=== FINAL RESULT ===\n" + t3)
    return t1, t2, t3


def run_real_crewai():
    agents, tasks = build_agents_and_tasks()
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
    return crew.kickoff()


def main():
    key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
    if not key:
        t1, t2, t3 = run_mock_sequential()
        write_prompt_log(t1, t2, t3, used_mock=True)
        print("[Done] Generated crew-run-log.json (task prompts + outputs).")
        return
    print("[Real Mode] OPENAI_API_KEY detected. Starting CrewAI sequential run.")
    try:
        final_report = run_real_crewai()
        write_prompt_log("(See output.txt)", "(See output.txt)", str(final_report), used_mock=False)
        print("\n=== FINAL RESULT ===\n" + str(final_report))
    except Exception as e:
        print(f"[Real Mode] Failed: {e}. Switching to Mock Mode.")
        t1, t2, t3 = run_mock_sequential()
        write_prompt_log(t1, t2, t3, used_mock=True)


if __name__ == "__main__":
    main()

