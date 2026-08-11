import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(page_title="Day 13 AI Observability", layout="wide")
st.title("Day 13 AI Observability Dashboard")
st.markdown("Dữ liệu được làm mới từ file `data/logs.jsonl`.")

# Đọc dữ liệu
def load_data(file_path):
    data = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Auto-refresh mỗi 30s
@st.fragment(run_every="30s")
def render_dashboard():
    df = load_data("data/logs.jsonl")
    
    if df.empty:
        st.warning("Không tìm thấy dữ liệu trong `data/logs.jsonl`")
        return

    # Lọc 60 phút gần nhất
    if "ts" in df.columns and not df.empty:
        max_ts = df["ts"].max()
        cutoff_time = max_ts - pd.Timedelta(minutes=60)
        df = df[df["ts"] >= cutoff_time]
    
    # Lọc sự kiện (Events)
    response_sent = df[df["event"] == "response_sent"].copy()
    request_received = df[df["event"] == "request_received"].copy()
    request_failed = df[df["event"] == "request_failed"].copy()
    
    # Layout
    st.markdown("### Metrics (Time Range: 60 minutes)")
    col1, col2, col3 = st.columns(3)

    # 1. Latency percentiles
    with col1:
        st.subheader("1. Latency Percentiles")
        if not response_sent.empty and "latency_ms" in response_sent.columns:
            p50 = response_sent["latency_ms"].quantile(0.5)
            p95 = response_sent["latency_ms"].quantile(0.95)
            p99 = response_sent["latency_ms"].quantile(0.99)
            st.metric("P95 Latency", f"{p95:.0f} ms", delta_color="inverse", help="Threshold <= 3000 ms")
            
            if p95 <= 3000:
                st.success("✅ Đạt SLO (<= 3000 ms)")
            else:
                st.error("❌ Vi phạm SLO (> 3000 ms)")
                
            fig_lat = px.box(response_sent, y="latency_ms", title="Latency Distribution (ms)")
            fig_lat.add_hline(y=3000, line_dash="dash", line_color="red", annotation_text="Threshold 3000ms")
            st.plotly_chart(fig_lat, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu độ trễ")

    # 2. Request traffic
    with col2:
        st.subheader("2. Request Traffic")
        if not request_received.empty and "ts" in request_received.columns:
            req_by_min = request_received.set_index("ts").resample("1min").size().reset_index(name="count")
            current_rate = req_by_min["count"].iloc[-1] if not req_by_min.empty else 0
            
            st.metric("Traffic (Rate per min)", f"{current_rate} req/min", help="Threshold >= 1 req/min")
            
            if current_rate >= 1:
                st.success("✅ Đạt SLO (>= 1 req/min)")
            else:
                st.error("❌ Vi phạm SLO (< 1 req/min)")
                
            fig_traffic = px.line(req_by_min, x="ts", y="count", title="Traffic (requests/minute)")
            fig_traffic.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Threshold 1 req/min")
            st.plotly_chart(fig_traffic, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu traffic")

    # 3. Error rate and breakdown
    with col3:
        st.subheader("3. Error Rate & Breakdown")
        total_req = len(request_received)
        total_err = len(request_failed)
        error_rate = (total_err / total_req * 100) if total_req > 0 else 0
        
        st.metric("Error Rate", f"{error_rate:.2f}%", delta_color="inverse", help="Threshold <= 2%")
        
        if error_rate <= 2:
            st.success("✅ Đạt SLO (<= 2%)")
        else:
            st.error("❌ Vi phạm SLO (> 2%)")
            
        if not request_failed.empty and "error_type" in request_failed.columns:
            err_counts = request_failed["error_type"].value_counts().reset_index()
            err_counts.columns = ["error_type", "count"]
            fig_err = px.pie(err_counts, names="error_type", values="count", title="Error Breakdown")
            st.plotly_chart(fig_err, use_container_width=True)
        else:
            st.info("Không có request lỗi nào được ghi nhận.")

    st.markdown("---")
    col4, col5, col6 = st.columns(3)

    # 4. Cost over time
    with col4:
        st.subheader("4. Cost Over Time")
        if not response_sent.empty and "cost_usd" in response_sent.columns:
            total_cost = response_sent["cost_usd"].sum()
            st.metric("Total Cost", f"${total_cost:.4f}", help="Threshold <= 2.5 USD")
            
            if total_cost <= 2.5:
                st.success("✅ Đạt SLO (<= $2.5)")
            else:
                st.error("❌ Vi phạm SLO (> $2.5)")
                
            if "ts" in response_sent.columns:
                cost_by_min = response_sent.set_index("ts").resample("1min")["cost_usd"].sum().reset_index()
                fig_cost = px.bar(cost_by_min, x="ts", y="cost_usd", title="Cost per Minute (USD)")
                st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu chi phí")

    # 5. Tokens
    with col5:
        st.subheader("5. Input & Output Tokens")
        if not response_sent.empty:
            tokens_in = response_sent["tokens_in"].sum() if "tokens_in" in response_sent.columns else 0
            tokens_out = response_sent["tokens_out"].sum() if "tokens_out" in response_sent.columns else 0
            total_tokens = tokens_in + tokens_out
            
            st.metric("Total Tokens", f"{total_tokens:,.0f}", help="Threshold <= 50000 tokens")
            
            if total_tokens <= 50000:
                st.success("✅ Đạt SLO (<= 50000 tokens)")
            else:
                st.error("❌ Vi phạm SLO (> 50000 tokens)")
                
            fig_tokens = px.bar(
                x=["Tokens In", "Tokens Out"], 
                y=[tokens_in, tokens_out],
                title="Token Usage Breakdown"
            )
            st.plotly_chart(fig_tokens, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu tokens")

    # 6. Quality proxy
    with col6:
        st.subheader("6. Quality Proxy")
        if not response_sent.empty and "quality_score" in response_sent.columns:
            mean_quality = response_sent["quality_score"].mean()
            st.metric("Mean Quality Score", f"{mean_quality:.2f}", help="Threshold >= 0.75")
            
            if mean_quality >= 0.75:
                st.success("✅ Đạt SLO (>= 0.75)")
            else:
                st.error("❌ Vi phạm SLO (< 0.75)")
                
            fig_qual = px.histogram(response_sent, x="quality_score", title="Quality Score Distribution")
            fig_qual.add_vline(x=0.75, line_dash="dash", line_color="red", annotation_text="Threshold 0.75")
            st.plotly_chart(fig_qual, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu chất lượng")

render_dashboard()
