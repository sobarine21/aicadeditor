import streamlit as st
import numpy as np
from stl import mesh
import re
import random
import string
from io import BytesIO

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

# Helper function for generating random string for file names
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

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
        return generate_stl_sphere(dimensions)
    elif shape_type == "cone":
        return generate_stl_cone(dimensions)  # Implement cone generation
    elif shape_type == "pyramid":
        return generate_stl_pyramid(dimensions)  # Implement pyramid generation
    elif shape_type == "cylinder":
        return generate_stl_cylinder(dimensions)  # Implement cylinder generation
    elif shape_type == "torus":
        return generate_stl_torus(dimensions)  # Implement torus generation
    elif shape_type == "custom":
        return generate_custom_shape(dimensions)

# Function to generate an STL file for the box shape
def generate_stl_box(dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]

    vertices = np.array([
        [-length/2, -width/2, -height/2],
        [ length/2, -width/2, -height/2],
        [ length/2,  width/2, -height/2],
        [-length/2,  width/2, -height/2],
        [-length/2, -width/2,  height/2],
        [ length/2, -width/2,  height/2],
        [ length/2,  width/2,  height/2],
        [-length/2,  width/2,  height/2]
    ])

    faces = np.array([
        [0, 3, 1], [1, 3, 2],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7]
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j], :]

    return box_mesh

# Function to generate an STL file for the sphere shape
def generate_stl_sphere(dimensions):
    radius = dimensions["length"] / 2
    num_points = 50  # Set grid resolution

    vertices = []
    faces = []

    for i in range(num_points):
        lat = np.pi * (i / (num_points - 1) - 0.5)
        for j in range(num_points):
            lon = 2 * np.pi * j / (num_points - 1)
            x = radius * np.cos(lat) * np.cos(lon)
            y = radius * np.cos(lat) * np.sin(lon)
            z = radius * np.sin(lat)
            vertices.append([x, y, z])

    for i in range(num_points - 1):
        for j in range(num_points - 1):
            p1 = i * num_points + j
            p2 = p1 + 1
            p3 = p1 + num_points
            p4 = p3 + 1
            faces.append([p1, p2, p3])
            faces.append([p2, p4, p3])

    sphere_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = vertices[face[j]]

    return sphere_mesh

# Function to generate a custom shape (based on AI's interpretation)
def generate_custom_shape(dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]

    # Example of a simple custom shape - combining a box and a sphere
    if length > 0 and width > 0 and height > 0:
        # Create a box with the specified dimensions
        box_mesh = generate_stl_box({"length": length, "width": width, "height": height})

        # Optionally, create a sphere with a radius defined by height (or any other dimension)
        sphere_mesh = generate_stl_sphere({"length": height, "width": width, "height": height})

        # Example: You can combine the box and the sphere (this could involve more complex geometry processing)
        return box_mesh
    else:
        st.error("Unable to generate custom shape with the given dimensions.")
        return None

# Function to download the STL file
def download_stl(mesh):
    stl_file = BytesIO()
    mesh.save(stl_file)
    stl_file.seek(0)
    st.download_button("Download STL file", stl_file, file_name="generated_design.stl", mime="application/stl")

# Trigger generation and download
if st.button("Generate Design"):
    # Process the prompt to extract dimensions and shape
    dimensions = extract_dimensions_regex(prompt)  # Assuming dimensions extracted from prompt
    stl_mesh = generate_stl_shape(dimensions, shape_type)
    
    if stl_mesh:
        download_stl(stl_mesh)  # Allow the user to download the STL file
