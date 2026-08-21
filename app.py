import streamlit as st
import json
import glob
import pandas as pd                              # NEW: table/data library, for the chart

st.title("Model Evaluation Dashboard")

run_files = sorted(glob.glob("results/run_*.json"))

if not run_files:
    st.warning("No runs found. Run phase6.py first.")
else:
    # ---------- Pick a run ----------
    chosen_file = st.selectbox("Pick a run", run_files)
    with open(chosen_file) as f:
        run = json.load(f)
    st.write(f"**Question set:** {run['question_file']}")

    # ---------- Model comparison table ----------
    rows = []
    for r in run["results"]:
        percent = (r["correct"] / r["total"]) * 100
        rows.append({
            "Model": r["model"],
            "Score": r["score"],
            "Percent": round(percent, 1),
            "Cost ($)": round(r["cost"], 6),
        })
    st.subheader("Model comparison")
    st.dataframe(rows)

    # ---------- Score chart ----------
    st.subheader("Score chart")
    chart_df = pd.DataFrame({                    # a small table: one column of models, one of percents
        "Model": [r["model"] for r in run["results"]],
        "Percent": [round(r["correct"] / r["total"] * 100, 1) for r in run["results"]],
    })
    st.bar_chart(chart_df, x="Model", y="Percent")   # draw bars: models on x, percent on y

    # ---------- Download this run ----------
    st.download_button(
        "Download this run (JSON)",
        data=json.dumps(run, indent=2),          # the run turned back into JSON text
        file_name=chosen_file.split("/")[-1],    # just the filename, without "results/"
        mime="application/json",
    )

    # ---------- Question explorer ----------
    st.subheader("Question explorer")
    model_names = [r["model"] for r in run["results"]]
    chosen_model_name = st.selectbox("Pick a model", model_names)
    model = None
    for r in run["results"]:
        if r["model"] == chosen_model_name:
            model = r
    filter_choice = st.radio("Show", ["All", "Correct only", "Incorrect only"], horizontal=True)
    q_rows = []
    for i, a in enumerate(model["answers"], start=1):
        if filter_choice == "Correct only" and not a["is_correct"]:
            continue
        if filter_choice == "Incorrect only" and a["is_correct"]:
            continue
        q_rows.append({
            "Q#": i,
            "Question": a["question"],
            "Model answer": a["model_answer"],
            "Correct": a["correct"],
            "Result": "correct" if a["is_correct"] else "WRONG",
        })
    st.write(f"Showing {len(q_rows)} of {len(model['answers'])} questions")
    st.dataframe(q_rows)

    # ---------- Compare two runs ----------
    st.subheader("Compare two runs")
    other_file = st.selectbox("Pick a second run", run_files, key="compare")  # 'key' avoids a clash with the first dropdown
    with open(other_file) as f:
        other_run = json.load(f)
    other_rows = []
    for r in other_run["results"]:
        percent = (r["correct"] / r["total"]) * 100
        other_rows.append({"Model": r["model"], "Score": r["score"], "Percent": round(percent, 1)})
    col1, col2 = st.columns(2)                    # split the page into two side-by-side columns
    col1.write(chosen_file.split("/")[-1])
    col1.dataframe(rows)                          # first run on the left
    col2.write(other_file.split("/")[-1])
    col2.dataframe(other_rows)                    # second run on the right