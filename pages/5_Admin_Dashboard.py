import streamlit as st
import pandas as pd
import plotly.express as px
from utils import db, theme

st.set_page_config(page_title="Admin Dashboard", page_icon="⚙️", layout="wide")
theme.inject_css()

user = st.session_state.get("user")
if user is None:
    st.warning("Please log in first.")
    st.stop()
if user["role"] != "admin":
    st.error("🚫 Access restricted to admin accounts only.")
    st.stop()

st.title("⚙️ Admin Dashboard")

stats = db.get_stats()
c1, c2, c3, c4 = st.columns(4)
theme.metric_card("Total Users", stats["users"], "👥", "purple", col=c1)
theme.metric_card("Total Rides", stats["rides"], "🚘", "blue", col=c2)
theme.metric_card("Active Rides", stats["active_rides"], "🟢", "green", col=c3)
theme.metric_card("Total Bookings", stats["bookings"], "🎫", "orange", col=c4)

st.write("")

users = db.get_all_users()
rides = db.get_all_rides()
bookings = db.get_all_bookings()

chart_c1, chart_c2 = st.columns(2)
with chart_c1:
    st.subheader("👥 Users by Role")
    if users:
        df_u = pd.DataFrame(users)
        role_counts = df_u["role"].value_counts().reset_index()
        role_counts.columns = ["Role", "Count"]
        fig = px.pie(role_counts, names="Role", values="Count", hole=0.5,
                     color_discrete_sequence=["#7F5AF0", "#F5576C", "#4FACFE", "#43E97B"])
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#312E81"))
        st.plotly_chart(fig, use_container_width=True)

with chart_c2:
    st.subheader("🚘 Ride Status")
    if rides:
        df_r = pd.DataFrame(rides)
        status_counts = df_r["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig2 = px.bar(status_counts, x="Status", y="Count", color="Status", text="Count",
                      color_discrete_sequence=["#43E97B", "#FF6B6B", "#4FACFE"])
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#312E81"), yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig2, use_container_width=True)

if bookings:
    st.subheader("🧠 Match Score Distribution")
    df_b = pd.DataFrame(bookings)
    if "match_score" in df_b.columns and df_b["match_score"].notna().any():
        fig3 = px.histogram(df_b, x="match_score", nbins=20,
                             color_discrete_sequence=["#7F5AF0"])
        fig3.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#312E81"),
                           xaxis_title="Match Score (%)", yaxis_title="Bookings")
        st.plotly_chart(fig3, use_container_width=True)

st.divider()
tab_users, tab_rides, tab_bookings = st.tabs(["👥 Users", "🚘 Rides", "🎫 Bookings"])

with tab_users:
    df = pd.DataFrame(users)
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab_rides:
    df = pd.DataFrame(rides)
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab_bookings:
    df = pd.DataFrame(bookings)
    st.dataframe(df, use_container_width=True, hide_index=True)
