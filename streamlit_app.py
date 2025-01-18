import streamlit as st
import numpy as np
from stl import mesh
import re
import random
import string
import tempfile

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

# Function to process user input (NLP or Regex extraction)
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
        return generate_stl_cone(dimensions)
    elif shape_type == "pyramid":
        return generate_stl_pyramid(dimensions)
    elif shape_type == "cylinder":
        return generate_stl_cylinder(dimensions)
    elif shape_type == "torus":
        return generate_stl_torus(dimensions)
    elif shape_type == "custom":
        return generate_custom_shape(dimensions)

# Function to generate a custom shape (combining predefined shapes or parts)
def generate_custom_shape(dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]

    if length > 0 and width > 0 and height > 0:
        box_mesh = generate_stl_box({"length": length, "width": width, "height": height})
        sphere_mesh = generate_stl_sphere({"length": height, "width": width, "height": height})
        # Combine shapes or create new geometry based on AI's response
        return box_mesh
    else:
        st.error("Unable to generate custom shape with the given dimensions.")
        return None

# Function to generate a box STL
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

# Function to generate a sphere STL
def generate_stl_sphere(dimensions):
    radius = dimensions["length"] / 2
    num_points = 20

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

# Function to provide download option for STL file using a temporary file
def stl_download_link(stl_mesh, filename="generated_design.stl"):
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp_file:
        stl_mesh.save(temp_file.name)  # Save STL to temp file
        st.download_button(label="Download STL", data=open(temp_file.name, 'rb'), file_name=filename, mime="application/octet-stream")

# Button to generate design and download it
if st.button("Generate Design"):
    if prompt:
        # Extract dimensions from user input using NLP or Regex
        dimensions = extract_dimensions_nlp(prompt)  # Replace with actual NLP logic
        stl_mesh = generate_stl_shape(dimensions, shape_type)
        if stl_mesh:
            stl_download_link(stl_mesh)  # Provide the STL file for download
        else:
            st.error("Unable to generate the design with the given parameters.")
    else:
        st.error("Please enter a valid prompt.")
