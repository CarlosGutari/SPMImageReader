# -*- coding: utf-8 -*-
"""
Image Viewer and Exporter with Brightness/Contrast Control

A Streamlit web application for viewing and exporting images with adjustable
brightness, contrast, and colormap options.
"""

import io
import tempfile
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image as PILImage

from bcrf_utils import load_bcrf_image


# Set page configuration
st.set_page_config(
    page_title="Image Viewer & Exporter",
    page_icon="🖼️",
    layout="wide",
)

st.title("🖼️ Image Viewer & Exporter")
st.markdown("Open images, adjust brightness/contrast, and export with colormaps")


def load_image_from_upload(uploaded_file):
    """Load an uploaded image from a standard file or a BCRF archive."""
    if uploaded_file.name.endswith(".bcrf"):
        temp_path = Path(tempfile.gettempdir()) / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        image, _ = load_bcrf_image(str(temp_path))
        return image

    uploaded_file.seek(0)
    image = np.array(PILImage.open(uploaded_file))
    if len(image.shape) == 3 and image.shape[2] >= 3:
        image = np.mean(image[:, :, :3], axis=2)
    return image


def apply_preview_settings(image, brightness, contrast):
    """Apply brightness and contrast adjustments to an image array."""
    display_image = image.copy().astype(float)

    image_min = np.min(display_image)
    image_max = np.max(display_image)
    if image_max > image_min:
        display_image = (display_image - image_min) / (image_max - image_min)

    display_image = contrast * (display_image - 0.5) + 0.5
    display_image = display_image + brightness / 100.0
    return np.clip(display_image, 0, 1)


def build_export_image(display_image, cmap_name):
    """Convert the adjusted preview image to a colored PIL image for export."""
    export_image_data = display_image.copy()
    export_image_data = (
        (export_image_data - np.min(export_image_data))
        / (np.max(export_image_data) - np.min(export_image_data))
        * 255
    )
    export_image_data = export_image_data.astype(np.uint8)

    cmap = plt.get_cmap(cmap_name)
    colored_image = cmap(export_image_data / 255.0)
    colored_image_uint8 = (colored_image[:, :, :3] * 255).astype(np.uint8)
    return PILImage.fromarray(colored_image_uint8, mode="RGB")


def export_image_bytes(pil_image, export_format):
    """Serialize a PIL image to bytes in the requested format."""
    buf = io.BytesIO()
    if export_format == "PNG":
        pil_image.save(buf, format="PNG")
        return buf, "image/png", "png"
    if export_format == "TIF":
        pil_image.save(buf, format="TIFF")
        return buf, "image/tiff", "tif"
    pil_image.save(buf, format="BMP")
    return buf, "image/bmp", "bmp"


# Sidebar configuration
st.sidebar.header("📁 File Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more image files",
    type=["bcrf", "jpg", "jpeg", "png", "bmp", "tiff", "tif"],
    accept_multiple_files=True,
    help="Select one or more BCRF, JPG, PNG, BMP, or TIFF image files",
)

if uploaded_files:
    st.sidebar.success(f"✓ {len(uploaded_files)} file(s) loaded")

    try:
        image_names = [uploaded_file.name for uploaded_file in uploaded_files]
        selected_image_name = st.sidebar.selectbox(
            "Select image for preview",
            image_names,
            index=0,
        )
        selected_file = next(
            uploaded_file for uploaded_file in uploaded_files if uploaded_file.name == selected_image_name
        )

        image = load_image_from_upload(selected_file)

        # Sidebar controls
        st.sidebar.header("⚙️ Adjustments")
        brightness = st.sidebar.slider("Brightness", -100, 100, 0)
        contrast = st.sidebar.slider("Contrast", 0.1, 3.0, 1.0)

        st.sidebar.header("🎨 Display")
        cmap_name = st.sidebar.selectbox(
            "Colormap",
            [
                "viridis",
                "plasma",
                "inferno",
                "magma",
                "cividis",
                "copper",
                "gray",
                "hot",
                "cool",
                "spring",
                "summer",
                "autumn",
                "winter",
                "bone",
                "pink",
                "RdBu",
                "seismic",
            ],
            index=6,
        )

        display_image = apply_preview_settings(image, brightness, contrast)

        # Display image
        st.subheader("Image Preview")
        col_preview, col_spacer = st.columns([2, 1])
        with col_preview:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(display_image, cmap=cmap_name, vmin=0, vmax=1)
            ax.set_title(selected_file.name)
            st.pyplot(fig, use_container_width=False)
            plt.close(fig)

        # Export section
        st.subheader("💾 Export Image")
        st.caption("The same brightness, contrast, and colormap settings are used for every image in the batch export.")
        export_format = st.radio("Select format:", ["PNG", "TIF", "BMP"], horizontal=True)

        export_image = build_export_image(display_image, cmap_name)
        buf, mime, ext = export_image_bytes(export_image, export_format)
        buf.seek(0)

        st.download_button(
            label=f"⬇️ Download {export_format}",
            data=buf,
            file_name=f"{Path(selected_file.name).stem}.{ext}",
            mime=mime,
            use_container_width=True,
            key="download_btn",
        )

        st.divider()
        st.subheader("📦 Batch Export")
        batch_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(batch_zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for uploaded_file in uploaded_files:
                image_to_export = load_image_from_upload(uploaded_file)
                display_image_to_export = apply_preview_settings(image_to_export, brightness, contrast)
                export_image_to_export = build_export_image(display_image_to_export, cmap_name)
                image_buf, _, image_ext = export_image_bytes(export_image_to_export, export_format)
                archive.writestr(
                    f"{Path(uploaded_file.name).stem}.{image_ext}",
                    image_buf.getvalue(),
                )
        batch_zip_buffer.seek(0)

        st.download_button(
            label=f"⬇️ Download ZIP ({len(uploaded_files)} images)",
            data=batch_zip_buffer,
            file_name=f"processed_images.{export_format.lower()}.zip",
            mime="application/zip",
            use_container_width=True,
            key="batch_download_btn",
        )

    except Exception as e:
        st.error(f"❌ Error loading image: {str(e)}")

else:
    st.info("👆 Upload one or more image files to get started")
