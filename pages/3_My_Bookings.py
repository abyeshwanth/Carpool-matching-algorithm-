import streamlit as st
from utils import db, theme

st.set_page_config(page_title="My Bookings", page_icon="📜", layout="wide")
theme.inject_css()

if st.session_state.get("user") is None:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state.user
st.title("📜 My Bookings & Ride History")

tab_rider, tab_driver = st.tabs(["🎫 As Rider", "🚘 As Driver"])

with tab_rider:
    bookings = db.get_bookings_by_rider(user["id"])
    if not bookings:
        st.info("You have no bookings yet. Go to 'Find a Ride' to book one!")
    for b in bookings:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            status_color = {"booked": "orange", "completed": "green", "cancelled": "red"}.get(b["status"], "purple")
            c1.markdown(f"**{b['source']} ➜ {b['destination']}**  "
                        + theme.badge(b['status'].capitalize(), status_color), unsafe_allow_html=True)
            c1.markdown(f"👤 Driver: {b['driver_name']}  ·  📅 {b['ride_date']} at {b['ride_time']}  \n"
                        f"💺 {b['seats_booked']} seat(s)  ·  🧠 Match Score: {b['match_score']}%")
            with c2:
                if not b["otp_verified"]:
                    st.info(f"OTP: **{b['otp']}**")
                    otp_input = st.text_input("Enter OTP to verify pickup", key=f"otp_{b['id']}")
                    if st.button("Verify Pickup", key=f"verify_{b['id']}"):
                        if db.verify_otp(b["id"], otp_input):
                            st.success("Pickup verified!")
                            st.rerun()
                        else:
                            st.error("Incorrect OTP.")
                else:
                    st.success("✅ Ride completed")
                    with st.popover("Rate driver"):
                        score = st.slider("Rating", 1, 5, 5, key=f"rate_{b['id']}")
                        comment = st.text_input("Comment (optional)", key=f"comment_{b['id']}")
                        if st.button("Submit Rating", key=f"submit_rate_{b['id']}"):
                            db.add_rating(b["id"], user["id"], b["driver_id"], score, comment)
                            st.success("Thanks for your feedback!")

with tab_driver:
    driver_bookings = db.get_bookings_for_driver(user["id"])
    if not driver_bookings:
        st.info("No riders have booked your rides yet.")
    for b in driver_bookings:
        with st.container(border=True):
            st.markdown(f"**{b['source']} ➜ {b['destination']}**  \n"
                        f"👤 Rider: {b['rider_name']} ({b['rider_phone']})  ·  "
                        f"📅 {b['ride_date']} at {b['ride_time']}  \n"
                        f"💺 {b['seats_booked']} seat(s)  ·  Status: **{b['status']}**  ·  "
                        f"OTP Verified: {'✅' if b['otp_verified'] else '❌ (ask rider for OTP: ' + str(b['otp']) + ')'}")
