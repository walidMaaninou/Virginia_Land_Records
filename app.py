import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from auth import get_access_token
from search import search_names
from details import get_instr_details
from pdf import download_pdf_to_file
from ocr import extract_addresses_from_pdf

st.set_page_config(page_title="📄 Virginia Records Scraper", layout="wide")
st.title("📥 Virginia Land Records Address Extractor")

# === Sidebar Inputs ===
st.sidebar.header("🔐 Login")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

date_range_option = st.sidebar.selectbox(
    "Search From",
    options=["7 days", "1 month", "2 months", "3 months"],
    index=1
)

INSTR_TYPE_CODE_MAP = {
    "AFFIDAVIT": "AF     ",
    "DEED TRANSFER ON DEATH": "DTD    ",
    "DEED PURSUANT TO DIVORCE": "DPD    ",
    "DIVORCE DECREE": "DD     ",
    "MECHANICS LIEN": "LM     ",
    "MEMORANDUM OF LIEN": "MEML   ",
    "NOTICE OF LIEN": "NL     ",
    "NOTICE OF LIS PENDENS": "NLP    ",
    "NOTICE": "NOT    ",
    "ORDER-DECREE BANKRUPTCY W/PLAT": "ODRB-PL",
    "REAL ESTATE AFFIDAVIT": "REA    ",
    "WILL": "WILL   "
}

instr_type_options = [
    "AFFIDAVIT", "DEED TRANSFER ON DEATH", "DEED PURSUANT TO DIVORCE",
    "DIVORCE DECREE", "MECHANICS LIEN", "MEMORANDUM OF LIEN",
    "NOTICE OF LIEN", "NOTICE OF LIS PENDENS", "NOTICE",
    "ORDER-DECREE BANKRUPTCY W/PLAT", "REAL ESTATE AFFIDAVIT", "WILL"
]

selected_instr_types = st.sidebar.multiselect("Instrument Types", instr_type_options)

if st.sidebar.button("Start Scraping"):
    if not email or not password:
        st.sidebar.error("Please enter both email and password.")
    elif not selected_instr_types:
        st.sidebar.error("Please select at least one Instrument Type.")
    else:
        st.session_state["scraping"] = True

# === Main App Logic ===
if st.session_state.get("scraping", False):
    status_placeholder = st.empty()
    table_placeholder = st.empty()

    rows = []
    seen_urowids = set()

    try:
        status_placeholder.info("🔐 Connecting to Virginia Court System...")
        token = get_access_token(email, password)

        today = datetime.today()
        if date_range_option == "7 days":
            from_date = today - timedelta(days=7)
        elif date_range_option == "1 month":
            from_date = today - timedelta(days=30)
        elif date_range_option == "2 months":
            from_date = today - timedelta(days=60)
        else:
            from_date = today - timedelta(days=90)

        to_date_str = today.strftime("%m/%d/%Y")
        from_date_str = from_date.strftime("%m/%d/%Y")

        page_count = 0
        instr_codes = [INSTR_TYPE_CODE_MAP[name] for name in selected_instr_types]

        for page_results in search_names(token, search_term="aa", max_pages=100, instr_types=instr_codes, from_date=from_date_str, to_date=to_date_str):
            page_count += 1
            status_placeholder.info(f"🔍 Searching page {page_count}...")

            for entry in page_results:
                name = entry["name"]
                status_placeholder.info(f"➡️ Fetching urowid for: {name}")

                details = get_instr_details(
                    token,
                    search_name=entry["name"],
                    count=entry["count"],
                    business=entry["business"],
                    nameflag=entry["nameflag"],
                    original_term="aa"
                )

                for d in details:
                    urowid = d["urowid"]
                    if urowid in seen_urowids:
                        continue
                    seen_urowids.add(urowid)

                    try:
                        filepath = download_pdf_to_file(
                            token=token,
                            urowid=urowid,
                            instr_group=d["instr_group"],
                            fips=d["fips"],
                            verified=d.get("verified", "VER")
                        )
                        status_placeholder.info(f"📄 OCR on: {urowid}")
                        addresses = extract_addresses_from_pdf(filepath, st.secrets["OPENAI_API_KEY"])

                        rows.append({
                            "Instrument Type": d["instr_type"].strip(),
                            "Grantee": d.get("reverseParty", "-").strip(),
                            "Extracted Address": addresses[0] if addresses else "-"
                        })

                        table_placeholder.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    except Exception as e:
                        rows.append({
                            "Instrument Type": d["instr_type"].strip(),
                            "Grantee": d.get("reverseParty", "-").strip(),
                            "Extracted Address": f"Error: {e}"
                        })
                        table_placeholder.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        status_placeholder.success("✅ Scraping completed!")

    except Exception as e:
        status_placeholder.error(f"❌ Error: {e}")

    st.session_state["scraping"] = False
