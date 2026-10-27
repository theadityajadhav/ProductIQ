import streamlit as st
import pandas as pd
import plotly.express as px
 
st.set_page_config(
    page_title="ProductIQ — AI Product Strategy Consultant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.markdown("""
<style>
/* Hide anchor link icons */
h1 a, h2 a, h3 a, .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
    display: none !important;
}
a[href*="#"] svg { display: none !important; }
 
/* Sidebar — consulting blue */
[data-testid="stSidebar"] {
    background-color: #1B4FD8 !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.25) !important;
}
 
/* Main background white */
.stApp { background-color: #FFFFFF !important; }
 
/* Playfair Display for main title only */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
h1 {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-weight: 700 !important;
}
 
/* Blue button — no red border on click */
.stButton > button {
    background-color: #1B4FD8 !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background-color: #1440B0 !important;
}
.stButton > button:focus {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
}
 
/* Table header blue (best-effort) */
[data-testid="stDataFrame"] th {
    background-color: #1B4FD8 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)
 
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 ProductIQ")
    st.caption("AI STRATEGY CONSULTANT")
    st.divider()
 
    st.markdown("**About**")
    st.write(
        "ProductIQ applies a BCG-inspired portfolio framework and Google Gemini AI "
        "to classify your products and deliver data-driven strategy recommendations."
    )
    st.divider()
 
    st.markdown("**How to Use**")
    st.write("1. Upload your sales Excel or CSV file")
    st.write("2. Click **Analyze Now**")
    st.write("3. Review BCG categories and charts")
    st.write("4. Read AI strategy recommendations")
    st.write("5. Download results as CSV")
    st.divider()
 
    st.markdown("**Built by Aditya Jadhav**")
    st.write("Data Analyst")
    st.write("Portfolio Project")
 
# ── Main header ───────────────────────────────────────────────────────────────
st.title("ProductIQ")
st.subheader("AI Product Strategy Consultant - BCG-Inspired Portfolio Analysis + Google Gemini AI")
st.divider()
 
# ── File Upload ───────────────────────────────────────────────────────────────
st.markdown("### Step 1 - Upload Your Data")
 
uploaded_file = st.file_uploader(
    "Drop your file here or click Upload",
    type=["xlsx", "csv"],
    help="Required columns: Product Name, Sales/Revenue, Profit. Date column optional."
)
 
if uploaded_file is not None:
    # Reset analysis if a new file is uploaded
    if "last_file" not in st.session_state or st.session_state["last_file"] != uploaded_file.name:
        st.session_state["analyzed"] = False
        st.session_state["last_file"] = uploaded_file.name
        st.session_state["kpis"] = None
        st.session_state["prod_col"] = None
 
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
 
    # File stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows Loaded",   f"{len(df):,}")
    c2.metric("Columns Found", f"{len(df.columns)}")
    c3.metric("File Size",     f"{uploaded_file.size / 1024:.1f} KB")
 
    # Preview
    with st.expander("👁 Preview - first 10 rows"):
        st.dataframe(df.head(10), use_container_width=True)
 
    st.success("File loaded successfully! Ready to analyze.")
 
    st.markdown("---")
    st.markdown("### Step 2 - Run Analysis")
 
    analyze = st.button("🚀 Analyze Now", type="primary")
 
    if analyze:
        # ── Column detection ──────────────────────────────────────────────────
        df.columns = [c.lower().strip() for c in df.columns]
        col_map = {}
        for c in df.columns:
            if any(x in c for x in ["product name", "product", "item name", "item"]) and "product" not in col_map:
                col_map["product"] = c
            if any(x in c for x in ["sales", "revenue", "amount"]) and "sales" not in col_map:
                col_map["sales"] = c
            if "profit" in c and "profit" not in col_map:
                col_map["profit"] = c
            if any(x in c for x in ["order date", "date"]) and "date" not in col_map:
                col_map["date"] = c
 
        # Also detect a separate product name column (e.g. Superstore has both product id and product name)
        name_col = None
        for c in df.columns:
            if "product name" in c and c != col_map.get("product"):
                name_col = c
                break
 
        missing = [k for k in ["product", "sales", "profit"] if k not in col_map]
        if missing:
            st.error(f"Missing columns: {missing}. Found: {list(df.columns)}")
            st.stop()
 
        prod_col   = col_map["product"]
        sales_col  = col_map["sales"]
        profit_col = col_map["profit"]
 
        # ── KPI calculation ───────────────────────────────────────────────────
        df[sales_col]  = pd.to_numeric(df[sales_col],  errors="coerce").fillna(0)
        df[profit_col] = pd.to_numeric(df[profit_col], errors="coerce").fillna(0)
 
        agg_dict = {
            "total_revenue": (sales_col, "sum"),
            "total_profit":  (profit_col, "sum"),
        }
        # If there's a separate product name column, carry it along
        if name_col and name_col != prod_col:
            agg_dict["product_name"] = (name_col, "first")
 
        kpis = df.groupby(prod_col).agg(**agg_dict).reset_index()
 
        kpis["total_revenue"]     = kpis["total_revenue"].round(2)
        kpis["total_profit"]      = kpis["total_profit"].round(2)
        kpis["profit_margin_pct"] = (
            (kpis["total_profit"] / kpis["total_revenue"].replace(0, 1)) * 100
        ).round(2)
 
        # ── Growth calculation (latest 2 years only) ──────────────────────────
        years = []
        y1, y2 = None, None
        growth_unavailable = False  # Flag: True when growth data cannot be calculated
 
        if "date" in col_map:
            df[col_map["date"]] = pd.to_datetime(df[col_map["date"]], errors="coerce")
            df["year"] = df[col_map["date"]].dt.year
            years = sorted(df["year"].dropna().unique())
            if len(years) >= 2:
                y1, y2 = int(years[-2]), int(years[-1])
                rev_y1 = df[df["year"] == y1].groupby(prod_col)[sales_col].sum()
                rev_y2 = df[df["year"] == y2].groupby(prod_col)[sales_col].sum()
 
                # Only calculate growth for products present in BOTH years
                # Products in only one year get NaN → marked as "Insufficient Data"
                both_years = rev_y1.index.intersection(rev_y2.index)
                growth = pd.Series(index=kpis[prod_col], dtype=float)
                for prod in kpis[prod_col]:
                    if prod in both_years:
                        r1 = rev_y1[prod]
                        r2 = rev_y2[prod]
                        growth[prod] = round(((r2 - r1) / r1 * 100), 2) if r1 != 0 else 0.0
                    else:
                        growth[prod] = None  # Not enough data
 
                kpis["growth_pct"] = kpis[prod_col].map(growth).values
            else:
                # Only one year of data found
                kpis["growth_pct"] = None
                growth_unavailable = True
        else:
            # No date column in dataset
            kpis["growth_pct"] = None
            growth_unavailable = True
 
        # ── KPI cards ─────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Key Performance Indicators")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue",  f"${kpis['total_revenue'].sum():,.0f}")
        k2.metric("Total Profit",   f"${kpis['total_profit'].sum():,.0f}")
        k3.metric("Avg Margin %",   f"{kpis['profit_margin_pct'].mean():.2f}%")
        k4.metric("Total Products", f"{len(kpis):,}")
 
        if y1 and y2:
            st.caption(f"📅 Growth calculated: {y1} vs {y2} (products present in both years only)")
 
        st.success("✅ KPIs calculated!")
 
        # ── BCG Classification ────────────────────────────────────────────────
        revenue_median = kpis["total_revenue"].median()
 
        # Only use products with valid growth for median calculation
        valid_growth = kpis["growth_pct"].dropna()
        growth_median = valid_growth.median() if len(valid_growth) > 0 else None
 
        def assign_bcg(row):
            high_rev = row["total_revenue"] >= revenue_median
            if growth_unavailable or pd.isna(row["growth_pct"]):
                # No growth data — classify by revenue only
                return "Star" if high_rev else "Cash Cow"
            # Use strict > so products exactly at median don't all skew one side
            high_growth = row["growth_pct"] > growth_median
            if high_rev and high_growth:
                return "Star"
            elif high_rev and not high_growth:
                return "Cash Cow"
            elif not high_rev and high_growth:
                return "Hidden Gem"
            else:
                return "Dead Weight"
 
        kpis["bcg_category"] = kpis.apply(assign_bcg, axis=1)
 
        # Flag loss-making products (negative profit margin)
        kpis["loss_making"] = kpis["profit_margin_pct"] < 0
 
        # ── BCG Summary Table ─────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### BCG-Inspired Portfolio Summary")
 
        # Show warning if growth data was unavailable for some/all products
        insufficient_count = kpis["growth_pct"].isna().sum()
        if growth_unavailable:
            st.warning("⚠️ Growth data unavailable — classifying by revenue only.")
        elif insufficient_count > 0:
            st.info(f"ℹ️ {insufficient_count} products appeared in only one year — classified by revenue only (insufficient growth data).")
 
        bcg_summary = kpis.groupby("bcg_category").agg(
            Products    =("bcg_category",     "count"),
            Avg_Revenue =("total_revenue",     "mean"),
            Avg_Margin  =("profit_margin_pct", "mean"),
            Avg_Growth  =("growth_pct",        "mean")
        ).reset_index()
        bcg_summary.columns = ["BCG Category", "Products", "Avg Revenue ($)", "Avg Margin (%)", "Avg Growth (%)"]
        for c in ["Avg Revenue ($)", "Avg Margin (%)", "Avg Growth (%)"]:
            bcg_summary[c] = bcg_summary[c].round(2)
 
        with st.container(border=True):
            st.dataframe(
                bcg_summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "BCG Category":    st.column_config.TextColumn("BCG Category"),
                    "Products":        st.column_config.NumberColumn("Products"),
                    "Avg Revenue ($)": st.column_config.NumberColumn("Avg Revenue ($)", format="$%.2f"),
                    "Avg Margin (%)":  st.column_config.NumberColumn("Avg Margin (%)",  format="%.2f%%"),
                    "Avg Growth (%)":  st.column_config.NumberColumn("Avg Growth (%)",  format="%.2f%%"),
                }
            )
 
        # ── Charts ────────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Visual Analysis")
 
        color_map = {
            "Star":        "#1B4FD8",
            "Cash Cow":    "#0EA5E9",
            "Hidden Gem":  "#10B981",
            "Dead Weight": "#EF4444"
        }
 
        chart_col1, chart_col2 = st.columns(2)
 
        with chart_col1:
            bar_data = kpis.groupby("bcg_category")["total_revenue"].sum().reset_index()
            bar_data.columns = ["BCG Category", "Total Revenue"]
            fig_bar = px.bar(
                bar_data,
                x="BCG Category", y="Total Revenue",
                color="BCG Category",
                color_discrete_map=color_map,
                title="Revenue by BCG Category",
                text_auto=".2s"
            )
            fig_bar.update_layout(
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                showlegend=False,
                title_font_color="#1B4FD8",
                height=450
            )
 
            with st.container(border=True):
                st.plotly_chart(fig_bar, use_container_width=True)
 
        with chart_col2:
            scatter_data = kpis.dropna(subset=["growth_pct"]).copy()
            hover_col = "product_name" if "product_name" in kpis.columns else prod_col
            fig_scatter = px.scatter(
                scatter_data,
                x="total_revenue", y="growth_pct",
                color="bcg_category",
                color_discrete_map=color_map,
                hover_name=hover_col,
                title="BCG-Inspired Matrix - Revenue vs Growth",
                labels={
                    "total_revenue": "Total Revenue ($)",
                    "growth_pct":    "Growth Rate (%)",
                    "bcg_category":  "BCG Category"
                }
            )
            if growth_median is not None:
                fig_scatter.add_hline(y=growth_median,  line_dash="dot", line_color="#999", line_width=1)
            fig_scatter.add_vline(x=revenue_median, line_dash="dot", line_color="#999", line_width=1)
            fig_scatter.update_layout(
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
                title_font_color="#1B4FD8",
                height=450,
                yaxis=dict(range=[-100, 500]),
                xaxis=dict(range=[0, kpis["total_revenue"].max() * 1.05])
            )
            with st.container(border=True):
                st.plotly_chart(fig_scatter, use_container_width=True)
 
        st.success("✅ BCG analysis complete!")
 
        # ── Save to session_state so filter dropdown doesn't reset results ────
        st.session_state["kpis"]               = kpis
        st.session_state["prod_col"]           = prod_col
        st.session_state["name_col"]           = name_col
        st.session_state["bcg_summary"]        = bcg_summary
        st.session_state["analyzed"]           = True
        st.session_state["growth_unavailable"] = growth_unavailable
 
    # ── Part 5: Product Table + Filter + CSV Download ─────────────────────────
    if st.session_state.get("analyzed") and st.session_state.get("kpis") is not None:
        kpis             = st.session_state["kpis"]
        prod_col         = st.session_state["prod_col"]
        name_col         = st.session_state.get("name_col")
        bcg_summary      = st.session_state["bcg_summary"]
 
        st.markdown("---")
        st.markdown("### Product Details")
 
        categories = ["All"] + sorted(kpis["bcg_category"].unique().tolist())
        selected_cat = st.selectbox("🔍 Filter by BCG Category", categories)
 
        if selected_cat == "All":
            filtered = kpis.copy()
        else:
            filtered = kpis[kpis["bcg_category"] == selected_cat].copy()
 
        # Add loss-making flag to display
        def bcg_label(row):
            label = row["bcg_category"]
            if row["loss_making"]:
                label += " ⚠️"
            return label
 
        filtered = filtered.copy()
        filtered["bcg_display"] = filtered.apply(bcg_label, axis=1)
 
        # Build display columns — show product name if available, keep ID as second col
        rename_map = {
            "total_revenue":     "Total Revenue ($)",
            "total_profit":      "Total Profit ($)",
            "profit_margin_pct": "Margin (%)",
            "growth_pct":        "Growth (%)",
            "bcg_display":       "BCG Category",
        }
 
        if name_col and "product_name" in filtered.columns:
            rename_map["product_name"] = "Product Name"
            rename_map[prod_col]       = "Product ID"
            display_cols = ["Product Name", "Product ID", "BCG Category",
                            "Total Revenue ($)", "Total Profit ($)", "Margin (%)", "Growth (%)"]
        else:
            rename_map[prod_col] = "Product"
            display_cols = ["Product", "BCG Category",
                            "Total Revenue ($)", "Total Profit ($)", "Margin (%)", "Growth (%)"]
 
        display_df = filtered.rename(columns=rename_map)
        display_df = display_df[[c for c in display_cols if c in display_df.columns]]
 
        # Fix money format: negative profit should be -$117.88, not $-117.88
        for col in ["Total Revenue ($)", "Total Profit ($)"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"-${abs(x):,.2f}" if x < 0 else f"${x:,.2f}"
                )
 
        with st.container(border=True):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )
 
        st.caption(f"Showing {len(display_df)} of {len(kpis)} products  |  ⚠️ = loss-making product (negative margin)")
 
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_data,
            file_name="productiq_bcg_results.csv",
            mime="text/csv"
        )
 
        st.success("✅ Analysis complete! Download your results above.")
 
        # ── Part 6: Gemini AI Recommendations ────────────────────────────────
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
 
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            api_key = st.secrets.get("GEMINI_API_KEY", None)
 
        st.markdown("---")
        st.markdown("### 🤖 AI Strategy Recommendations")
 
        if not api_key:
            st.error("GEMINI_API_KEY not found in .env file.")
        else:
            if st.button("✨ Generate AI Recommendations", type="primary"):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.6-flash")
 
                summary_text = ""
                for _, row in bcg_summary.iterrows():
                    summary_text += (
                        f"- {row['BCG Category']}: {row['Products']} products, "
                        f"Avg Revenue ${row['Avg Revenue ($)']:,.2f}, "
                        f"Avg Margin {row['Avg Margin (%)']:.2f}%, "
                        f"Avg Growth {row['Avg Growth (%)']:.2f}%\n"
                    )
 
                prompt = f"""
You are a strategy consultant. Analyze this BCG-inspired portfolio:
 
{summary_text}
 
Return recommendations in EXACTLY this format, only for categories present above:
 
##STARS##
2 sentences of strategy for Stars.
 
##CASH COWS##
2 sentences of strategy for Cash Cows.
 
##HIDDEN GEMS##
2 sentences of strategy for Hidden Gems.
 
##DEAD WEIGHT##
2 sentences of strategy for Dead Weight.
 
##OVERALL##
1 sentence overall portfolio recommendation.
 
Only include sections for categories that exist in the data. Be direct and specific.
"""
                with st.spinner("Generating AI recommendations..."):
                    response = model.generate_content(prompt)
                    st.session_state["ai_response"] = response.text
 
            if st.session_state.get("ai_response"):
                raw = st.session_state["ai_response"]
 
                # Category config — emoji, color, display name
                category_config = {
                    "STARS":       ("⭐", "#1B4FD8", "Stars"),
                    "CASH COWS":   ("🐄", "#0EA5E9", "Cash Cows"),
                    "HIDDEN GEMS": ("💎", "#10B981", "Hidden Gems"),
                    "DEAD WEIGHT": ("⚖️", "#EF4444", "Dead Weight"),
                    "OVERALL":     ("🎯", "#1B4FD8", "Overall Portfolio Strategy"),
                }
 
                # Parse sections from response
                import re
                sections = re.split(r"##([A-Z ]+)##", raw)
 
                parsed = {}
                for i in range(1, len(sections) - 1, 2):
                    key = sections[i].strip()
                    text = sections[i + 1].strip()
                    parsed[key] = text
 
                # Display each section as a colored card
                for key, (emoji, color, label) in category_config.items():
                    if key in parsed:
                        st.markdown(f"""
<div style="
    border-left: 5px solid {color};
    background-color: {color}10;
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 12px;
">
<strong style="color:{color}; font-size:16px;">{emoji} {label}</strong><br><br>
<span style="color:#1a1a1a;">{parsed[key]}</span>
</div>
""", unsafe_allow_html=True)
 
                st.success("✅ AI recommendations generated!")
 