import altair as alt
import pandas as pd
import streamlit as st


# -----------------------------
# PAGE SETUP
# -----------------------------

st.set_page_config(page_title="Promotions Planner", layout="wide")

st.title("Promotions Planner")

st.info(
    """
This tool helps decide which content to promote by balancing expected engagement with safety.

It uses precomputed model scores, removes risky content, then promotes the highest-engagement safe posts within budget.
"""
)


# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/decision_system_df.parquet")


df = load_data().copy()


# -----------------------------
# SIDEBAR INPUTS
# -----------------------------

st.sidebar.header("Planning assumptions")

promotion_budget = st.sidebar.number_input("Promotion budget", 0, 100000, 1000, 100)
cost_per_promotion = st.sidebar.number_input("Cost per promotion", 1, 1000, 10, 1)
value_per_success = st.sidebar.number_input("Value per successful promotion", 1, 1000, 25, 1)

safety_threshold = st.sidebar.slider(
    "Maximum acceptable safety risk",
    min_value=0.0,
    max_value=1.0,
    value=0.70,
    step=0.01,
)


# -----------------------------
# DECISION LOGIC
# -----------------------------

# Content is considered safe if its predicted safety risk is below the threshold.
df["content_status"] = df["safety_prob"].apply(
    lambda x: "Safe" if x < safety_threshold else "Excluded"
)

safe_content = df[df["content_status"] == "Safe"].copy()
excluded_content = df[df["content_status"] == "Excluded"].copy()

promotion_slots = int(promotion_budget // cost_per_promotion)

to_promote = (
    safe_content
    .sort_values("engagement_prob", ascending=False)
    .head(promotion_slots)
    .copy()
)

unpromoted_safe_content = safe_content.drop(to_promote.index).copy()

total_promotion_cost = len(to_promote) * cost_per_promotion
unused_promotion_budget = promotion_budget - total_promotion_cost

expected_success = to_promote["engagement_prob"].sum()
expected_value = expected_success * value_per_success
net_value = expected_value - total_promotion_cost

roi = (
    net_value / total_promotion_cost * 100
    if total_promotion_cost > 0
    else 0
)

expected_success_rate = (
    expected_success / len(to_promote) * 100
    if len(to_promote) > 0
    else 0
)

promotion_budget_used_pct = (
    total_promotion_cost / promotion_budget * 100
    if promotion_budget > 0
    else 0
)

effective_engagement_threshold = (
    to_promote["engagement_prob"].min()
    if len(to_promote) > 0
    else None
)


# -----------------------------
# RECOMMENDED PLAN
# -----------------------------

st.subheader("Recommended plan")

if len(to_promote) == 0:
    st.error("No posts meet the current safety threshold.")
elif net_value <= 0:
    st.warning(
        f"This plan promotes {len(to_promote):,} posts, but expected ROI is weak. "
        "Try reducing spend or increasing the expected value per successful promotion."
    )
else:
    st.success(
        f"Promote {len(to_promote):,} safe posts. "
        f"Expected outcome: {expected_success:.1f} successful posts and {roi:.1f}% ROI."
    )

col1, col2, col3, col4 = st.columns(4)

col1.metric("Spend", f"£{total_promotion_cost:,.0f}")
col2.metric("Expected value", f"£{expected_value:,.0f}")
col3.metric("Net value", f"£{net_value:,.0f}")
col4.metric("ROI", f"{roi:.1f}%")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Posts promoted", f"{len(to_promote):,}")
col2.metric("Expected successes", f"{expected_success:.1f}")
col3.metric("Expected success rate", f"{expected_success_rate:.1f}%")
col4.metric("Budget used", f"{promotion_budget_used_pct:.0f}%")


# -----------------------------
# WHAT THIS MEANS
# -----------------------------

st.subheader("What this means")

st.markdown(
    f"""
This plan filters out content above the safety risk threshold, then promotes the strongest remaining posts.

- **{len(safe_content):,} posts** are safe enough to consider.
- **{len(to_promote):,} posts** are selected for promotion.
- **{len(unpromoted_safe_content):,} safe posts** are not promoted because the budget runs out first.
- **{len(excluded_content):,} posts** are excluded because their safety risk is too high.
- **£{unused_promotion_budget:,.0f}** promotion budget remains unused.
"""
)


# -----------------------------
# PLAN VISUALS
# -----------------------------

st.subheader("Plan at a glance")

value_df = pd.DataFrame(
    {
        "Metric": ["Spend", "Expected value", "Net value"],
        "Amount": [total_promotion_cost, expected_value, net_value],
    }
)

value_chart = (
    alt.Chart(value_df)
    .mark_bar()
    .encode(
        x=alt.X("Amount:Q", title="£"),
        y=alt.Y("Metric:N", title=None, sort=None),
        color=alt.Color(
            "Metric:N",
            scale=alt.Scale(
                domain=["Spend", "Expected value", "Net value"],
                range=["#b0b0b0", "#b0b0b0", "#2ca02c"]
            ),
            legend=None
        ),
        tooltip=[
            "Metric:N",
            alt.Tooltip("Amount:Q", format=",.0f", title="Amount (£)"),
        ],
    )
    .properties(height=180)
)

st.altair_chart(value_chart, use_container_width=True)


classification_df = pd.DataFrame(
    {
        "Content status": [
            "Promoted",
            "Safe but not promoted",
            "Excluded",
        ],
        "Posts": [
            len(to_promote),
            len(unpromoted_safe_content),
            len(excluded_content),
        ],
    }
)

classification_chart = (
    alt.Chart(classification_df)
    .mark_arc(innerRadius=60)
    .encode(
        theta=alt.Theta("Posts:Q"),
        color=alt.Color("Content status:N", title="Content status"),
        tooltip=[
            "Content status:N",
            alt.Tooltip("Posts:Q", format=","),
        ],
    )
    .properties(height=320)
)

st.altair_chart(classification_chart, use_container_width=True)


# -----------------------------
# RECOMMENDED CONTENT TABLE
# -----------------------------

st.subheader("Recommended content")

display_cols = [
    "title",
    "subreddit",
    "engagement_prob",
    "safety_prob",
    "content_status",
]

promoted_display_df = to_promote[display_cols].copy()

promoted_display_df = promoted_display_df.rename(
    columns={
        "title": "Post title",
        "subreddit": "Subreddit",
        "engagement_prob": "Engagement score",
        "safety_prob": "Safety risk",
        "content_status": "Status",
    }
)

st.dataframe(
    promoted_display_df.head(50),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Engagement score": st.column_config.NumberColumn(format="%.3f"),
        "Safety risk": st.column_config.NumberColumn(format="%.3f"),
    },
)


# -----------------------------
# EXPANDERS
# -----------------------------

with st.expander("Show excluded content"):
    excluded_display_df = excluded_content[display_cols].copy()

    excluded_display_df = excluded_display_df.rename(
        columns={
            "title": "Post title",
            "subreddit": "Subreddit",
            "engagement_prob": "Engagement score",
            "safety_prob": "Safety risk",
            "content_status": "Status",
        }
    )

    st.dataframe(
        excluded_display_df.head(50),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Engagement score": st.column_config.NumberColumn(format="%.3f"),
            "Safety risk": st.column_config.NumberColumn(format="%.3f"),
        },
    )


with st.expander("View technical details and definitions"):
    threshold_text = (
        f"{effective_engagement_threshold:.3f}"
        if effective_engagement_threshold is not None
        else "N/A"
    )

    st.markdown(
        f"""
### How the planner works

1. **Safety filter:** remove content with predicted safety risk above `{safety_threshold:.2f}`.
2. **Engagement ranking:** rank the remaining safe content by predicted engagement.
3. **Budget allocation:** promote the highest-ranked safe posts until the promotion budget runs out.

### Definitions

- **Engagement score:** Predicted likelihood that a post will perform successfully.
- **Safety risk:** Predicted likelihood that a post may be unsafe or unsuitable for promotion.
- **Safety threshold:** Maximum safety risk the plan is willing to accept.
- **Effective engagement threshold:** Engagement score of the lowest-ranked promoted post.

### Current settings

- **Promotion budget:** £{promotion_budget:,.0f}
- **Cost per promotion:** £{cost_per_promotion:,.0f}
- **Promotion slots available:** {promotion_slots:,}
- **Safety threshold:** {safety_threshold:.2f}
- **Effective engagement threshold:** {threshold_text}
- **Total content assessed:** {len(df):,}
"""
    )


st.caption(
    "Prototype note: scoring is precomputed. This app demonstrates a simple decision layer on top of model outputs."
)
