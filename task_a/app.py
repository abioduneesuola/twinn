import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL", "http://localhost:8001")

st.set_page_config(
    page_title="Twinn Review Simulator — Task A",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0d0d0d; }
    
    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #ffffff15;
    }
    
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    
    .hero p {
        color: #a0a0b0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #ffffff15;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4ecca3;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #a0a0b0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .review-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #ffffff15;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .review-card h4 {
        color: #4ecca3;
        margin-bottom: 0.5rem;
    }
    
    .tag {
        display: inline-block;
        background: #0f3460;
        color: #4ecca3;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .profile-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #4ecca340;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .stars { color: #ffd700; font-size: 1.2rem; }
    
    .diff-good { color: #4ecca3; font-weight: 600; }
    .diff-bad { color: #ff6b6b; font-weight: 600; }
    
    div[data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #ffffff20;
        background: #1a1a2e;
        color: white;
    }
    
    .sidebar-section {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #ffffff10;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='hero'>
    <h1>🎵 Twinn Review</h1>
    <p>AI-powered review simulation — understanding users deeply enough to write in their voice</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Controls")

    st.markdown("### 👤 User Selection")
    if st.button("🎲 Get Random Users", use_container_width=True):
        with st.spinner("Fetching quality users..."):
            response = requests.get(f"{API_URL}/sample-users?n=8")
            if response.status_code == 200:
                st.session_state.sample_users = response.json().get("users", [])

    if "sample_users" in st.session_state:
        st.markdown("**Click to select a user:**")
        for u in st.session_state.sample_users:
            if st.button(f"👤 {u[:20]}...", key=u, use_container_width=True):
                st.session_state.selected_user = u

    st.divider()
    st.markdown("### ⚙️ Settings")
    n_products = st.slider("Products to simulate", 1, 10, 3)

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    <div style='color: #a0a0b0; font-size: 0.85rem;'>
    Twinn Review analyzes a user's review history to build a behavioral profile, 
    then simulates what they would write about products they haven't reviewed yet.
    </div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    user_id = st.text_input(
        "User ID",
        value=st.session_state.get("selected_user", ""),
        placeholder="e.g. A2TYZ821XXK2YZ — or pick from sidebar",
    )

    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        if not user_id:
            st.error("Please enter or select a User ID")
        else:
            with st.spinner("🧠 Building user profile and simulating reviews..."):
                response = requests.post(f"{API_URL}/simulate", json={
                    "user_id": user_id,
                    "n_products": n_products
                })

            if response.status_code == 200:
                st.session_state.results = response.json()
                st.success("✅ Simulation complete!")
            elif response.status_code == 404:
                st.error(f"❌ {response.json().get('detail')}")
            else:
                st.error(f"❌ Error: {response.json().get('detail')}")

with col2:
    if "results" in st.session_state:
        profile = st.session_state.results.get("profile", {})
        metrics = st.session_state.results.get("metrics", {})
        rmse = metrics.get("rmse", 0)
        diff_class = "diff-good" if rmse < 0.5 else "diff-bad"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value {diff_class}'>{rmse}</div>
            <div class='metric-label'>RMSE</div>
        </div>
        <div class='metric-card'>
            <div class='metric-value'>{metrics.get('total_reviews', 0)}</div>
            <div class='metric-label'>Reviews Simulated</div>
        </div>
        <div class='metric-card'>
            <div class='metric-value'>{metrics.get('high_confidence', 0)}</div>
            <div class='metric-label'>High Confidence</div>
        </div>
        """, unsafe_allow_html=True)

# User Profile Section
if "results" in st.session_state:
    profile = st.session_state.results.get("profile", {})
    st.divider()
    st.markdown("### 👤 User Behavioral Profile")
    st.markdown(f"""
    <div class='profile-card'>
        <span class='tag'>🎭 {profile.get('tone', 'N/A')}</span>
        <span class='tag'>📚 {profile.get('vocabulary_level', 'N/A')}</span>
        <span class='tag'>⭐ {profile.get('rating_pattern', 'N/A')}</span>
        <span class='tag'>📊 Avg: {profile.get('avg_rating', 'N/A')}/5</span>
        <span class='tag'>🎯 {profile.get('topics', 'N/A')}</span>
        <br><br>
        <div style='color: #a0a0b0; font-size: 0.9rem;'>
            <b style='color: white;'>Writing Style:</b> {profile.get('writing_style', 'N/A')}
        </div>
        <div style='color: #a0a0b0; font-size: 0.9rem; margin-top: 0.5rem;'>
            <b style='color: white;'>Common Phrases:</b> {profile.get('common_phrases', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Simulated Reviews
    st.markdown("### 📝 Simulated Reviews")
    raw_reviews = st.session_state.results.get("simulated_reviews", [])
    presented = st.session_state.results.get("presented_reviews", [])

    for i, (raw, presentation) in enumerate(zip(raw_reviews, presented), 1):
        sim_rating = raw.get("simulated_rating", 0)
        act_rating = raw.get("actual_rating", 0)
        diff = abs(sim_rating - act_rating)
        diff_class = "diff-good" if diff <= 0.5 else "diff-bad"
        stars = "⭐" * int(round(sim_rating))

        st.markdown(f"""
        <div class='review-card'>
            <h4>Review {i} — Product: {raw.get('product_id')}</h4>
            <div style='margin-bottom: 1rem;'>
                <span class='tag'>🤖 Simulated: {sim_rating}/5 {stars}</span>
                <span class='tag'>✅ Actual: {act_rating}/5</span>
                <span class='tag {diff_class}'>Δ {diff:.2f}</span>
                <span class='tag'>🎯 {raw.get('confidence', 'N/A')} confidence</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🤖 Simulated Review:**")
            st.markdown(f"> {raw.get('simulated_review', 'N/A')}")
        with col_b:
            st.markdown("**✅ Actual Review (Ground Truth):**")
            st.markdown(f"> {raw.get('actual_review', 'N/A')}")

        st.divider()
