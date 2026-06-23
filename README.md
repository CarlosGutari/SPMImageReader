# SPM BCRF Image Viewer & Exporter

A modern Streamlit web application for viewing and exporting BCRF image files from Bruker Scanning Probe Microscopy (SPM) devices.

## Features

- 📂 **File Upload**: Upload BCRF image files directly
- 🎨 **Customizable Visualization**: Choose from 15+ colormaps (viridis, copper, hot, etc.)
- 📊 **Image Statistics**: View min, max, mean, and standard deviation
- 📈 **Normalization Options**: Linear or log scale visualization
- 💾 **Multi-format Export**:
  - PNG (with colorbar and labels)
  - NumPy (.npy) for scientific computing
  - CSV for spreadsheet applications
- 📐 **Image Processing**: Compute gradients and generate histograms
- 🔍 **Metadata Viewer**: Access BCRF header information

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup

1. Navigate to the project directory:
```bash
cd SPMImagesWebApp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Application

1. **Upload a BCRF File**: Click "Browse files" in the sidebar and select a BCRF image
2. **Adjust Display**: 
   - Select a colormap from the dropdown
   - Choose between Linear or Log Scale normalization
3. **View Information**:
   - Image statistics appear on the right panel
   - Expand "View Header Information" to see metadata
4. **Export Data**:
   - Click "Export as PNG" for a visualization-ready image
   - Click "Export as NPY" for NumPy array format
   - Click "Export as CSV" for spreadsheet compatibility
5. **Process Image**:
   - Compute gradients to analyze image edges
   - View histogram for intensity distribution analysis

## Project Structure

```
SPMImagesWebApp/
├── app.py                      # Main Streamlit application
├── bcrf_utils.py              # BCRF file handling utilities
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── BCRFReadTest.py            # Original test script (reference)
└── Before_000 GF.bcrf         # Example BCRF file
```

## Module Documentation

### bcrf_utils.py

Provides utilities for reading and processing BCRF files:

#### Functions

- **`read_bcrf_file(filename, header_size=4096, width=256, height=256)`**
  - Reads BCRF file header and raw data
  - Returns: tuple of (header_dict, raw_data)

- **`convert_data_to_float(data, dtype=np.float32)`**
  - Converts binary data to float array
  - Returns: numpy array of floats

- **`load_bcrf_image(filename, width=256, height=256)`**
  - Complete image loading with automatic reshaping
  - Returns: tuple of (image_2d_array, metadata_dict)

- **`get_image_statistics(image)`**
  - Calculates image statistics (min, max, mean, std)
  - Returns: dictionary with statistics

## BCRF File Format

BCRF files from Bruker SPM devices have the following structure:

- **Header** (4096 bytes): UTF-16 encoded key=value pairs
- **Image Data** (262,144 bytes): 256×256 pixels of 32-bit floats
- **Total Size**: 266,240 bytes (minimum)

### Example Header Fields

Common metadata includes:
- Device information
- Scan parameters
- Calibration data
- Timestamp
- User notes

## Troubleshooting

### "Error reading BCRF file"
- Ensure the file is a valid BCRF image
- Check that file permissions allow reading
- Verify file size is at least 266KB

### "Error reshaping image data"
- The file may have non-standard dimensions
- Try modifying the `width` and `height` parameters in `bcrf_utils.py`

### App won't start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python 3.7+ is being used

## Dependencies

- **streamlit**: Web application framework
- **numpy**: Numerical computations
- **matplotlib**: Visualization and image rendering
- **pillow**: Image processing (optional, used for compatibility)

## Tips & Best Practices

1. **Large Images**: The app is optimized for 256×256 images. Larger images may impact performance.
2. **Log Scale**: Use log scale normalization to better visualize images with wide intensity ranges.
3. **Export Format Selection**:
   - **PNG**: For reports and presentations
   - **NPY**: For scientific analysis and further processing
   - **CSV**: For data manipulation in Excel or statistical software
4. **Gradient Analysis**: Useful for identifying surface features and edges

## Original Code

The original test code from `BCRFReadTest.py` has been refactored into:
- **Extracted utilities** in `bcrf_utils.py` with improved error handling
- **Modern UI** in `app.py` with Streamlit framework
- **Production-ready code** with type hints and documentation

## License

This project is provided as-is for research and analysis purposes.

## Support

For issues or questions, refer to:
- [Streamlit Documentation](https://docs.streamlit.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
