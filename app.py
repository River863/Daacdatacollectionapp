import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime

st.set_page_config(page_title="Sample Data Collection App", page_icon="📋", layout="wide")

DATA_FILE = Path("sample_project_data.csv")
ADMIN_CODE = "Daac2026"

def load_data():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_entry(entry):
    df = load_data()
    updated_df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    updated_df.to_csv(DATA_FILE, index=False)

def date_already_exists(selected_date):
    df = load_data()
    if df.empty or "DATE" not in df.columns:
        return False
    return str(selected_date) in df["DATE"].astype(str).values

def create_record_id(selected_date):
    df = load_data()
    prefix = selected_date.strftime("%Y%m%d")
    if df.empty or "RECORD ID" not in df.columns:
        number = 1
    else:
        number = df["RECORD ID"].astype(str).str.startswith(prefix).sum() + 1
    return f"{prefix}-{number:03d}"

st.title("Sample Data Collection App")
st.write("This demo app collects surface temperature data using a structured form.")

entry_tab, admin_tab, export_tab = st.tabs(["Enter Data", "Admin Review", "Export Data"])

with entry_tab:
    st.header("Enter New Data")

    selected_date = st.date_input("Date", value=date.today())

    duplicate_date = date_already_exists(selected_date)
    allow_duplicate = True

    if duplicate_date:
        st.warning("Data already exist for this date.")
        allow_duplicate = st.checkbox("I understand and want to add another entry for this date.")

    with st.form("data_entry_form"):
        time_of_day = st.selectbox("Time of Day", ["", "8a", "9a", "10a", "11a", "12p", "1p", "2p", "3p", "4p", "5p"])

        ambient_air_temperature = st.number_input("Ambient Air Temperature", min_value=-50.0, max_value=150.0, value=None)

        unit = st.selectbox("Unit", ["F", "C"])

        cloud_cover = st.selectbox("Cloud Cover", ["", "No Cloud Cover", "Partial Cloud Cover", "Full Cloud Cover"])

        wind_speed = st.selectbox("Wind Speed", ["", "No Breeze", "Light Breeze", "Moderate Breeze", "Strong Breeze"])

        st.subheader("Surface Temperature Measurements")

        black_aggregate = st.number_input("Black Aggregate / Asphalt", min_value=-50.0, max_value=200.0, value=None)
        light_gray_aggregate = st.number_input("Light Gray Aggregate", min_value=-50.0, max_value=200.0, value=None)
        two_coats_sealant = st.number_input("2 Coats White Cooling Sealant", min_value=-50.0, max_value=200.0, value=None)
        four_coats_sealant = st.number_input("4 Coats White Cooling Sealant", min_value=-50.0, max_value=200.0, value=None)
        dirt = st.number_input("Dirt", min_value=-50.0, max_value=200.0, value=None)
        vegetation = st.number_input("Vegetation", min_value=-50.0, max_value=200.0, value=None)

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Review Entry")

    if submitted:
        errors = []

        if time_of_day == "":
            errors.append("Time of Day is required.")
        if ambient_air_temperature is None:
            errors.append("Ambient Air Temperature is required.")
        if cloud_cover == "":
            errors.append("Cloud Cover is required.")
        if wind_speed == "":
            errors.append("Wind Speed is required.")
        if duplicate_date and not allow_duplicate:
            errors.append("Please confirm duplicate entry.")

        entry = {
            "RECORD ID": create_record_id(selected_date),
            "DATE": str(selected_date),
            "TIME OF DAY": time_of_day,
            "AMBIENT AIR TEMPERATURE": ambient_air_temperature,
            "UNIT": unit,
            "CLOUD COVER": cloud_cover,
            "WIND SPEED": wind_speed,
            "BLACK AGGREGATE / ASPHALT": black_aggregate,
            "LIGHT GRAY AGGREGATE": light_gray_aggregate,
            "2 COATS WHITE COOLING SEALANT": two_coats_sealant,
            "4 COATS WHITE COOLING SEALANT": four_coats_sealant,
            "DIRT": dirt,
            "VEGETATION": vegetation,
            "NOTES": notes,
            "ENTRY TIMESTAMP": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "Needs duplicate review" if duplicate_date else "Active"
        }

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state["pending_entry"] = entry

    if "pending_entry" in st.session_state:
        st.subheader("Review Before Saving")
        st.dataframe(pd.DataFrame([st.session_state["pending_entry"]]), use_container_width=True)

        if st.button("Save Entry"):
            save_entry(st.session_state["pending_entry"])
            del st.session_state["pending_entry"]
            st.success("Entry saved successfully.")
            st.rerun()

with admin_tab:
    st.header("Admin Review")

    admin_code = st.text_input("Admin Code", type="password")

    if admin_code == ADMIN_CODE:
        df = load_data()

        if df.empty:
            st.info("No data have been saved yet.")
        else:
            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

            if st.button("Save Admin Edits"):
                edited_df.to_csv(DATA_FILE, index=False)
                st.success("Admin edits saved.")

            st.subheader("Possible Duplicate Dates")
            duplicate_rows = df[df.duplicated("DATE", keep=False)]
            st.dataframe(duplicate_rows, use_container_width=True)

    elif admin_code:
        st.error("Incorrect admin code.")

with export_tab:
    st.header("Export Data")

    df = load_data()

    if df.empty:
        st.info("No data available to export yet.")
    else:
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="sample_project_data_export.csv",
            mime="text/csv"
        )
