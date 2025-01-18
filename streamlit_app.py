import streamlit as st
import google.generativeai as genai
import numpy as np
from stl import mesh
import re

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("AI CAD Design Generator")
st.write("Use generative AI to create CAD designs from your description.")

# Prompt input field
prompt = st.text_area("Describe the design you want (e.g., 'Create a toy car with length 10mm, width 5mm, and height 15mm.')")

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

# Function to extract details (shape and dimensions) from the AI's response
def extract_details_from_response(response):
    details = {"shape": None, "length": 0, "width": 0, "height": 0, "unit": "mm"}

    # Regular expressions for identifying shapes and extracting dimensions
    shape_match = re.search(r'(box|sphere|cylinder|cone|pyramid|car|toy car)', response, re.IGNORECASE)
    dimensions_match = re.findall(r'(\d+\.?\d*)\s*(mm|cm|m|in|ft|yd)?', response)

    if shape_match:
        details["shape"] = shape_match.group(0).lower()

    if dimensions_match:
        # Extract dimensions and units (if provided)
        for dim in dimensions_match:
            details["length"] = float(dim[0])
            details["unit"] = dim[1] if dim[1] else "mm"  # Default to mm if no unit provided
            # For simplicity, assuming length=width=height if only one dimension is given
            details["width"] = details["length"]
            details["height"] = details["length"]

    return details

# Function to convert units to millimeters
def convert_to_mm(value, unit):
    if unit == "cm":
        return value * 10
    elif unit == "m":
        return value * 1000
    elif unit == "in":
        return value * 25.4
    elif unit == "ft":
        return value * 304.8
    elif unit == "yd":
        return value * 914.4
    return value  # default to mm if the unit is already mm

# Function to generate a box (rectangular prism) STL
def generate_stl_box(dimensions):
    length = convert_to_mm(dimensions["length"], dimensions["unit"])
    width = convert_to_mm(dimensions["width"], dimensions["unit"])
    height = convert_to_mm(dimensions["height"], dimensions["unit"])

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
        [0, 3, 1], [1, 3, 2], # Bottom face
        [4, 5, 6], [4, 6, 7], # Top face
        [0, 1, 5], [0, 5, 4], # Front face
        [1, 2, 6], [1, 6, 5], # Right face
        [2, 3, 7], [2, 7, 6], # Back face
        [3, 0, 4], [3, 4, 7]  # Left face
    ])

    box_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            box_mesh.vectors[i][j] = vertices[face[j], :]

    return box_mesh

# Function to generate a sphere STL
def generate_stl_sphere(radius):
    # Placeholder: Generating sphere using vertices (simplified)
    phi = np.linspace(0, np.pi, 10)
    theta = np.linspace(0, 2 * np.pi, 10)
    phi, theta = np.meshgrid(phi, theta)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)

    # Create a list of faces (triangles between the points)
    faces = []
    for i in range(len(phi)-1):
        for j in range(len(theta)-1):
            faces.append([i * len(theta) + j, (i+1) * len(theta) + j, i * len(theta) + (j+1)])
            faces.append([(i+1) * len(theta) + j, (i+1) * len(theta) + (j+1), i * len(theta) + (j+1)])

    sphere_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            sphere_mesh.vectors[i][j] = [x[face[j]], y[face[j]], z[face[j]]]

    return sphere_mesh

# Function to generate a cylinder STL
def generate_stl_cylinder(radius, height):
    # A simple cylindrical mesh (using a basic parametric equation for a cylinder)
    theta = np.linspace(0, 2 * np.pi, 30)
    z = np.linspace(-height / 2, height / 2, 10)
    theta, z = np.meshgrid(theta, z)

    x = radius * np.cos(theta)
    y = radius * np.sin(theta)

    # Create faces for the cylinder
    faces = []
    for i in range(len(z) - 1):
        for j in range(len(theta) - 1):
            faces.append([i * len(theta) + j, (i+1) * len(theta) + j, i * len(theta) + (j+1)])
            faces.append([(i+1) * len(theta) + j, (i+1) * len(theta) + (j+1), i * len(theta) + (j+1)])

    cylinder_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            cylinder_mesh.vectors[i][j] = [x[face[j]], y[face[j]], z[face[j]]]

    return cylinder_mesh

# Button to generate design based on AI's interpretation
if st.button("Generate CAD Design"):
    if prompt:
        # Step 1: Use Gemini AI to process the user's description
        design_details = process_user_input(prompt)
        if design_details:
            st.write("AI interpreted the design as: ", design_details)

            # Step 2: Extract the design details from the AI's response (e.g., shape, dimensions)
            details = extract_details_from_response(design_details)
            shape = details["shape"]

            # Initialize stl_file to None, in case the shape is not recognized
            stl_file = None

            if shape == "box":
                # Step 3: Generate the CAD design (STL file) for a box
                box_mesh = generate_stl_box(details)
                stl_file = "box_design.stl"
                box_mesh.save(stl_file)
            
            elif shape == "sphere":
                # Step 3: Generate the CAD design (STL file) for a sphere
                radius = convert_to_mm(details["length"], details["unit"])  # Assuming sphere's radius is the "length"
                sphere_mesh = generate_stl_sphere(radius)
                stl_file = "sphere_design.stl"
                sphere_mesh.save(stl_file)

            elif shape == "cylinder":
                # Step 3: Generate the CAD design (STL file) for a cylinder
                radius = convert_to_mm(details["length"], details["unit"])  # Assuming radius is provided as "length"
                cylinder_mesh = generate_stl_cylinder(radius, details["height"])
                stl_file = "cylinder_design.stl"
                cylinder_mesh.save(stl_file)

            else:
                st.error("Shape not recognized or supported. Please provide a valid description.")

            # Check if stl_file was defined before attempting to open it
            if stl_file:
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
