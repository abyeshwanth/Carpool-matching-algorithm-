import streamlit as st
import pandas as pd
from utils import db, theme

st.set_page_config(page_title="Map View", page_icon="🗺️", layout="wide")
theme.inject_css()

if st.session_state.get("user") is None:
    st.warning("Please log in first.")
    st.stop()

st.title("🗺️ Active Rides Map")
st.caption("Pickup points (blue) and drop points (red) for all currently active rides.")

rides = db.get_active_rides()
if not rides:
    st.info("No active rides to display.")
    st.stop()

rows = []
for r in rides:
    rows.append({"lat": r["source_lat"], "lon": r["source_lon"], "type": "Pickup",
                 "label": f"{r['source']} (Driver: {r['driver_name']})"})
    rows.append({"lat": r["dest_lat"], "lon": r["dest_lon"], "type": "Drop",
                 "label": f"{r['destination']} (Driver: {r['driver_name']})"})

df = pd.DataFrame(rows)
st.map(df, latitude="lat", longitude="lon", size=60)

st.divider()
st.subheader("Active Rides List")
for r in rides:
    st.write(f"🔵 **{r['source']}** ➜ 🔴 **{r['destination']}** · Driver: {r['driver_name']} "
             f"· {r['ride_date']} {r['ride_time']} · {r['available_seats']} seats left")
