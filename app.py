# -*- coding: utf-8 -*-
"""
Image Viewer and Exporter with Brightness/Contrast Control

A Streamlit web application for viewing and exporting images with adjustable
brightness, contrast, and colormap options.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
from pathlib import Path
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

# Sidebar configuration
st.sidebar.header("📁 File Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload an image file",
    type=["bcrf", "jpg", "jpeg", "png", "bmp", "tiff", "tif"],
    help="Select a BCRF, JPG, PNG, BMP, or TIFF image file"
)

if uploaded_file:
    st.sidebar.success("✓ File loaded")

    # Load image based on file type
    try:
        if uploaded_file.name.endswith(".bcrf"):
            # Load BCRF file
            temp_path = Path(f"/tmp/{uploaded_file.name}")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image, _ = load_bcrf_image(str(temp_path))
        else:
            # Load standard image format
            image = np.array(PILImage.open(uploaded_file))
            # Convert to grayscale if RGB
            if len(image.shape) == 3 and image.shape[2] >= 3:
                image = np.mean(image[:, :, :3], axis=2)

        # Sidebar controls
        st.sidebar.header("⚙️ Adjustments")
        brightness = st.sidebar.slider("Brightness", -100, 100, 0)
        contrast = st.sidebar.slider("Contrast", 0.1, 3.0, 1.0)

        st.sidebar.header("🎨 Display")
        cmap_name = st.sidebar.selectbox(
            "Colormap",
            ["viridis", "plasma", "inferno", "magma", "cividis", "copper", 
             "gray", "hot", "cool", "spring", "summer", "autumn", "winter", 
             "bone", "pink", "RdBu", "seismic"],
            index=6,
        )

        # Apply brightness and contrast
        display_image = image.copy().astype(float)
        
        # Normalize to [0, 1]
        image_min = np.min(display_image)
        image_max = np.max(display_image)
        if image_max > image_min:
            display_image = (display_image - image_min) / (image_max - image_min)
        
        # Apply contrast (centered around 0.5)
        display_image = contrast * (display_image - 0.5) + 0.5
        
        # Apply brightness
        display_image = display_image + brightness / 100.0
        
        # Clip to valid range
        display_image = np.clip(display_image, 0, 1)
        
        # Display image
        st.subheader("Image Preview")
        col_preview, col_spacer = st.columns([2, 1])
        with col_preview:
            fig, ax = plt.subplots(figsize=(6, 6))
            im = ax.imshow(display_image, cmap=cmap_name, vmin=0, vmax=1)
            ax.set_title(uploaded_file.name)
            st.pyplot(fig, use_container_width=False)
            plt.close(fig)

        # Export section
        st.subheader("💾 Export Image")
        export_format = st.radio("Select format:", ["PNG", "TIF", "BMP"], horizontal=True)

        col_export = st.columns(3)
        with col_export[0]:
            if st.button("Download", use_container_width=True, key="export"):
                # Prepare image for export with colormap applied
                export_image_data = display_image.copy()
                export_image_data = (export_image_data - np.min(export_image_data)) / (np.max(export_image_data) - np.min(export_image_data)) * 255
                export_image_data = export_image_data.astype(np.uint8)

                # Apply colormap
                cmap = plt.get_cmap(cmap_name)
                colored_image = cmap(export_image_data / 255.0)
                colored_image_uint8 = (colored_image[:, :, :3] * 255).astype(np.uint8)
                pil_image = PILImage.fromarray(colored_image_uint8, mode="RGB")

                # Save to bytes
                buf = io.BytesIO()
                if export_format == "PNG":
                    pil_image.save(buf, format="PNG")
                    mime = "image/png"
                    ext = "png"
                elif export_format == "TIF":
                    pil_image.save(buf, format="TIFF")
                    mime = "image/tiff"
                    ext = "tif"
                else:  # BMP
                    pil_image.save(buf, format="BMP")
                    mime = "image/bmp"
                    ext = "bmp"
                
                buf.seek(0)

                st.download_button(
                    label=f"⬇️ Download {export_format}",
                    data=buf,
                    file_name=f"{Path(uploaded_file.name).stem}.{ext}",
                    mime=mime,
                    use_container_width=True,
                    key="download_btn",
                )

    except Exception as e:
        st.error(f"❌ Error loading image: {str(e)}")

else:
    st.info("👆 Upload an image file to get started")
