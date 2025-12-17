#
# Copyright(c) [2025] Advanced Micro Devices, Inc. All rights reserved.
#
from PIL import Image
from cucim import CuImage
import demo_cpu_transforms as cputrfs
import demo_gpu_transforms as gputrfs
import demo_utils as utility
from demo_tooltips import tooltips
import matplotlib.pyplot as plt
import cupy as cp
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import io
import time
import os.path

# Set page layout to wide mode
st.set_page_config(layout="wide")

# Header section for documentation
with open('demo_header.md', 'r') as header_md:
    content = header_md.read()
st.markdown(content, unsafe_allow_html=True)

# Initialize session states for tracking performance
if 'gpu_times' not in st.session_state:
    st.session_state['gpu_times'] = []
if 'cpu_times' not in st.session_state:
    st.session_state['cpu_times'] = []
if 'operation_count' not in st.session_state:
    st.session_state['operation_count'] = 0
if 'last_operation_caption' not in st.session_state:
    st.session_state['last_operation_caption'] = None

# Load WSI into CuImage 
tiff_path = "sample_images/77917-ome_base.tif"
thumbnail = "downsampled_images/77917-ome_base-800x_.jpg"
thumbwidth = 800
wsi = CuImage(tiff_path)
img_width, img_height = wsi.shape[1], wsi.shape[0]
if 'spacing_x' not in st.session_state:
    st.session_state['spacing_x'] = wsi.metadata['cucim']['spacing'][1]  # YXC order: spacing[1] is X
if 'spacing_y' not in st.session_state:
    st.session_state['spacing_y'] = wsi.metadata['cucim']['spacing'][0]  # spacing[0] is Y
if 'unit_x' not in st.session_state:
    st.session_state['unit_x'] = utility.unit_map.get(wsi.metadata['cucim']['spacing_units'][1])
if 'unit_y' not in st.session_state:
    st.session_state['unit_y'] = utility.unit_map.get(wsi.metadata['cucim']['spacing_units'][0])
if 'gpu_tile' not in st.session_state:
    st.session_state['gpu_tile'] = None
if 'cpu_tile' not in st.session_state:
    st.session_state['cpu_tile'] = None

# Generate the thumbnail from the WSI
with st.spinner('Generating thumbnail... Please wait.'):
    utility.generate_wsi_thumbnail(tiff_path, thumbnail, thumbwidth)

# Load downsampled JPEG thumbnail
thumb_img = Image.open(thumbnail).convert("RGB")
thumb_img.thumbnail((thumbwidth, thumbwidth), Image.Resampling.LANCZOS)
thumb_np = np.asarray(thumb_img)
thumb_width, thumb_height = thumb_img.size

# Compute applicable scaling
scale_x = thumb_width / img_width
scale_y = thumb_height / img_height

# Calculate initial position at the center
initial_x = img_width // 2
initial_y = img_height // 2

# Sidebar - Control Panel
with open('demo_sidebar.md', 'r') as sidebar_md:
    content = sidebar_md.read()
st.sidebar.markdown(content, unsafe_allow_html=True)

tile_size = st.sidebar.slider(
    "Tile Size", 
    int(min(128, img_width/2, img_height/2)), 
    int(min(4096, img_width/2, img_height/2)), 
    128, 
    help=tooltips['tile_size']
)

x = st.sidebar.slider(
    "X position", 
    0, 
    img_width - tile_size, 
    initial_x, 
    step=32,
    help=tooltips['x_position']
)

y = st.sidebar.slider(
    "Y position", 
    0, 
    img_height - tile_size, 
    initial_y, 
    step=32,
    help=tooltips['y_position']
)

# Transformation Categories
with st.sidebar.expander("Stain Separation"):
    stain_option = st.radio("Select Stain", (None, 'Eosin', 'Hematoxylin', 'DAB'), help=tooltips['stain_option'])

with st.sidebar.expander("Feature Extraction"):
    gabor = st.checkbox("Gabor Filter", help=tooltips['gabor'])
    sobel = st.checkbox("Edge Detection (sobel)", help=tooltips['sobel'])

with st.sidebar.expander("Morphology"):
    dilation = st.checkbox("Binary Dilation", help=tooltips['dilation'])
    smallobjs = st.checkbox("Remove Small Objects", help=tooltips['smallobjs'])

with st.sidebar.expander("Geometric Transformations"):
    rotate = st.checkbox("Rotate", help=tooltips['rotate'])
    warp = st.checkbox("Warp", help=tooltips['warp'])

# Execute all selected transformations on the GPU
def transform_tile_gpu(tile):
    # Apply stain separation
    if stain_option:
        tile = gputrfs.stain_separation(tile, stain_option)

    # Apply Gabor filters, if selected
    if gabor:
        tile = gputrfs.gabor_filter(tile)

    # Apply Sobel edge detection, if selected
    if sobel:
        tile = gputrfs.sobel_edge(tile)

    # Apply morphology
    if dilation:
        tile = gputrfs.dilation(tile)
    if smallobjs:
        tile = gputrfs.erase_small_objects(tile)

    # Apply geometric transformations
    if rotate:
        tile = gputrfs.rotate_patch(tile)
    if warp:
        tile = gputrfs.affine_warp(tile)

    # Update operation count only if any operations performed
    if stain_option or gabor or sobel or dilation or smallobjs or rotate or warp:
        st.session_state['operation_count'] += 1

    # Return the final tile post all GPU transformations
    return cp.asnumpy(tile)

# Execute all selected transformations on the CPU
def transform_tile_cpu(tile):
    # Apply stain separation
    if stain_option:
        tile = cputrfs.stain_separation(tile, stain_option)

    # Apply Gabor filters, if selected
    if gabor:
        tile = cputrfs.gabor_filter(tile)

    # Apply Sobel edge detection, if selected
    if sobel:
        tile = cputrfs.sobel_edge(tile)

    # Apply morphology
    if dilation:
        tile = cputrfs.dilation(tile)
    if smallobjs:
        tile = cputrfs.erase_small_objects(tile)

    # Apply geometric transformations
    if rotate:
        tile = cputrfs.rotate_patch(tile)
    if warp:
        tile = cputrfs.affine_warp(tile)

    # Return the final tile post all CPU transformations
    return tile 

# Main Layout
col_main, col_perf = st.columns([5, 1])
with col_main:
    def display_thumbnail_with_grid(x, y, tile_size):
        # --- Step 1: Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

        ax.imshow(thumb_np)
        ax.set_xticks(np.arange(0, thumb_width, step=100))
        ax.set_yticks(np.arange(0, thumb_height, step=100))
        ax.grid(color='gray', linestyle='--', linewidth=0.5)

        for i in ax.get_xticks():
            ax.text(i, -15, str(int(i / scale_x)), ha='center', va='center', fontsize=6)
        for j in ax.get_yticks():
            ax.text(-15, j, str(int(j / scale_y)), ha='right', va='center', fontsize=6)

        rect = plt.Rectangle((x * scale_x, y * scale_y),
                             tile_size * scale_x, tile_size * scale_y,
                             linewidth=2, edgecolor='red', facecolor='none')
        ax.add_patch(rect)

        ax.text(-80, thumb_height / 2, "Thumbnail Map", va='center', ha='center',
                rotation='vertical', fontsize=12)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        plt.axis('on')

        # --- Step 2: Save figure to PNG buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        plt.close(fig)

        # --- Step 3: Resize the image using PIL
        image = Image.open(buf)
        max_height = 300
        aspect_ratio = image.width / image.height
        new_size = (int(max_height * aspect_ratio), max_height)
        image = image.resize(new_size)

        # --- Step 4: Display in Streamlit with container width
        st.image(image, use_container_width=True)

    # Display CuImage metadata
    def display_metadata(image):
        # Get details of the image
        size_h = utility.filesize_h(image.path)
        width, height = image.shape[1], image.shape[0]
        pixel_type = utility.dl_datatype_to_str(image.dtype)
        width_physical = width * st.session_state['spacing_x']
        height_physical = height * st.session_state['spacing_y']

        data = {
            "Metadata": [
                "Filename", 
                "Image file size", 
                "Image width (phys.)", 
                "Image height (phys.)",
                "Image device", 
                "Pixel type", 
                "No. of dimensions [channels]"
            ],
            "Value": [
                f"{image.path}", 
                f"{size_h}",
                f"{width}px ({width_physical:.2f} {st.session_state['unit_x']})", 
                f"{height}px ({height_physical:.2f} {st.session_state['unit_y']})",
                f"{image.device}",
                f"{pixel_type}",
                f"{image.ndim} {image.channel_names}"
            ]
        }
        
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Display Tiles Side-by-Side
    def display_tiles(x, y):
        # Track GPU timing
        tstart = time.time()

        # Read the tile on GPU
        st.session_state['gpu_tile'] = wsi.read_region((x, y), 
                                                       (tile_size, tile_size), 
                                                       device="cuda")
        tile_gpu_np = cp.asnumpy(st.session_state['gpu_tile'])

        # Execute selected transformations on the GPU
        transformed_gpu = transform_tile_gpu(st.session_state['gpu_tile'])
        transformed_gpu_np = cp.asnumpy(transformed_gpu)

        # Track GPU time
        gpu_time = time.time() - tstart
        st.session_state['gpu_times'].append(gpu_time)

        # Track CPU timing
        tstart = time.time()

        # Shadow the same operations on CPU
        st.session_state['cpu_tile'] = wsi.read_region((x, y), 
                                                       (tile_size, tile_size))
        transformed_cpu = transform_tile_cpu(st.session_state['cpu_tile'])
        transformed_cpu_np = np.asarray(transformed_cpu)

        # Track CPU time
        cpu_time = time.time() - tstart
        st.session_state['cpu_times'].append(cpu_time)

        # Layout the display
        wsi_tile, cpu_tile, gpu_tile = st.columns(3)
        with wsi_tile:
            st.image(tile_gpu_np, 
                     caption="Original Tile", 
                     use_container_width=True, 
                     clamp=True)
        
        with cpu_tile:
            st.image(transformed_cpu_np, 
                     caption="Transformed Tile (CPU)", 
                     use_container_width=True, 
                     clamp=True)

        with gpu_tile:
            st.image(transformed_gpu_np, 
                     caption="Transformed Tile (GPU)", 
                     use_container_width=True, 
                     clamp=True)

    # Display the thumbnail along with some metadata
    thumb, metadata = st.columns([1.5, 1])

    # Display the patch tiles
    # Ensure this is done *before* accessing metadata below
    display_tiles(x, y)

    with thumb:
        # Call Functions to Update Display
        display_thumbnail_with_grid(x, y, tile_size)

    with metadata:
        # Tabify metadata for the original WSI, GPU tile and CPU tile
        wsi_intro, wsi_meta, gpu_meta, cpu_meta = st.tabs([
                                                "**Whole Slide Image (WSI)**",
                                                "**WSI Metadata**", 
                                                "**GPU Tile Metadata**", 
                                                "**CPU Tile Metadata**"
                                               ])
        with wsi_intro:
            # Introduce the WSI
            with open('demo_wsi_intro.md', 'r') as wsi_intro_md:
                content = wsi_intro_md.read()
                st.markdown(content, unsafe_allow_html=True)

        with wsi_meta:
            # Display metadata of the WSI
            display_metadata(wsi)

        with gpu_meta:
            if st.session_state['gpu_tile'] is not None:
                display_metadata(st.session_state['gpu_tile'])
            else:
                st.markdown("Region tile not loaded yet...")

        with cpu_meta:
            if st.session_state['cpu_tile'] is not None:
                display_metadata(st.session_state['cpu_tile'])
            else:
                st.markdown("Region tile not loaded yet...")

# Right Pane for Performance Metrics
with col_perf:
    with open('demo_performance.md', 'r') as perf_md:
        content = perf_md.read()
    st.markdown(content, unsafe_allow_html=True)

    # Placeholder for last operation details using st.empty
    last_operation_placeholder = st.empty()

    # Compose categorical selection as caption
    def categorical_caption(caption, category, flag_text_pairs):
        values = [text for flag, text in flag_text_pairs if flag]
        if values:
            caption += f"<br>{category}: {', '.join(values)}\n"
        return caption

    # Display Latest Operation using st.empty
    with last_operation_placeholder.container():
        # Caption all operations performed
        caption = ""
        if stain_option: caption += f"<br>Stain Separation: {stain_option}"
        caption = categorical_caption(caption, "Feature Extraction", [(gabor, "Gabor"), (sobel, "Sobel")])
        caption = categorical_caption(caption, "Morphology", [(dilation, "Binary Dilation"), 
                                                              (smallobjs, "Remove Small Objects"),
                                                             ])
        caption = categorical_caption(caption, "Geometric", [(rotate, "Rotate"), 
                                                             (warp, "Warp"),
                                                            ])

        # In case nothing was selected, create special caption
        if caption != "":
            caption = f"<em><b>Last Operation(s)</b></em>" + caption
            st.session_state['last_operation_caption'] = caption

        # Display performance graph
        if st.session_state['operation_count']:
            # Get latest times for the last operation
            latest_gpu = st.session_state['gpu_times'][-1]
            latest_cpu = st.session_state['cpu_times'][-1]
            last_ratio = latest_cpu / latest_gpu

            # Cumulative times
            total_gpu_time = sum(st.session_state['gpu_times'])
            total_cpu_time = sum(st.session_state['cpu_times'])
            cumulative_ratio = total_cpu_time / total_gpu_time

            # Create a bar chart
            labels = ['']
            data_values = [last_ratio]
            colors = ['orange']

            fig = go.Figure()

            # Add last operation bars
            fig.add_trace(go.Bar(
                x=labels,
                y=data_values,
                name='GPU Speedup',
                orientation='v',
                marker_color=colors
            ))

            # Update layout
            fig.update_layout(
                barmode='group',  # Bars appear side-by-side
                height=300,
                title=dict(
                    text=(""),
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(
                        family="Arial, sans-serif",
                        size=12,
                    )
                ),
                # Caption the last operation details
                xaxis_title=dict(
                    text=(st.session_state['last_operation_caption']),
                    font=dict(
                        family="Arial, sans-serif",
                        size=8,
                    )
                ),
                yaxis_title='Performance Speedup (GPU vs. CPU)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig)

        else:
            # Create a blank bar chart
            labels = ['']
            data_values = []
            colors = ['orange']

            fig = go.Figure()

            # Add last operation bars
            fig.add_trace(go.Bar(
                x=labels,
                y=data_values,
                name='GPU Speedup',
                orientation='v',
                marker_color=colors
            ))

            # Update layout
            fig.update_layout(
                barmode='group',  # Bars appear side-by-side
                height=300,
                title=dict(
                    text=(""),
                    x=0.5,
                    xanchor='center',
                    yanchor='top',
                    font=dict(
                        family="Arial, sans-serif",
                        size=12,
                    )
                ),
                # Caption the last operation details
                xaxis_title=dict(
                    text="",
                    font=dict(
                        family="Arial, sans-serif",
                        size=8,
                    )
                ),
                yaxis_title='Performance Speedup (GPU vs. CPU)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig)

        # Footer
        cpu_details = utility.get_cpu_info()
        gpu_details = utility.get_gpu_info()
        hipcim_details = utility.get_package_version("amd-hipcim")
        st.markdown(f"<strong><u><small>Powered By</small></u></strong><br>"
                    f"<small><strong>CPU:</strong> {cpu_details}<br>"
                    f"<strong>GPU:</strong> {gpu_details}<br>"
                    f"<strong>hipCIM:</strong> {hipcim_details}</small>",
                    unsafe_allow_html=True
        )
        st.markdown("---")
        with open('demo_footer.md', 'r') as footer_md:
            content = footer_md.read()
        st.markdown(content, unsafe_allow_html=True)

