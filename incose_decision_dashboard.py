
import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="INCOSE India – Decision Support System",
    layout="wide"
)

st.title("INCOSE India – Survey Decision Support System")
st.caption("Outcomes • Insights • Risks • Strategic Direction")

# =====================================================
# FILE UPLOAD
# =====================================================
file = st.file_uploader(
    "Upload INCOSE India Survey Excel File",
    type=["xlsx"]
)

# Initialize df defensively
df = None

if file is None:
    st.info("Please upload the INCOSE India survey Excel file to proceed.")
    st.stop()

# =====================================================
# LOAD DATA
# =====================================================
try:
    # Explicit engine for .xlsx
    df = pd.read_excel(file, engine="openpyxl")
except Exception as e:
    st.error("Failed to read the Excel file.")
    st.exception(e)
    st.stop()

if df is None or df.empty:
    st.error("The uploaded file contains no data.")
    st.stop()

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================
df.columns = (
    df.columns.astype(str)
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)
)

st.success("Survey data loaded successfully")

# =====================================================
# SAFE COLUMN DETECTION
# =====================================================
def find_column(keywords):
    """
    Return the first column whose lowercased name contains *all* keywords.
    """
    for col in df.columns:
        col_lower = col.lower()
        if all(k in col_lower for k in keywords):
            return col
    return None

membership_col  = find_column(["incose", "member"])   # e.g., "Are you an INCOSE member?"
confidence_col  = find_column(["decide"])             # e.g., "What would help you decide?"
expectation_col = find_column(["valuable"])           # e.g., "What would be valuable in 2026?"
domain_col      = find_column(["domain"])             # e.g., "Domain"

missing = []
if membership_col is None:
    missing.append("Membership")
if confidence_col is None:
    missing.append("Decision / Confidence")
if expectation_col is None:
    missing.append("Expectations")
if domain_col is None:
    missing.append("Domain")

if missing:
    st.error(
        "Required columns not found:\n\n" +
        "\n".join(f"- {m}" for m in missing)
    )
    st.stop()

# =====================================================
# DOMAIN FILTER
# =====================================================
st.subheader("🔍 Filter by Domain")

domains = ["All"] + sorted(pd.Series(df[domain_col]).dropna().astype(str).unique().tolist())
selected_domain = st.selectbox("Select Domain", domains)

if selected_domain != "All":
    df = df[df[domain_col].astype(str) == selected_domain]

if df.empty:
    st.warning("No responses available for the selected domain.")
    st.stop()

# =====================================================
# KEY OUTCOMES
# =====================================================
st.header("📌 Key Outcomes")

col1, col2, col3 = st.columns(3)

col1.metric("Total Responses", len(df))

col2.metric(
    "Existing INCOSE Members",
    df[membership_col].astype(str)
      .str.contains("yes", case=False, na=False).sum()
)

col3.metric(
    "Need ASEP / CSEP Guidance",
    df[confidence_col].astype(str)
      .str.contains("ASEP|CSEP", case=False, na=False).sum()
)

# =====================================================
# DISTRIBUTIONS
# =====================================================
st.header("📊 Survey Distributions")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Membership Status")
    st.bar_chart(
        df[membership_col].astype(str).value_counts(),
        use_container_width=True
    )

with c2:
    st.subheader("Domain Representation")
    st.bar_chart(
        df[domain_col].astype(str).value_counts(),
        use_container_width=True
    )

st.subheader("What Members Expect from INCOSE (2026)")
st.bar_chart(
    df[expectation_col].astype(str).value_counts(),
    use_container_width=True
)

# =====================================================
# RELATIONSHIPS
# =====================================================
st.header("🔗 Domain vs Membership Status")

relationship_df = pd.crosstab(
    df[domain_col].astype(str),
    df[membership_col].astype(str)
)

st.dataframe(relationship_df, use_container_width=True)

# =====================================================
# KEY INSIGHTS
# =====================================================
st.header("💡 Key Insights")

domain_counts = df[domain_col].astype(str).value_counts()
expect_counts = df[expectation_col].astype(str).value_counts()

top_domain = domain_counts.idxmax() if not domain_counts.empty else "N/A"
top_expectation = expect_counts.idxmax() if not expect_counts.empty else "N/A"

st.markdown(f"""
### Insight Summary
- **Most represented domain:** {top_domain}
- **Top expectation for 2026:** {top_expectation}
- Most non-members are seeking **clarity, not awareness**
- **Certification pathway guidance** is the strongest conversion lever
""")

# =====================================================
# RISKS & 🟢 OPPORTUNITIES
# =====================================================
st.header("⚠️ Risks & 🟢 Opportunities")

risks = []
opportunities = []

asep_count = df[confidence_col].astype(str).str.contains(
    "ASEP|CSEP", case=False, na=False
).sum()

if asep_count > 10:
    risks.append(
        "Lack of structured ASEP/CSEP guidance may delay membership conversion"
    )

if df[membership_col].astype(str).str.contains(
    "exploring|decide", case=False, na=False
).sum() > 8:
    opportunities.append(
        "High near-term conversion potential with targeted follow-up"
    )

if "Healthcare" in domain_counts.head(3).index.tolist():
    opportunities.append(
        "Healthcare domain shows strong potential for focused INCOSE initiatives"
    )

col_risk, col_opp = st.columns(2)

with col_risk:
    st.subheader("🔴 Risks")
    if risks:
        for r in risks:
            st.write(f"- {r}")
    else:
        st.write("No critical risks identified.")

with col_opp:
    st.subheader("🟢 Opportunities")
    if opportunities:
        for o in opportunities:
            st.write(f"- {o}")
    else:
        st.write("No major opportunities identified.")

# =====================================================
# STRATEGIC RECOMMENDATIONS
# =====================================================
st.header("🧭 Strategic Recommendations")

recommendations = [
    "Launch a structured ASEP/CSEP guidance program with clear timelines",
    "Create domain-focused engagement tracks starting with Healthcare",
    "Introduce mentorship-driven certification enablement",
    "Position INCOSE membership as a career credential",
    "Develop employer-facing material highlighting certification ROI",
    "Repeat this survey annually to track engagement trends"
]

for i, rec in enumerate(recommendations, 1):
    st.write(f"{i}. {rec}")

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================
st.header("📄 Executive Summary")

if st.button("Generate Executive Summary"):
    summary = f"""
Executive Summary – INCOSE India Survey

Total Responses: {len(df)}
Most Represented Domain: {top_domain}
Primary Member Expectation (2026): {top_expectation}

Key Findings:
- Strong interest exists, but clarity gaps slow conversion
- Certification guidance is the strongest decision driver
- Domain-specific engagement improves perceived value

Strategic Direction:
INCOSE India should shift toward certification-led,
domain-focused professional enablement.
"""
    st.text_area("Executive Summary Output", summary, height=300)

# =====================================================
# RAW DATA
# =====================================================
with st.expander("📂 View Raw Data"):
    st.dataframe(df, use_container_width=True)
