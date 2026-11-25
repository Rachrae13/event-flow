"""
EVENTFLOW - Performance Analysis Lab View
Benchmarks Linear Search vs AVL Interval Tree Search across repetition counts,
visualizing real execution times, node prunes, and algorithmic trade-offs.
"""

import streamlit as st
import time
import pandas as pd
import plotly.express as px
from components.theme import get_plotly_dark_theme
from components.data_loader import linear_search, avl_search

def render_performance_view(events_df, avl_root):
    """Renders empirical benchmarking lab comparing Linear vs AVL interval search."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> ALGORITHM PERFORMANCE</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Advanced Performance Analysis Lab</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Empirical runtime benchmarking comparing brute-force O(n) Linear Search against Augmented AVL Interval Tree Search.
        </p>
    </div>
    """, unsafe_allow_html=True)

    reps = st.selectbox("Benchmark Repetitions", [100, 500, 1000, 5000], index=1)

    if st.button("📈 Run High-Precision Benchmark", key="btn_run_benchmark"):
        query_start = 10 * 60
        query_end = 11 * 60

        # Linear Search Benchmark
        t0 = time.perf_counter()
        for _ in range(reps):
            linear_res = linear_search(events_df, query_start, query_end)
        linear_duration = time.perf_counter() - t0

        # AVL Search Benchmark
        t1 = time.perf_counter()
        for _ in range(reps):
            avl_res = avl_search(avl_root, query_start, query_end)
        avl_duration = time.perf_counter() - t1

        comp_df = pd.DataFrame({
            "Algorithm": ["Linear Search O(n)", "AVL Interval Tree"],
            "Execution Time (seconds)": [linear_duration, avl_duration],
            "Matching Events Count": [len(linear_res), len(avl_res)]
        })

        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        fig = px.bar(
            comp_df,
            x="Algorithm",
            y="Execution Time (seconds)",
            color="Algorithm",
            color_discrete_sequence=["#38BDF8", "#00F2FE"]
        )
        dark_theme = get_plotly_dark_theme()
        fig.update_layout(**dark_theme, height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        if len(linear_res) == len(avl_res):
            st.success("✅ Algorithmic correctness verified: both algorithms yielded identical overlapping event counts.")
        else:
            st.error("Mismatch in matching events count! Please inspect AVL tree balancing.")

        # Complexity Explanation Card
        st.markdown("""
        <div class="glass-card" style="margin-top:16px; padding:18px 22px;">
            <div style="font-weight:750; color:#F8FAFC; margin-bottom:8px; font-size:1.02rem;">
                📚 Algorithmic Complexity Breakdown
            </div>
            <div style="font-size:0.86rem; color:#CBD5E1; line-height:1.6;">
                • <b>Linear Search:</b> Strictly scans every event in the dataset. Time complexity is <code>O(n)</code> regardless of query interval overlap.<br>
                • <b>Augmented AVL Interval Tree:</b> Organizes intervals by start time while tracking the maximum end time in every subtree. Pruning condition: if a subtree's maximum end is less than the query start time, that entire branch is skipped in <code>O(1)</code> time. When few intervals overlap, search approaches <code>O(k log n)</code> where <i>k</i> is the output size.
            </div>
        </div>
        """, unsafe_allow_html=True)
