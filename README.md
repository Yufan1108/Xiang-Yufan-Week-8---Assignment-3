# CrewAI Sequential Process Business Analysis Assignment

## Business Problem
This CrewAI project analyzes how a B2C e-commerce company can improve its **90-day repurchase rate** without significantly increasing acquisition cost, in order to improve LTV and profitability. The core outputs include root-cause hypotheses for low repurchase, top 3 actionable opportunities, matching KPI/validation methods, and a reproducible ROI framework with implementation roadmap.

## How the Three Agents Collaborate
The project uses three agents executed in sequence: **Researcher** decomposes the “activation -> repurchase” metric chain, proposes customer segmentation angles, and provides benchmark signals (via offline tools when needed) to produce a structured Research Dossier; **Analyst** receives Task 1 context, converts the dossier into root-cause hypotheses, top 3 opportunities, KPI/risk/validation plan, and ROI rationale using `calculate_roi`; **Writer** receives Task 2 context and transforms the analysis into an executive-facing Business Analysis Report including summary, insights, action steps, 0-30/31-90/91-180 day roadmap, and KPI Measurement Plan.

## Challenges and Solutions
1. **Dependency compatibility conflict**: A newer CrewAI version caused compatibility issues with Python 3.9/SQLAlchemy, so the project was pinned to `crewai==0.1.32` and `sqlalchemy>=2.0.0` to ensure stable import and execution.
2. **Missing LLM API key**: Since `OPENAI_API_KEY` is not configured in this environment, real model calls are unavailable. To keep the assignment fully reproducible end-to-end (`output.txt` and `prompt-log.md` generation), `crew.py` includes a **Mock Mode** that preserves the same 3-task sequential behavior and output structure.

## One Thing I Would Improve with More Time
With more time, I would replace Mock Mode with live data integration and stronger experiment design (e.g., SQL/event data pipeline and cohort attribution), and capture a more complete low-level conversation trace closer to raw LLM message logs.

