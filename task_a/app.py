import streamlit as st
import requests

API_URL = "http://localhost:8001"

st.set_page_config(
    page_title="Twinn Review Simulator — Task A",
    page_icon="🎵",
    layout="wide"
)

st.markdown("# 🎵 Twinn Review")
st.markdown("*AI-powered review simulation — Task A*")
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Simulate User Reviews")

    # Get sample users
    if st.button("🎲 Get Sample Users"):
        response = requests.get(f"{API_URL}/sample-users?n=10")
        if response.status_code == 200:
            users = response.json().get("users", [])
            st.session_state.sample_users = users

    if "sample_users" in st.session_state:
        st.markdown("**Sample User IDs from dataset:**")
        for u in st.session_state.sample_users:
            st.code(u)

    st.divider()

    user_id = st.text_input(
        "Enter User ID",
        placeholder="e.g. A2TYZ821XXK2YZ",
        help="Enter an Amazon reviewer ID from the dataset"
    )

    n_products = st.slider("Number of products to simulate", 1, 10, 3)

    if st.button("🚀 Simulate Reviews", type="primary"):
        if not user_id:
            st.error("Please enter a User ID")
        else:
            with st.spinner("Running simulation pipeline..."):
                response = requests.post(f"{API_URL}/simulate", json={
                    "user_id": user_id,
                    "n_products": n_products
                })

            if response.status_code == 200:
                data = response.json()
                st.session_state.results = data
            elif response.status_code == 404:
                st.error(f"User not found: {response.json().get('detail')}")
            else:
                st.error(f"Error: {response.json().get('detail')}")

with col2:
    st.markdown("### 📊 Metrics")
    if "results" in st.session_state:
        metrics = st.session_state.results.get("metrics", {})
        st.metric("Total Reviews", metrics.get("total_reviews", 0))
        st.metric("RMSE", metrics.get("rmse", 0))
        st.metric("Avg Rating Error", metrics.get("avg_rating_error", 0))
        st.metric("High Confidence", metrics.get("high_confidence", 0))

        st.divider()
        st.markdown("### 👤 User Profile")
        profile = st.session_state.results.get("profile", {})
        st.markdown(f"**Tone:** {profile.get('tone', 'N/A')}")
        st.markdown(f"**Vocabulary:** {profile.get('vocabulary_level', 'N/A')}")
        st.markdown(f"**Rating Pattern:** {profile.get('rating_pattern', 'N/A')}")
        st.markdown(f"**Avg Rating:** {profile.get('avg_rating', 'N/A')}")
        st.markdown(f"**Topics:** {profile.get('topics', 'N/A')}")
    else:
        st.info("Run a simulation to see metrics")

# Display results
if "results" in st.session_state:
    st.divider()
    st.markdown("### 📝 Simulated Reviews")
    presented = st.session_state.results.get("presented_reviews", [])
    raw = st.session_state.results.get("simulated_reviews", [])

    for i, (presentation, raw_review) in enumerate(zip(presented, raw), 1):
        with st.expander(f"Review {i} — Product: {raw_review.get('product_id')} | Simulated: ⭐{raw_review.get('simulated_rating')} | Actual: ⭐{raw_review.get('actual_rating')}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**🤖 Simulated:**")
                st.write(presentation)
            with col_b:
                st.markdown("**✅ Actual (Ground Truth):**")
                st.write(raw_review.get("actual_review", "N/A"))