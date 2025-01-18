import streamlit as st
import google.generativeai as genai
import numpy as np
from stl import mesh
import re
import random
import string

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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
material = st.selectbox("Choose a material type:", ["Plastic", "Metal", "Wood", "Glass", "Rubber"])
smooth_surface = st.checkbox("Smooth Surface?", value=False)
hollow = st.checkbox("Hollow Structure?", value=False)

# Helper function for generating random string for file names
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to process user input with Gemini AI
def process_user_input(user_input):
    try:
        # Load and configure the Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Generate a response from the AI
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        st.error(f"Error processing input: {e}")
        return None

# Function to extract dimensions from the AI's response
def extract_dimensions(response):
    dimensions = {"length": 0, "width": 0, "height": 0}
    # Regex to extract numerical dimensions (assuming a format like: length x width x height)
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

# Function to generate a custom shape (based on AI's interpretation)
def generate_custom_shape(dimensions):
    # Placeholder for custom shape logic. In practice, this can be more advanced depending on AI's interpretation
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]
    
    # Example of a simple custom shape - a randomly created combination of predefined shapes or parts
    # Here, we just simulate the custom shape creation using a box and sphere together
    # This can be extended as per the prompt description, e.g., a car, a chair, etc.
    
    if length > 0 and width > 0 and height > 0:
        box_mesh = generate_stl_box({"length": length, "width": width, "height": height})
        sphere_mesh = generate_stl_sphere({"length": height, "width": width, "height": height})
        return box_mesh  # For simplicity, returning box mesh as a placeholder for a "custom" shape
    else:
        st.error("Unable to generate custom shape with the given dimensions.")
        return None

# Function to generate a box STL
def generate_stl_box(dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]

    # Vertices of a 3D box
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

    # Faces of the box (using vertex indices)
    faces = np.array([
        [0, 3, 1], [1, 3, 2], # Bottom face
        [4, 5, 6], [4, 6, 7], # Top face
        [0, 1, 5], [0, 5, 4], # Front face
        [1, 2, 6], [1, 6, 5], # Right face
        [2, 3, 7], [2, 7, 6], # Back face
        [3, 0, 4], [3, 4, 7]  # Left face
    ])

    # Create the mesh
    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j], :]

    return box_mesh

# Function to generate a sphere STL
def generate_stl_sphere(dimensions):
    radius = dimensions["length"] / 2  # Assuming spherical dimension is based on length
    num_points = 50  # Resolution of the sphere

    # Create the sphere using parametric equations
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

    # Create faces (triangles between adjacent vertices)
    for i in range(num_points - 1):
        for j in range(num_points - 1):
            p1 = i * num_points + j
            p2 = i * num_points + j + 1
            p3 = (i + 1) * num_points + j
            p4 = (i + 1) * num_points + j + 1
            faces.append([p1, p2, p3])
            faces.append([p2, p3, p4])

    vertices = np.array(vertices)
    faces = np.array(faces)

    # Create mesh
    sphere_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = vertices[face[j], :]

    return sphere_mesh

# Button to generate design based on AI's interpretation
if st.button("Generate CAD Design"):
    if prompt:
        # Step 1: Use Gemini AI to process the user's description
        design_details = process_user_input(prompt)
        if design_details:
            st.write("AI interpreted the design as: ", design_details)

            # Step 2: Extract the design dimensions from the AI's response
            dimensions = extract_dimensions(design_details)

            # Step 3: Generate the CAD design (STL file) using numpy-stl
            shape_mesh = generate_stl_shape(dimensions, shape_type)

            # Step 4: Export the design as an STL file
            if shape_mesh:
                stl_file = f"{random_string(8)}_design.stl"
                shape_mesh.save(stl_file)

                # Provide a download link for the STL file
                with open(stl_file, "rb") as file:
                    st.download_button(
                        label="Download STL File",
                        data=file,
                        file_name=stl_file,
                        mime="application/octet-stream"
                    )
    else:
        st.write("Please provide a description for the design.")
