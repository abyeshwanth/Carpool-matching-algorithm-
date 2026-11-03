import streamlit as st
from utils import db, geocode, matching, clustering, theme

st.set_page_config(page_title="Find a Ride", page_icon="🔍", layout="wide")
theme.inject_css()

if st.session_state.get("user") is None:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state.user
st.title("🔍 Find a Ride")
st.caption("Enter your trip details and let the AI matching engine rank the best available rides for you.")

places = geocode.get_all_places()

with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Pickup Location", places, index=places.index("Koramangala") if "Koramangala" in places else 0)
        ride_date = st.date_input("Travel Date")
    with col2:
        destination = st.selectbox("Drop Location", places, index=places.index("Whitefield") if "Whitefield" in places else 1)
        ride_time = st.time_input("Preferred Time")
    seats_needed = st.slider("Seats Needed", 1, 4, 1)
    submitted = st.form_submit_button("🧠 Find AI-Matched Rides", use_container_width=True)

# ---------------------------------------------------------------------
# When the search form is submitted, run clustering + matching ONCE and
# stash everything needed to render results & handle bookings into
# session_state. This is essential: clicking "Book This Ride" below
# triggers a Streamlit rerun, and on that rerun `submitted` is False
# again (the form wasn't re-submitted) — without session_state the
# whole results list would disappear before the booking could show
# any confirmation, which is why booking looked like it "did nothing".
# ---------------------------------------------------------------------
if submitted:
    if source == destination:
        st.error("Pickup and drop locations must be different.")
        st.stop()

    src_lat, src_lon = geocode.geocode(source)
    dst_lat, dst_lon = geocode.geocode(destination)

    search_request = {
        "source_lat": src_lat, "source_lon": src_lon,
        "dest_lat": dst_lat, "dest_lon": dst_lon,
        "ride_date": str(ride_date), "ride_time": ride_time.strftime("%H:%M"),
        "seats_needed": seats_needed,
    }

    active_rides = db.get_active_rides()

    if not active_rides:
        st.session_state.search_results = None
        st.session_state.search_info = None
        st.info("No active rides available right now. Check back later!")
        st.stop()

    # --- K-Means clustering step: narrow candidate pool to nearby zones ---
    model, ride_cluster_map = clustering.build_zone_clusters(active_rides, n_clusters=min(5, len(active_rides)))
    req_cluster = clustering.predict_cluster(model, src_lat, src_lon)
    neighbor_clusters = clustering.get_cluster_neighbors(model, src_lat, src_lon, ride_cluster_map, top_k=3)

    candidates = [r for r in active_rides if ride_cluster_map.get(r["id"]) in neighbor_clusters]
    if not candidates:
        candidates = active_rides  # fallback: search everything

    # --- AI match scoring step ---
    ranked = matching.rank_matches(candidates, search_request, min_score=20.0)

    # Persist everything needed to render results + process a booking later
    st.session_state.search_results = ranked
    st.session_state.search_info = {
        "source": source, "destination": destination,
        "src_lat": src_lat, "src_lon": src_lon,
        "dst_lat": dst_lat, "dst_lon": dst_lon,
        "ride_date": str(ride_date), "ride_time": ride_time.strftime("%H:%M"),
        "seats_needed": seats_needed,
        "req_cluster": req_cluster,
        "n_active": len(active_rides),
        "n_candidates": len(candidates),
    }
    st.session_state.pop("booking_confirmation", None)

# ---------------------------------------------------------------------
# Render results from session_state (persists across the rerun that a
# "Book This Ride" click causes).
# ---------------------------------------------------------------------
ranked = st.session_state.get("search_results")
info = st.session_state.get("search_info")

# Show a booking confirmation banner if a booking just happened
if st.session_state.get("booking_confirmation"):
    conf = st.session_state.booking_confirmation
    st.success(f"✅ Ride booked! Your OTP is **{conf['otp']}** — share it with the driver to verify pickup.")
    st.balloons()
    st.session_state.pop("booking_confirmation", None)

if ranked is not None and info is not None:
    if not ranked:
        st.warning("No good matches found for this route/time. Try a different time or location.")
    else:
        st.caption(f"📍 K-Means placed your request in zone **{info['req_cluster']}** — "
                   f"searching {info['n_candidates']} of {info['n_active']} rides in nearby zones.")
        st.success(f"Found {len(ranked)} matching ride(s), ranked by AI match score:")

        for item in ranked:
            ride = item["ride"]
            score = item["score"]
            total = score["total_score"]
            if total >= 75:
                tier_color, tier_label = "green", "Excellent Match"
            elif total >= 50:
                tier_color, tier_label = "blue", "Good Match"
            else:
                tier_color, tier_label = "orange", "Fair Match"

            # Re-check live seat count in case another booking changed it since search
            live_ride = db.get_ride(ride["id"]) or ride

            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{ride['source']} ➜ {ride['destination']}**  "
                                + theme.badge(tier_label, tier_color), unsafe_allow_html=True)
                    st.caption(f"👤 Driver: {ride['driver_name']}  ·  ⭐ {ride['driver_rating']:.1f}  ·  "
                               f"📅 {ride['ride_date']} at {ride['ride_time']}  ·  "
                               f"💺 {live_ride['available_seats']} seats left  ·  ₹{ride['price_per_seat']}/seat")
                    with st.expander("Match score breakdown"):
                        b1, b2, b3, b4, b5 = st.columns(5)
                        theme.metric_card("Route", f"{score['route_match']}%", "🛣️", "purple", col=b1)
                        theme.metric_card("Time", f"{score['time_compatibility']}%", "🕐", "pink", col=b2)
                        theme.metric_card("Proximity", f"{score['pickup_proximity']}%", "📍", "blue", col=b3)
                        theme.metric_card("Seats", f"{score['seat_availability']}%", "💺", "green", col=b4)
                        theme.metric_card("Rating", f"{score['driver_rating']}%", "⭐", "orange", col=b5)
                with c2:
                    theme.metric_card("AI Match Score", f"{total}%", "🧠", tier_color)

                    already_booked_key = f"booked_flag_{ride['id']}"
                    if st.session_state.get(already_booked_key):
                        st.info("✅ Booked")
                    elif live_ride["available_seats"] < info["seats_needed"]:
                        st.button("Not Enough Seats", key=f"book_{ride['id']}", use_container_width=True, disabled=True)
                    else:
                        if st.button("Book This Ride", key=f"book_{ride['id']}", use_container_width=True):
                            request_id = db.create_request(
                                rider_id=user["id"], source=info["source"], destination=info["destination"],
                                source_lat=info["src_lat"], source_lon=info["src_lon"],
                                dest_lat=info["dst_lat"], dest_lon=info["dst_lon"],
                                ride_date=info["ride_date"], ride_time=info["ride_time"],
                                seats_needed=info["seats_needed"],
                            )
                            booking_id, otp = db.create_booking(
                                ride["id"], user["id"], info["seats_needed"], total, request_id
                            )
                            st.session_state.booking_confirmation = {"booking_id": booking_id, "otp": otp}
                            st.session_state[already_booked_key] = True
                            st.rerun()
else:
    st.info("Use the form above to search for AI-matched rides.")
