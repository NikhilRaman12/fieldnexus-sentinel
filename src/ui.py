import os
import sys
import json
import pandas as pd
import numpy as np
import streamlit as st

# Configure sys.path so modules import properly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agents.data_cleaning_agent import DataCleaningAgent
from agents.eda_agent import EDAAgent
from agents.model_agent import ModelAgent
from agents.evaluation_agent import EvaluationAgent
from agents.insight_agent import InsightAgent
from agents.inference_agent import InferenceAgent
from agents.pipeline_agent import PipelineAgent
from utilis import get_logger

# Page configuration
st.set_page_config(
    page_title="FieldNexus-Sentinel | Agentic ML Control Center",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics and modern dark theme UI
st.markdown(
    """
    <style>
    /* Dark Theme & Custom Color Palette */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .main-header {
        font-size: 2.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #10b981;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_pipeline():
    """Initialize agentic pipeline instances."""
    cleaning_agent = DataCleaningAgent()
    eda_agent = EDAAgent()
    model_agent = ModelAgent(model_type="rf")
    evaluation_agent = EvaluationAgent()
    insight_agent = InsightAgent()
    inference_agent = InferenceAgent()

    pipeline = PipelineAgent(
        cleaning_agent=cleaning_agent,
        eda_agent=eda_agent,
        model_agent=model_agent,
        evaluation_agent=evaluation_agent,
        insight_agent=insight_agent,
        inference_agent=inference_agent,
    )
    return pipeline, model_agent, evaluation_agent, inference_agent


pipeline_obj, model_agent_obj, eval_agent_obj, infer_agent_obj = get_pipeline()

# Sidebar Navigation
st.sidebar.markdown("### 🌾 FieldNexus Sentinel")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    [
        "🚀 Pipeline Control Center",
        "🔮 Live Crop Recommendation Simulator",
        "📊 EDA & Dataset Explorer",
        "🎯 Model Performance Hub",
        "📑 Insights & Audit Report",
    ],
)

raw_dir = os.path.join("data", "raw")
proc_dir = os.path.join("data", "processed")
eda_dir = os.path.join("eda", "reports")
report_dir = os.path.join("outputs", "reports")

# Header Section
st.markdown("<div class='main-header'>FieldNexus Sentinel AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Autonomous Multi-Agent Agriculture Intelligence & Predictive Analytics System</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 1: Pipeline Control Center
# ---------------------------------------------------------
if page == "🚀 Pipeline Control Center":
    st.subheader("🚀 Agentic Pipeline Control Center")

    col1, col2, col3, col4 = st.columns(4)

    raw_files = [f for f in os.listdir(raw_dir) if f.endswith(".csv")] if os.path.exists(raw_dir) else []
    proc_files = [f for f in os.listdir(proc_dir) if f.endswith(".csv")] if os.path.exists(proc_dir) else []

    insights_path = os.path.join(report_dir, "insights.json")
    insights_data = {}
    if os.path.exists(insights_path):
        try:
            with open(insights_path, "r", encoding="utf-8") as f:
                insights_data = json.load(f)
        except Exception:
            pass

    evaluations_count = len(insights_data.get("evaluations", {})) if "evaluations" in insights_data else len(insights_data)

    with col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Raw Datasets</div>
                <div class='metric-value'>{len(raw_files)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Cleaned Datasets</div>
                <div class='metric-value'>{len(proc_files)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-label'>Trained ML Models</div>
                <div class='metric-value'>{evaluations_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div class='metric-card'>
                <div class='metric-label'>System Status</div>
                <div class='metric-value' style='color:#34d399;'>OPERATIONAL</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("The agentic pipeline orchestrates DataCleaningAgent ➔ EDAAgent ➔ ModelAgent ➔ EvaluationAgent ➔ InsightAgent ➔ InferenceAgent.")

    if st.button("▶ Run Full Agentic Pipeline Now", use_container_width=True, type="primary"):
        with st.spinner("Executing end-to-end multi-agent workflow..."):
            results = pipeline_obj.run_full_pipeline(
                raw_dir=raw_dir,
                proc_dir=proc_dir,
                eda_dir=eda_dir,
                report_dir=report_dir,
            )
            st.success(f"Pipeline executed successfully! Trained {results['trained_models_count']} models.")
            st.rerun()

    st.markdown("### 📁 Dataset Inventory")
    if raw_files:
        inventory_df = pd.DataFrame({
            "Dataset Name": raw_files,
            "Raw Path": [os.path.join(raw_dir, f) for f in raw_files],
            "Cleaned Status": ["Cleaned" if f in proc_files else "Pending" for f in raw_files],
        })
        st.dataframe(inventory_df, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2: Live Crop Recommendation Simulator
# ---------------------------------------------------------
elif page == "🔮 Live Crop Recommendation Simulator":
    st.subheader("🔮 Realistic Kaggle Crop Recommendation & Live Inference")
    st.write("Predict optimal crop recommendation using real-time soil N-P-K levels and environmental conditions.")

    kaggle_path = os.path.join(proc_dir, "kaggle_crop_recommendation.csv")
    if not os.path.exists(kaggle_path):
        kaggle_path = os.path.join(raw_dir, "kaggle_crop_recommendation.csv")

    if not os.path.exists(kaggle_path):
        st.error("Kaggle Crop Recommendation dataset not found. Please run the pipeline first.")
    else:
        df_kaggle = pd.read_csv(kaggle_path)

        st.markdown("#### 🧪 Input Soil & Climate Parameters")
        c1, c2, c3 = st.columns(3)

        with c1:
            val_n = st.slider("Nitrogen (N) - kg/ha", min_value=0, max_value=140, value=90)
            val_p = st.slider("Phosphorus (P) - kg/ha", min_value=5, max_value=145, value=42)
            val_k = st.slider("Potassium (K) - kg/ha", min_value=5, max_value=205, value=43)

        with c2:
            val_temp = st.slider("Temperature (°C)", min_value=8.0, max_value=45.0, value=20.8, step=0.1)
            val_hum = st.slider("Relative Humidity (%)", min_value=14.0, max_value=100.0, value=82.0, step=0.1)

        with c3:
            val_ph = st.slider("Soil pH Value", min_value=3.5, max_value=9.9, value=6.5, step=0.1)
            val_rain = st.slider("Rainfall (mm)", min_value=20.0, max_value=300.0, value=202.9, step=0.1)

        input_sample = {
            "N": val_n,
            "P": val_p,
            "K": val_k,
            "temperature": val_temp,
            "humidity": val_hum,
            "ph": val_ph,
            "rainfall": val_rain,
        }

        if st.button("🌱 Predict Optimal Crop Recommendation", type="primary", use_container_width=True):
            with st.spinner("ModelAgent & InferenceAgent executing neural/random forest prediction..."):
                # Train/fetch model for Kaggle dataset
                res = model_agent_obj.execute(df_kaggle, dataset_name="kaggle_crop_recommendation.csv")
                prediction_res = infer_agent_obj.run(res, input_sample)

                predicted_crop = prediction_res.get("prediction", "Unknown")

                st.markdown("<br>", unsafe_allow_html=True)
                st.success(f"### 🎉 Recommended Crop: **{str(predicted_crop).upper()}**")

                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.json({
                        "Predicted Crop": predicted_crop,
                        "Model Task": res["task_type"],
                        "Target Variable": res["target_name"],
                        "Feature Count": len(res["feature_names"]),
                    })
                with col_res2:
                    st.info(f"The ModelAgent trained a zero-leakage classifier on {len(res['X_train'])} samples using legitimate target '{res['target_name']}'.")

# ---------------------------------------------------------
# PAGE 3: EDA & Dataset Explorer
# ---------------------------------------------------------
elif page == "📊 EDA & Dataset Explorer":
    st.subheader("📊 Exploratory Data Analysis & Feature Distribution Explorer")

    available_proc = [f for f in os.listdir(proc_dir) if f.endswith(".csv")] if os.path.exists(proc_dir) else []
    if not available_proc:
        st.warning("No processed datasets found. Please run the pipeline from the Control Center.")
    else:
        selected_ds = st.selectbox("Select Dataset to Explore", available_proc)
        df_selected = pd.read_csv(os.path.join(proc_dir, selected_ds))

        tab1, tab2, tab3 = st.tabs(["Preview & Structure", "Statistical Summary", "Correlations & Outliers"])

        with tab1:
            st.write(f"**Shape:** {df_selected.shape[0]} rows × {df_selected.shape[1]} columns")
            st.dataframe(df_selected.head(10), use_container_width=True)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("##### Column Data Types")
                st.dataframe(pd.DataFrame(df_selected.dtypes.astype(str), columns=["Data Type"]), use_container_width=True)
            with col_t2:
                st.markdown("##### Missing Values Count")
                st.dataframe(pd.DataFrame(df_selected.isnull().sum(), columns=["Missing Count"]), use_container_width=True)

        with tab2:
            st.markdown("##### Numerical Descriptive Statistics")
            st.dataframe(df_selected.describe(), use_container_width=True)

        with tab3:
            st.markdown("##### Outlier Analysis (IQR Method)")
            num_df = df_selected.select_dtypes(include=["number"])
            if not num_df.empty:
                outlier_summary = {}
                for col in num_df.columns:
                    q1, q3 = num_df[col].quantile([0.25, 0.75])
                    iqr = q3 - q1
                    cnt = int(((num_df[col] < (q1 - 1.5 * iqr)) | (num_df[col] > (q3 + 1.5 * iqr))).sum())
                    outlier_summary[col] = cnt
                st.dataframe(pd.DataFrame(list(outlier_summary.items()), columns=["Column", "Outlier Count"]), use_container_width=True)

                st.markdown("##### Correlation Matrix Heatmap")
                corr_df = num_df.corr().round(2)
                st.dataframe(corr_df, use_container_width=True)
            else:
                st.info("No numeric columns available for outlier and correlation analysis.")

# ---------------------------------------------------------
# PAGE 4: Model Performance Hub
# ---------------------------------------------------------
elif page == "🎯 Model Performance Hub":
    st.subheader("🎯 Model Performance Hub & Verification Matrix")

    insights_path = os.path.join(report_dir, "insights.json")
    if not os.path.exists(insights_path):
        st.warning("No insights report found. Run the pipeline to generate model metrics.")
    else:
        with open(insights_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        evals = data.get("evaluations", data)

        rows = []
        for name, item in evals.items():
            if isinstance(item, dict) and item.get("status") == "evaluated":
                task_type = item.get("task_type", "unknown")
                target_name = item.get("target_name", "-")
                metrics = item.get("metrics", {})

                row = {
                    "Dataset": name,
                    "Task Type": task_type,
                    "Target Variable": target_name,
                    "Metric 1": f"R2: {metrics.get('r2_score')}" if task_type == "regression" else f"Accuracy: {metrics.get('accuracy')}",
                    "Metric 2": f"RMSE: {metrics.get('rmse')}" if task_type == "regression" else f"F1: {metrics.get('f1_score')}",
                    "Metric 3": f"MAE: {metrics.get('mae')}" if task_type == "regression" else f"Precision: {metrics.get('precision')}",
                }
                rows.append(row)

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else:
            st.info("No evaluated model metrics available yet.")

# ---------------------------------------------------------
# PAGE 5: Insights & Audit Report
# ---------------------------------------------------------
elif page == "📑 Insights & Audit Report":
    st.subheader("📑 Agentic Insights & Audit Report")

    insights_path = os.path.join(report_dir, "insights.json")
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as f:
            st.json(json.load(f))
    else:
        st.info("Insights report not generated yet. Run the pipeline first.")
