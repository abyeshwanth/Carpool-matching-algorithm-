"""
app.py - Main entry point for the AI Carpool Matching System (Streamlit).

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import db, auth, seed, theme

st.set_page_config(page_title="AI Carpool Matcher", page_icon="🚗", layout="wide")
theme.inject_css()

# ---- init db + seed demo data on first run ----
db.init_db()
seed.seed_if_empty()

if "user" not in st.session_state:
    st.session_state.user = None


def show_login_signup():
    st.markdown("""
    <div class="hero-banner">
        <h1>🚗 AI Carpool Matching System</h1>
        <p>🤖 K-Means zone clustering + 🧠 AI-based match scoring for smarter, greener carpooling</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = auth.login(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
        st.caption("Demo accounts (password: `password123`): admin@carpool.com, driver1@example.com, rider1@example.com")

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email_s = st.text_input("Email", key="signup_email")
            phone = st.text_input("Phone Number")
            role = st.selectbox("I want to sign up as", ["rider", "driver"])
            password_s = st.text_input("Password", type="password", key="signup_pw")
            confirm = st.text_input("Confirm Password", type="password")
            submitted_s = st.form_submit_button("Create Account", use_container_width=True)
            if submitted_s:
                if not (name and email_s and password_s):
                    st.error("Please fill in all required fields.")
                elif password_s != confirm:
                    st.error("Passwords do not match.")
                else:
                    uid = auth.signup(name, email_s, password_s, phone, role)
                    if uid:
                        st.success("Account created! Please log in from the Login tab.")
                    else:
                        st.error("An account with that email already exists.")

    st.write("")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown(theme.badge("🤖 K-Means Clustering", "purple"), unsafe_allow_html=True)
    with b2:
        st.markdown(theme.badge("🧠 AI Match Scoring", "pink"), unsafe_allow_html=True)
    with b3:
        st.markdown(theme.badge("📍 Haversine Distance", "blue"), unsafe_allow_html=True)
    with b4:
        st.markdown(theme.badge("🎫 OTP Verified Rides", "green"), unsafe_allow_html=True)


def show_dashboard():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {user['name']}")
        st.caption(f"Role: **{user['role'].capitalize()}**  ·  ⭐ {user['rating']:.1f}")
        st.divider()
        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/1_Find_a_Ride.py", label="🔍 Find a Ride")
        st.page_link("pages/2_Offer_a_Ride.py", label="🚘 Offer a Ride")
        st.page_link("pages/3_My_Bookings.py", label="📜 My Bookings / History")
        st.page_link("pages/4_Map_View.py", label="🗺️ Map View")
        if user["role"] == "admin":
            st.page_link("pages/5_Admin_Dashboard.py", label="⚙️ Admin Dashboard")
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.title("🚗  Carpool Matching System")
    stats = db.get_stats()

    c1, c2, c3, c4 = st.columns(4)
    theme.metric_card("Total Users", stats["users"], "👥", "purple", col=c1)
    theme.metric_card("Rides Posted", stats["rides"], "🚘", "blue", col=c2)
    theme.metric_card("Active Rides", stats["active_rides"], "🟢", "green", col=c3)
    theme.metric_card("Total Bookings", stats["bookings"], "🎫", "orange", col=c4)

    st.write("")
    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        st.subheader("📊 Platform Activity")
        activity_df = pd.DataFrame({
            "Metric": ["Users", "Rides Posted", "Active Rides", "Bookings"],
            "Count": [stats["users"], stats["rides"], stats["active_rides"], stats["bookings"]],
        })
        fig = px.bar(
            activity_df, x="Metric", y="Count", color="Metric", text="Count",
            color_discrete_sequence=["#7F5AF0", "#4FACFE", "#43E97B", "#FA8231"],
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(
            showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10), yaxis_title=None, xaxis_title=None,
            font=dict(color="#312E81"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("⭐ Match Weight Breakdown")
        weights_df = pd.DataFrame({
            "Factor": ["Route Match", "Time Compat.", "Proximity", "Seats", "Rating"],
            "Weight": [35, 25, 20, 10, 10],
        })
        fig2 = go.Figure(data=[go.Pie(
            labels=weights_df["Factor"], values=weights_df["Weight"], hole=0.55,
            marker=dict(colors=["#7F5AF0", "#F5576C", "#4FACFE", "#43E97B", "#FA8231"]),
            textinfo="label+percent",
        )])
        fig2.update_layout(
            showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#312E81"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🧠 How the matching engine works")

    step_cols = st.columns(3)
    with step_cols[0]:
        st.markdown(f"""
        <div class="metric-card" style="background:linear-gradient(135deg,#7F5AF0,#A78BFA); min-height:150px;">
            <div class="m-label">Step 1</div>
            <div style="font-size:1.05rem;font-weight:700;margin:6px 0;">📍 K-Means Clustering</div>
            <div style="font-size:0.88rem;opacity:0.95;">Groups all posted rides into geographic zones based on
            pickup location, so a new request is only compared against nearby rides.</div>
        </div>""", unsafe_allow_html=True)
    with step_cols[1]:
        st.markdown(f"""
        <div class="metric-card" style="background:linear-gradient(135deg,#F5576C,#F093FB); min-height:150px;">
            <div class="m-label">Step 2</div>
            <div style="font-size:1.05rem;font-weight:700;margin:6px 0;">🧠 AI Match Score</div>
            <div style="font-size:0.88rem;opacity:0.95;">Ranks candidates using a weighted blend of route,
            time, proximity, seats, and driver rating — see the chart above.</div>
        </div>""", unsafe_allow_html=True)
    with step_cols[2]:
        st.markdown(f"""
        <div class="metric-card" style="background:linear-gradient(135deg,#43E97B,#38F9D7); min-height:150px;">
            <div class="m-label">Step 3</div>
            <div style="font-size:1.05rem;font-weight:700;margin:6px 0;">🎫 Book Instantly</div>
            <div style="font-size:0.88rem;opacity:0.95;">Use 🔍 Find a Ride (rider) or 🚘 Offer a Ride (driver)
            from the sidebar to get started right away.</div>
        </div>""", unsafe_allow_html=True)


if st.session_state.user is None:
    show_login_signup()
else:
    show_dashboard()
