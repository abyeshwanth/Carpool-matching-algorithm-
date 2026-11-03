import streamlit as st
from utils import db, geocode, theme

st.set_page_config(page_title="Offer a Ride", page_icon="🚘", layout="wide")
theme.inject_css()

if st.session_state.get("user") is None:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state.user
st.title("🚘 Offer a Ride")
st.caption("Post your trip so riders heading the same way can find and book it.")

places = geocode.get_all_places()

with st.form("offer_form"):
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Starting From", places, index=0)
        ride_date = st.date_input("Travel Date")
        total_seats = st.slider("Seats Available", 1, 6, 3)
    with col2:
        destination = st.selectbox("Going To", places, index=1)
        ride_time = st.time_input("Departure Time")
        price = st.number_input("Price per Seat (₹)", min_value=0, value=80, step=10)
    submitted = st.form_submit_button("Post Ride", use_container_width=True)

if submitted:
    if source == destination:
        st.error("Source and destination must differ.")
        st.stop()
    src_lat, src_lon = geocode.geocode(source)
    dst_lat, dst_lon = geocode.geocode(destination)
    ride_id = db.create_ride(
        driver_id=user["id"], source=source, destination=destination,
        source_lat=src_lat, source_lon=src_lon, dest_lat=dst_lat, dest_lon=dst_lon,
        ride_date=str(ride_date), ride_time=ride_time.strftime("%H:%M"),
        total_seats=total_seats, price_per_seat=price,
    )
    st.success(f"✅ Ride posted successfully! (Ride ID #{ride_id}) Riders can now find and book it.")

st.divider()
st.subheader("📋 Your Posted Rides")
my_rides = db.get_rides_by_driver(user["id"])
if not my_rides:
    st.info("You haven't posted any rides yet.")
else:
    for r in my_rides:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{r['source']} ➜ {r['destination']}**  \n"
                        f"📅 {r['ride_date']} at {r['ride_time']}  ·  "
                        f"💺 {r['available_seats']}/{r['total_seats']} seats free  ·  "
                        f"₹{r['price_per_seat']}/seat")
            status_color = {"active": "green", "cancelled": "red", "completed": "blue"}.get(r["status"], "purple")
            c2.markdown(theme.badge(r["status"].capitalize(), status_color), unsafe_allow_html=True)
            if r["status"] == "active":
                if c3.button("Cancel Ride", key=f"cancel_{r['id']}"):
                    db.cancel_ride(r["id"])
                    st.rerun()

            bookings = db.get_bookings_for_driver(user["id"])
            ride_bookings = [b for b in bookings if b["ride_id"] == r["id"]]
            if ride_bookings:
                with st.expander(f"👥 {len(ride_bookings)} booking(s) for this ride"):
                    for b in ride_bookings:
                        st.write(f"- {b['rider_name']} ({b['rider_phone']}) · {b['seats_booked']} seat(s) · "
                                 f"Status: {b['status']} · OTP verified: {'✅' if b['otp_verified'] else '❌'}")
