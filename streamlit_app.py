import streamlit as st
import numpy as np
from stl import mesh
import io
import random
import string

# Helper functions
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def stl_to_bytes(stl_mesh):
    stl_buffer = io.BytesIO()
    stl_mesh.save(stl_buffer, mode=mesh.Mode.BINARY)
    stl_buffer.seek(0)
    return stl_buffer.read()

# Shape generation functions
def generate_stl_box(dimensions):
    length, width, height = dimensions['length'], dimensions['width'], dimensions['height']

    vertices = np.array([
        [0, 0, 0],
        [length, 0, 0],
        [length, width, 0],
        [0, width, 0],
        [0, 0, height],
        [length, 0, height],
        [length, width, height],
        [0, width, height]
    ])

    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # Bottom
        [4, 5, 6], [4, 6, 7],  # Top
        [0, 1, 5], [0, 5, 4],  # Front
        [1, 2, 6], [1, 6, 5],  # Right
        [2, 3, 7], [2, 7, 6],  # Back
        [3, 0, 4], [3, 4, 7]   # Left
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j], :]

    return box_mesh

def generate_stl_cylinder(dimensions):
    st.error("Cylinder generation is not implemented yet.")
    return None

def generate_stl_sphere(dimensions):
    st.error("Sphere generation is not implemented yet.")
    return None

def generate_stl_cone(dimensions):
    st.error("Cone generation is not implemented yet.")
    return None

def generate_stl_pyramid(dimensions):
    st.error("Pyramid generation is not implemented yet.")
    return None

def generate_stl_torus(dimensions):
    st.error("Torus generation is not implemented yet.")
    return None

def generate_custom_shape(dimensions):
    st.error("Custom shape generation is not implemented yet.")
    return None

# Main STL shape generation function
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
    else:
        st.error(f"Shape type '{shape_type}' is not recognized.")
        return None

# Streamlit app
st.title("STL Shape Generator")
st.sidebar.header("Input Dimensions")

# Input for dimensions
dimensions = {
    'length': st.sidebar.number_input("Length (for applicable shapes):", min_value=1.0, value=10.0),
    'width': st.sidebar.number_input("Width (for applicable shapes):", min_value=1.0, value=5.0),
    'height': st.sidebar.number_input("Height (for applicable shapes):", min_value=1.0, value=15.0),
}

# Select shape type
shapes = ['box', 'sphere', 'cone', 'pyramid', 'cylinder', 'torus', 'custom']
shape_type = st.sidebar.selectbox("Select Shape Type:", shapes)

# Generate STL file
if st.button("Generate STL File"):
    stl_mesh = generate_stl_shape(dimensions, shape_type)

    if stl_mesh is not None:
        stl_data = stl_to_bytes(stl_mesh)
        st.download_button(
            label="Download STL File",
            data=stl_data,
            file_name=f"{shape_type}_{random_string()}.stl",
            mime="application/octet-stream",
        )
    else:
        st.error("Failed to generate the STL file. Please check the shape type or dimensions.")
