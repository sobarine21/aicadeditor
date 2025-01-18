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
prompt = st.text_area("Describe the design you want (e.g., 'Create a box with length 10mm, width 5mm, and height 15mm.')")

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

# Function to extract dimensions and possible units from the AI's response
def extract_dimensions_and_units(response):
    dimensions = {"length": 0, "width": 0, "height": 0, "unit": "mm"}
    # Regex to extract numerical dimensions and units (length x width x height with optional units)
    matches = re.findall(r'(\d+\.?\d*)\s*(mm|cm|m|in|ft|yd)?', response)
    if len(matches) >= 3:
        dimensions["length"] = float(matches[0][0])
        dimensions["width"] = float(matches[1][0])
        dimensions["height"] = float(matches[2][0])
        # Use the most common unit or default to 'mm'
        dimensions["unit"] = matches[0][1] or "mm"
    return dimensions

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

# Function to generate an STL file for a box
def generate_stl_box(dimensions):
    length = convert_to_mm(dimensions["length"], dimensions["unit"])
    width = convert_to_mm(dimensions["width"], dimensions["unit"])
    height = convert_to_mm(dimensions["height"], dimensions["unit"])

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

# Button to generate design based on AI's interpretation
if st.button("Generate CAD Design"):
    if prompt:
        # Step 1: Use Gemini AI to process the user's description
        design_details = process_user_input(prompt)
        if design_details:
            st.write("AI interpreted the design as: ", design_details)

            # Step 2: Extract the design dimensions and unit from the AI's response
            dimensions = extract_dimensions_and_units(design_details)

            # Step 3: Generate the CAD design (STL file) using numpy-stl
            box_mesh = generate_stl_box(dimensions)

            # Step 4: Export the design as an STL file
            stl_file = "design.stl"
            box_mesh.save(stl_file)

            # Provide a download link for the STL file
            with open(stl_file, "rb") as file:
                st.download_button(
                    label="Download STL File",
                    data=file,
                    file_name="design.stl",
                    mime="application/octet-stream"
                )
    else:
        st.write("Please provide a description for the design.")
