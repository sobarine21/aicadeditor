import streamlit as st
import google.generativeai as genai
import numpy as np
from stl import mesh
import re

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Dynamic AI CAD Design Generator")
st.write("Use generative AI to create 3D CAD designs from your description dynamically.")

# Prompt input field
prompt = st.text_area(
    "Describe the design you want. Example:\n- 'Create a box with length 10mm, width 5mm, height 15mm.'\n"
    "- 'Generate a cylinder with radius 5mm and height 20mm.'\n"
    "- 'Make a sphere with radius 10mm.'\n"
    "- 'Create a cone with radius 5mm and height 15mm.'\n"
    "- 'Make a pyramid with base 10mm and height 15mm.'",
    height=150,
)

# Scaling options
scaling_factor = st.slider("Scaling Factor (1.0 = original size):", 0.1, 10.0, 1.0, 0.1)

# Function to process user input with Gemini AI
def process_user_input(user_input):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        st.error(f"Error processing input: {e}")
        return None

# Function to extract design type and parameters dynamically
def parse_design_details(response):
    design_details = {
        "type": None,
        "parameters": {},
    }

    # Identify shape type (box, cylinder, sphere, cone, pyramid, etc.)
    if "box" in response.lower():
        design_details["type"] = "box"
        matches = re.findall(r"length\s*([\d.]+)|width\s*([\d.]+)|height\s*([\d.]+)", response, re.IGNORECASE)
        if matches:
            design_details["parameters"]["length"] = float(matches[0][0] or 0)
            design_details["parameters"]["width"] = float(matches[1][1] or 0)
            design_details["parameters"]["height"] = float(matches[2][2] or 0)

    elif "cylinder" in response.lower():
        design_details["type"] = "cylinder"
        matches = re.findall(r"radius\s*([\d.]+)|height\s*([\d.]+)", response, re.IGNORECASE)
        if matches:
            design_details["parameters"]["radius"] = float(matches[0][0] or 0)
            design_details["parameters"]["height"] = float(matches[1][1] or 0)

    elif "sphere" in response.lower():
        design_details["type"] = "sphere"
        matches = re.findall(r"radius\s*([\d.]+)", response, re.IGNORECASE)
        if matches:
            design_details["parameters"]["radius"] = float(matches[0][0] or 0)

    elif "cone" in response.lower():
        design_details["type"] = "cone"
        matches = re.findall(r"radius\s*([\d.]+)|height\s*([\d.]+)", response, re.IGNORECASE)
        if matches:
            design_details["parameters"]["radius"] = float(matches[0][0] or 0)
            design_details["parameters"]["height"] = float(matches[1][1] or 0)

    elif "pyramid" in response.lower():
        design_details["type"] = "pyramid"
        matches = re.findall(r"base\s*([\d.]+)|height\s*([\d.]+)", response, re.IGNORECASE)
        if matches:
            design_details["parameters"]["base"] = float(matches[0][0] or 0)
            design_details["parameters"]["height"] = float(matches[1][1] or 0)

    return design_details

# Dynamic STL generation functions
def generate_stl_box(params, scale):
    length = params.get("length", 0) * scale
    width = params.get("width", 0) * scale
    height = params.get("height", 0) * scale

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
        [0, 3, 1], [1, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j], :]
    return box_mesh

def generate_stl_cylinder(params, scale):
    radius = params.get("radius", 0) * scale
    height = params.get("height", 0) * scale
    num_sides = 32  # Resolution of the cylinder

    vertices = []
    faces = []

    # Generate top and bottom circles
    for i in range(num_sides):
        angle = 2 * np.pi * i / num_sides
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        vertices.append([x, y, -height / 2])  # Bottom circle
        vertices.append([x, y, height / 2])   # Top circle

    # Connect the sides
    for i in range(num_sides):
        next_i = (i + 1) % num_sides
        faces.append([i * 2, next_i * 2, i * 2 + 1])  # Side triangle 1
        faces.append([next_i * 2, next_i * 2 + 1, i * 2 + 1])  # Side triangle 2

    # Top and bottom faces
    for i in range(2, len(vertices), 2):
        faces.append([0, i, (i + 2) % len(vertices)])  # Bottom circle
        faces.append([1, (i + 1), ((i + 3) % len(vertices))])  # Top circle

    cylinder_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cylinder_mesh.vectors[i][j] = vertices[face[j]]
    return cylinder_mesh

def generate_stl_sphere(params, scale):
    radius = params.get("radius", 0) * scale
    num_slices = 16  # Slices for resolution
    num_stacks = 16  # Stacks for resolution
    vertices = []
    faces = []

    for i in range(num_stacks + 1):
        lat = np.pi * i / num_stacks  # Latitude
        for j in range(num_slices):
            lon = 2 * np.pi * j / num_slices  # Longitude
            x = radius * np.sin(lat) * np.cos(lon)
            y = radius * np.sin(lat) * np.sin(lon)
            z = radius * np.cos(lat)
            vertices.append([x, y, z])

    # Create faces (triangles) for the sphere
    for i in range(num_stacks):
        for j in range(num_slices):
            next_j = (j + 1) % num_slices
            top = i * num_slices + j
            bottom = (i + 1) * num_slices + j
            faces.append([top, bottom, top + 1])
            faces.append([top + 1, bottom, bottom + 1])

    sphere_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = vertices[face[j]]
    return sphere_mesh

def generate_stl_cone(params, scale):
    radius = params.get("radius", 0) * scale
    height = params.get("height", 0) * scale
    num_sides = 32  # Resolution of the cone

    vertices = [[0, 0, -height / 2]]  # Apex of the cone
    for i in range(num_sides):
        angle = 2 * np.pi * i / num_sides
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        vertices.append([x, y, height / 2])  # Bottom circle

    faces = []
    for i in range(1, num_sides + 1):
        next_i = (i % num_sides) + 1
        faces.append([0, i, next_i])

    cone_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cone_mesh.vectors[i][j] = vertices[face[j]]
    return cone_mesh

def generate_stl_pyramid(params, scale):
    base = params.get("base", 0) * scale
    height = params.get("height", 0) * scale
    vertices = np.array([
        [0, 0, height / 2],  # Apex
        [-base / 2, -base / 2, -height / 2],
        [base / 2, -base / 2, -height / 2],
        [base / 2, base / 2, -height / 2],
        [-base / 2, base / 2, -height / 2],
    ])

    faces = np.array([
        [0, 1, 2],
        [0, 2, 3],
        [0, 3, 4],
        [0, 4, 1],
        [1, 2, 3],
        [1, 3, 4]
    ])

    pyramid_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            pyramid_mesh.vectors[i][j] = vertices[face[j], :]
    return pyramid_mesh

# Main button to generate design
if st.button("Generate CAD Design"):
    if prompt:
        ai_response = process_user_input(prompt)
        if ai_response:
            st.write("AI interpreted your description as:")
            st.write(ai_response)

            # Parse design details
            design_details = parse_design_details(ai_response)
            st.write("Extracted Design Details:", design_details)

            # Generate STL based on type
            stl_file = None
            if design_details["type"] == "box":
                stl_file = generate_stl_box(design_details["parameters"], scale=scaling_factor)
            elif design_details["type"] == "cylinder":
                stl_file = generate_stl_cylinder(design_details["parameters"], scale=scaling_factor)
            elif design_details["type"] == "sphere":
                stl_file = generate_stl_sphere(design_details["parameters"], scale=scaling_factor)
            elif design_details["type"] == "cone":
                stl_file = generate_stl_cone(design_details["parameters"], scale=scaling_factor)
            elif design_details["type"] == "pyramid":
                stl_file = generate_stl_pyramid(design_details["parameters"], scale=scaling_factor)

            # Save and download STL
            if stl_file:
                stl_filename = "generated_design.stl"
                stl_file.save(stl_filename)
                with open(stl_filename, "rb") as file:
                    st.download_button(
                        label="Download STL File",
                        data=file,
                        file_name=stl_filename,
                        mime="application/octet-stream",
                    )
    else:
        st.warning("Please provide a valid description for the design.")

# Footer
st.write("---")
st.info("Powered by Google Gemini AI and Streamlit")
