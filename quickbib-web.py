import streamlit as st
from doi2bib3 import fetch_bibtex

# --- Your Custom Function ---
def get_bibtex_for_doi(doi: str):
    try:
        bibtex = fetch_bibtex(doi)
        return True, bibtex, None
    except Exception as e:
        return False, "", str(e)

# --- Streamlit UI Layout ---
st.set_page_config(page_title="DOI to BibTeX", page_icon="📚")

st.title("DOI to BibTeX Converter 📚")
st.markdown("Enter a DOI below to generate the BibTeX entry.")

# Input Field
# We use st.session_state to keep the input stable if the user interacts with other elements
doi_input = st.text_input("Enter DOI", placeholder="10.1038/s41586-020-2649-2")

# Logic Trigger
if doi_input:
    with st.spinner("Fetching data..."):
        # Call your function
        success, bibtex, error_msg = get_bibtex_for_doi(doi_input)

        if success:
            st.success("Citation found!")
            st.markdown("### Output")

            # st.code displays the text with a built-in "Copy to Clipboard" button
            # Look for the small copy icon in the top-right of this block when running
            st.code(bibtex, language='latex')

        else:
            st.error(f"Failed to resolve DOI.")
            with st.expander("See error details"):
                st.write(error_msg)
