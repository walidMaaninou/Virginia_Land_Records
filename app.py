import streamlit as st
import pandas as pd
import time
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
max_pages = st.sidebar.selectbox("Maximum Pages", options=list(range(1, 101)), index=2)

if st.sidebar.button("Start Scraping"):
    if not email or not password:
        st.sidebar.error("Please enter both email and password.")
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

        page_count = 0
        for page_results in search_names(token, search_term="aa", max_pages=max_pages):
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
