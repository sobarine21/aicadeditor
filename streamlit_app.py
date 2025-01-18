import streamlit as st
import numpy as np
import random
import string
from io import BytesIO
from stl import mesh
import tempfile
import re

# NLP library for improved dimension extraction (optional)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except ImportError:
    st.warning("spaCy library not found. Using simpler dimension extraction.")
    nlp = None

# Streamlit App UI
st.title("AI CAD Design Generator")
st.write("Use generative AI to create CAD designs from your description.")

# Prompt input field
prompt = st.text_area("Describe the design you want (e.g., 'Create a box with length 10mm, width 5mm, and height 15mm.')")

# Define available shapes
shapes = ['box', 'sphere', 'cone', 'pyramid', 'cylinder', 'torus', 'custom']

# Dropdown for shape selection
shape_type = st.selectbox("Choose a shape for your design:", shapes)

# Additional design parameters
color = st.color_picker("Pick a color for the design:", "#FF5733")
material = st.selectbox("Choose a material type:", ["Plastic", "Metal", "Wood", "Glass", "Rubber", "Concrete", "Carbon Fiber", "Aluminum", "Copper", "Stone"])
smooth_surface = st.checkbox("Smooth Surface?", value=False)
hollow = st.checkbox("Hollow Structure?", value=False)

# Advanced Features
texture = st.selectbox("Choose a texture:", ["Matte", "Glossy", "Metallic", "Transparent", "Fabric", "Wooden", "Stone", "Leather", "Grainy", "Smooth"])
grid_resolution = st.slider("Set Grid Resolution", min_value=10, max_value=100, value=50)
add_round_edges = st.checkbox("Add rounded edges?", value=False)
enable_symmetry = st.checkbox("Enable symmetry?", value=False)
wall_thickness = st.slider("Set wall thickness (for hollow objects)", min_value=1, max_value=10, value=2)

# Additional Features
add_stretch = st.checkbox("Apply Stretch/Deformation?", value=False)
apply_bumps = st.checkbox("Apply Bumps/Reliefs on surface?", value=False)
add_textures = st.checkbox("Add custom textures?", value=False)
use_gravity = st.checkbox("Simulate gravity effects?", value=False)
apply_noise = st.checkbox("Apply noise or random distortion?", value=False)
add_mesh_detail = st.slider("Mesh Detail Level", min_value=1, max_value=5, value=3)
apply_noise_type = st.selectbox("Noise Type", ["Perlin", "Gaussian", "Simplex", "White Noise", "Custom"])
apply_material_map = st.checkbox("Apply material map?", value=False)
add_lights = st.checkbox("Add lighting effects?", value=False)
enable_transparency = st.checkbox("Enable transparency?", value=False)
apply_reflection = st.checkbox("Add reflective surface?", value=False)
simulate_refraction = st.checkbox("Simulate refraction?", value=False)
change_orientation = st.selectbox("Shape Orientation", ["Front", "Side", "Top", "Isometric"])
add_displacement = st.checkbox("Add displacement mapping?", value=False)
modify_thickness = st.slider("Modify shape wall thickness", min_value=0.5, max_value=5.0, value=1.0)
add_custom_edges = st.checkbox("Add custom edge shapes?", value=False)
enable_decal = st.checkbox("Add decals to the surface?", value=False)
apply_noise_intensity = st.slider("Noise Intensity", min_value=0.0, max_value=1.0, value=0.5)
use_reflection_map = st.checkbox("Use reflection map?", value=False)
add_cutout = st.checkbox("Add cutouts to the shape?", value=False)
apply_shader = st.selectbox("Choose Shader", ["Phong", "Lambert", "Blinn-Phong", "Toon", "Cel", "Custom Shader"])
apply_dissolve = st.checkbox("Apply dissolve effect?", value=False)
add_bevel = st.checkbox("Add bevel to edges?", value=False)
apply_glow = st.checkbox("Add glow effect?", value=False)
add_extrusion = st.checkbox("Apply extrusion to the shape?", value=False)

# Helper function for generating random string for file names
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to process user input with Gemini AI (placeholder for AI functionality)
def process_user_input(user_input):
    # In a real application, you'd integrate a model like Gemini to process the input
    return user_input

# Function to extract dimensions from the AI's response (using NLP - optional)
def extract_dimensions_nlp(response):
    if nlp is None:
        return extract_dimensions_regex(response)

    doc = nlp(response)
    dimensions = {"length": 0, "width": 0, "height": 0}
    for token in doc:
        if token.pos_ == "NUM":
            value = float(token.text)
            if "length" in token.text.lower():
                dimensions["length"] = value
            elif "width" in token.text.lower():
                dimensions["width"] = value
            elif "height" in token.text.lower():
                dimensions["height"] = value

    return dimensions

# Function to extract dimensions from the AI's response (fallback regex)
def extract_dimensions_regex(response):
    dimensions = {"length": 0, "width": 0, "height": 0}
    numbers = re.findall(r'\d+', response)
    if len(numbers) >= 3:
        dimensions["length"] = float(numbers[0])
        dimensions["width"] = float(numbers[1])
        dimensions["height"] = float(numbers[2])
    return dimensions

# Function to generate an STL file for different shapes
def generate_stl_shape(dimensions, shape_type):
    if shape_type == "box":
        return generate_stl_box(dimensions)
    elif shape_type == "sphere":
        return generate_stl_sphere(dimensions)  # Implement sphere generation
    elif shape_type == "cone":
        return generate_stl_cone(dimensions)  # Implement cone generation
    elif shape_type == "pyramid":
        return generate_stl_pyramid(dimensions)  # Implement pyramid generation
    elif shape_type == "cylinder":
        return generate_stl_cylinder(dimensions)
    elif shape_type == "torus":
        return generate_stl_torus(dimensions)  # Implement torus generation
    elif shape_type == "custom":
        return generate_custom_shape(dimensions)

# Function to generate a box STL
def generate_stl_box(dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]

    vertices = np.array([
        [-length / 2, -width / 2, -height / 2],
        [length / 2, -width / 2, -height / 2],
        [length / 2, width / 2, -height / 2],
        [-length / 2, width / 2, -height / 2],
        [-length / 2, -width / 2, height / 2],
        [length / 2, -width / 2, height / 2],
        [length / 2, width / 2, height / 2],
        [-length / 2, width / 2, height / 2],
    ])

    faces = np.array([
        [0, 3, 1], [1, 3, 2],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j]]

    return box_mesh

# Main app logic
if st.button("Generate Design"):
    if prompt.strip() == "":
        st.error("Please provide a description for your design.")
    else:
        st.success("Design generated successfully!")
        response = process_user_input(prompt)
        dimensions = extract_dimensions_nlp(response)
        st.write(f"Extracted Dimensions: {dimensions}")

        stl_mesh = generate_stl_shape(dimensions, shape_type)
        stl_data = stl_to_bytes(stl_mesh)

        st.download_button(
            label="Download STL File",
            data=stl_data,
            file_name=f"{shape_type}_{random_string()}.stl",
            mime="application/octet-stream",
        )
