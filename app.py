import pandas as pd
import streamlit as st


# --- Title and description ---
st.set_page_config(page_title="Content Promotion Planner", layout="wide")

st.title("Content Promotion Planner")
st.caption(
    "Explore how budget, moderation capacity and safety thresholds affect which posts get promoted."
)


# --- Load precomputer data ---
@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/decision_system_df.parquet")

df = load_data()


# --- User input ---
st.sidebar.header("Assumptions")

campaign_budget = st.sidebar.number_input("Promotion budget", 0, 100000, 1000, 100)
cost_per_promotion = st.sidebar.number_input("Cost per promotion", 1, 1000, 10, 1)
value_per_success = st.sidebar.number_input("Value per successful promotion", 1, 1000, 25, 1)

max_moderation_budget = st.sidebar.number_input("Moderation budget", 0, 100000, 500, 100)
cost_per_moderation = st.sidebar.number_input("Cost per moderation review", 1, 1000, 5, 1)

review_threshold = st.sidebar.slider("Review threshold", 0.0, 1.0, 0.7, 0.01)
exclude_threshold = st.sidebar.slider("Exclude threshold", 0.0, 1.0, 0.9, 0.01)


# --- Moderation ---

# Safety buckets
def assign_safety_bucket(row):
    if row["safety_prob"] >= exclude_threshold:
        return "Excluded"
    elif row["safety_prob"] >= review_threshold:
        return "Under Review"
    return "Safe"

df = df.copy()
df["safety_bucket"] = df.apply(assign_safety_bucket, axis=1)

excluded_content = df[df["safety_bucket"] == "Excluded"].copy()
moderation_content = df[df["safety_bucket"] == "Under Review"].copy()
safe_content = df[df["safety_bucket"] == "Safe"].copy()

# Moderation capacity
max_review_capacity = int(max_moderation_budget // cost_per_moderation)

to_review = (
    moderation_content
    .sort_values("engagement_prob", ascending=False)
    .head(max_review_capacity)
    .copy()
)

unmoderated_content = moderation_content.drop(to_review.index).copy()

total_moderation_cost = len(to_review) * cost_per_moderation


# --- Promotion planning ---

promotion_slots = int(campaign_budget // cost_per_promotion)
promotion_slots = min(promotion_slots, len(safe_content))

to_promote = (
    safe_content
    .sort_values("engagement_prob", ascending=False)
    .head(promotion_slots)
    .copy()
)

unpromoted_content = safe_content.drop(to_promote.index).copy()

total_promotion_cost = len(to_promote) * cost_per_promotion


# --- Value ---

expected_success = to_promote["engagement_prob"].sum()
expected_value = expected_success * value_per_success
total_cost = total_promotion_cost + total_moderation_cost
net_value = expected_value - total_cost
roi = (net_value / total_cost * 100) if total_cost > 0 else 0

effective_engagement_threshold = (
    to_promote["engagement_prob"].min() if len(to_promote) > 0 else None
)


# --- Display results ---
# Top metrics
st.subheader("Plan summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Promoted", f"{len(to_promote):,}")
col2.metric("Expected successful posts", f"{expected_success:.1f}")
col3.metric("Net value", f"£{net_value:,.2f}")
col4.metric("ROI", f"{roi:.1f}%")

st.divider()

# Detailed sections
left, right = st.columns(2)

with left:
    st.subheader("Content safety")
    st.write(f"Safe: **{len(safe_content):,}**")
    st.write(f"Review candidates: **{len(moderation_content):,}**")
    st.write(f"Reviewed: **{len(to_review):,}**")
    st.write(f"Unreviewed / held back: **{len(unmoderated_content):,}**")
    st.write(f"Excluded: **{len(excluded_content):,}**")

with right:
    st.subheader("Budgets")
    st.write(f"Promotion budget: **£{campaign_budget:,.2f}**")
    st.write(f"Moderation budget: **£{max_moderation_budget:,.2f}**")
    st.write(f"Promotion cost used: **£{total_promotion_cost:,.2f}**")
    st.write(f"Moderation cost used: **£{total_moderation_cost:,.2f}**")
    st.write(f"Unused promotion budget: **£{campaign_budget - total_promotion_cost:,.2f}**")
    st.write(f"Unused moderation budget: **£{max_moderation_budget - total_moderation_cost:,.2f}**")

st.divider()

st.subheader("Promotion decision")

if effective_engagement_threshold is not None:
    st.write(f"Effective engagement threshold: **{effective_engagement_threshold:.3f}**")
else:
    st.write("No posts promoted with these assumptions.")

st.dataframe(
    to_promote[
        ["title", "subreddit", "engagement_prob", "safety_prob", "safety_bucket"]
    ].head(50),
    use_container_width=True
)

with st.expander("Show content held back for moderation"):
    st.dataframe(
        unmoderated_content[
            ["title", "subreddit", "engagement_prob", "safety_prob", "safety_bucket"]
        ].head(50),
        use_container_width=True
    )

with st.expander("Show excluded content"):
    st.dataframe(
        excluded_content[
            ["title", "subreddit", "engagement_prob", "safety_prob", "safety_bucket"]
        ].head(50),
        use_container_width=True
    )

st.caption(
    "Prototype note: scoring is precomputed. This app focuses on the decision layer, not live model inference."
)
