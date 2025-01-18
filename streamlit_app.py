import streamlit as st
import google.generativeai as genai
import numpy as np
import freecad, Part
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

# Advanced Features
texture = st.selectbox("Choose a texture:", ["Matte", "Glossy", "Metallic", "Transparent"])
grid_resolution = st.slider("Set Grid Resolution", min_value=10, max_value=100, value=50)
add_round_edges = st.checkbox("Add rounded edges?", value=False)
enable_symmetry = st.checkbox("Enable symmetry?", value=False)
wall_thickness = st.slider("Set wall thickness (for hollow objects)", min_value=1, max_value=10, value=2)

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

# Function to generate a FreeCAD document for different shapes
def generate_freecad_shape(dimensions, shape_type):
    doc = FreeCAD.newDocument("ShapeDesign")
    if shape_type == "box":
        return generate_freecad_box(doc, dimensions)
    elif shape_type == "sphere":
        return generate_freecad_sphere(doc, dimensions)
    elif shape_type == "cone":
        return generate_freecad_cone(doc, dimensions)
    elif shape_type == "pyramid":
        return generate_freecad_pyramid(doc, dimensions)
    elif shape_type == "cylinder":
        return generate_freecad_cylinder(doc, dimensions)
    elif shape_type == "torus":
        return generate_freecad_torus(doc, dimensions)
    elif shape_type == "custom":
        return generate_custom_shape(doc, dimensions)

# Function to generate a custom shape (based on AI's interpretation)
def generate_custom_shape(doc, dimensions):
    # Placeholder for custom shape logic. In practice, this can be more advanced depending on AI's interpretation
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]
    
    # Example of a simple custom shape - a randomly created combination of predefined shapes or parts
    if length > 0 and width > 0 and height > 0:
        box = generate_freecad_box(doc, {"length": length, "width": width, "height": height})
        sphere = generate_freecad_sphere(doc, {"length": height, "width": width, "height": height})
        return box # For simplicity, returning box as a placeholder for a "custom" shape
    else:
        st.error("Unable to generate custom shape with the given dimensions.")
        return None

# Function to generate a FreeCAD box
def generate_freecad_box(doc, dimensions):
    length = dimensions["length"]
    width = dimensions["width"]
    height = dimensions["height"]
    box = doc.addObject("Part::Box", "Box")
    box.Length = length
    box.Width = width
    box.Height = height
    doc.recompute()
    return box

# Function to generate a FreeCAD sphere
def generate_freecad_sphere(doc, dimensions):
    radius = dimensions["length"] / 2 # Assuming spherical dimension is based on length
    sphere = doc.addObject("Part::Sphere", "Sphere")
    sphere.Radius = radius
    doc.recompute()
    return sphere

# Button to generate design based on AI's interpretation
if st.button("Generate CAD Design"):
    if prompt:
        # Step 1: Use Gemini AI to process the user's description
        design_details = process_user_input(prompt)
        if design_details:
            st.write("AI interpreted the design as: ", design_details)

            # Step 2: Extract the design dimensions from the AI's response
            dimensions = extract_dimensions(design_details)

            # Step 3: Generate the CAD design using FreeCAD
            shape = generate_freecad_shape(dimensions, shape_type)

            # Step 4: Export the design as a FreeCAD file
            if shape:
                filename = f"{random_string(8)}_design.FCStd"
                doc.saveAs(filename)

                # Provide a download link for the FreeCAD file
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download FreeCAD File",
                        data=file,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
    else:
        st.write("Please provide a description for the design.")
