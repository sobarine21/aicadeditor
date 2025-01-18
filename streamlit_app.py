import streamlit as st
import openai
import trimesh
import numpy as np
import plotly.graph_objects as go
from google.generativeai import genai

# Configure API keys for AI models
openai.api_key = st.secrets["OPENAI_API_KEY"]
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit app UI
st.title("AI-Powered CAD Co-Pilot for Hardware Design")
st.write("Transform your plain text descriptions into parametric 3D models.")

# User input for CAD model description
prompt = st.text_area("Enter your 3D model description (e.g., 'a box with a hole in the center'):")

# Function to generate 3D model from text description using OpenAI or Google AI
def generate_3d_model(prompt):
    # Use a simple AI model (OpenAI's GPT or Google's Gemini) to interpret the prompt and return model parameters
    try:
        response = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt)
        model_description = response.text
        st.write("AI Response:", model_description)
        return model_description
    except Exception as e:
        st.error(f"Error generating model: {e}")
        return None

# Function to create a simple 3D model based on AI description (using trimesh)
def create_3d_model_from_description(description):
    # Example: Simple logic for parsing description and generating a 3D object.
    # Here we can interpret different shapes (like box, cylinder) and create 3D models.
    if "box" in description:
        # Create a box model
        box = trimesh.primitives.Box(extents=[2, 2, 2])
        return box
    elif "sphere" in description:
        # Create a sphere model
        sphere = trimesh.primitives.Sphere(radius=2)
        return sphere
    elif "cylinder" in description:
        # Create a cylinder model
        cylinder = trimesh.primitives.Cylinder(radius=1, height=3)
        return cylinder
    else:
        # Default to a simple box if no valid shape is found
        return trimesh.primitives.Box(extents=[2, 2, 2])

# Button to generate 3D model
if st.button("Generate 3D Model"):
    if prompt:
        # Generate the model description via AI
        model_description = generate_3d_model(prompt)
        
        # If a description is generated, proceed to create 3D model
        if model_description:
            # Generate 3D model from description
            model = create_3d_model_from_description(model_description)

            # Visualize the 3D model using Plotly
            if model:
                # Convert the trimesh model to vertices and faces for Plotly visualization
                vertices = model.vertices
                faces = model.faces
                fig = go.Figure(data=[go.Mesh3d(
                    x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
                    i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                    opacity=0.5,
                    color='blue'
                )])
                fig.update_layout(
                    title="Generated 3D Model",
                    scene=dict(
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False),
                        zaxis=dict(showgrid=False)
                    ),
                )
                st.plotly_chart(fig)
    else:
        st.error("Please enter a description for the 3D model.")
