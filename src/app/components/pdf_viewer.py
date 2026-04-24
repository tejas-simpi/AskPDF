"""PDF viewer component for the Streamlit app."""
import streamlit as st
import pdfplumber
from pathlib import Path
from typing import List, Optional

def extract_pdf_images(pdf_path: Path) -> List:
    """Extract images from PDF pages."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return [page.to_image().original for page in pdf.pages]
    except Exception as e:
        st.error(f"Error extracting PDF images: {e}")
        return []

def render_pdf_viewer(pdf_pages: Optional[List] = None):
    """Render the PDF viewer with zoom controls and page counter."""
    if pdf_pages:
        total_pages = len(pdf_pages)
        
        # Card header with page counter
        st.markdown(f"""
            <div class="card-header">
                <div class="card-header-title">📄 Document Preview</div>
                <div class="card-header-badge">{total_pages} page{'s' if total_pages != 1 else ''}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # PDF display controls
        zoom_level = st.slider(
            "Zoom Level",
            min_value=100,
            max_value=1000,
            value=700,
            step=50
        )
        
        # Display PDF pages in a styled container
        with st.container(height=410, border=True):
            for page_image in pdf_pages:
                st.image(page_image, width=zoom_level)
    else:
        # Empty state for PDF viewer
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📄</div>
                <div class="empty-state-title">No Document Loaded</div>
                <div class="empty-state-desc">Upload a PDF file to preview it here</div>
            </div>
        """, unsafe_allow_html=True)