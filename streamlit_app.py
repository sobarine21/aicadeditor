import streamlit as st
import google.generativeai as genai
import trimesh
import plotly.graph_objects as go
import re

# Configure the Gemini API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit app UI
st.title("AI-Powered CAD Co-Pilot for Hardware Design")
st.write("Transform your plain text descriptions into parametric 3D models.")

# User input for CAD model description
prompt = st.text_area("Enter your 3D model description (e.g., 'create a toy car with length 10mm, width 5mm, and height 15mm'):")

# Function to generate 3D model from text description using Google Gemini
def generate_3d_model(prompt):
    try:
        # Modify the prompt to ensure the AI generates a consistent, structured response
        refined_prompt = f"Generate a 3D model description with parameters in the format: length: x, width: y, height: z, wheel_radius: w. The description should be based on the following: {prompt}"

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(refined_prompt)
        model_description = response.text
        st.write("AI Response:", model_description)
        return model_description
    except Exception as e:
        st.error(f"Error generating model: {e}")
        return None

# Function to extract parameters from the description
def extract_parameters(description):
    # Default to an empty dictionary
    params = {
        "shape": "toy_car",
        "body_dimensions": [10, 5, 15],
        "wheel_radius": 2
    }
    
    # Try to extract dimensions with regex patterns
    length_match = re.search(r'length\s?(\d+\.?\d*)\s?mm', description)
    width_match = re.search(r'width\s?(\d+\.?\d*)\s?mm', description)
    height_match = re.search(r'height\s?(\d+\.?\d*)\s?mm', description)
    wheel_match = re.search(r'wheel\s?radius\s?(\d+\.?\d*)\s?mm', description)

    if length_match and width_match and height_match:
        params["body_dimensions"] = [
            float(length_match.group(1)),
            float(width_match.group(1)),
            float(height_match.group(1))
        ]
    
    if wheel_match:
        params["wheel_radius"] = float(wheel_match.group(1))
    
    return params

# Function to create a 3D model of the toy car using Trimesh
def create_3d_model_from_description(description):
    params = extract_parameters(description)

    # Toy car body (simple box)
    body = trimesh.primitives.Box(extents=params["body_dimensions"])

    # Create the wheels as cylinders (defaulting to 2 wheels if not specified)
    wheel_radius = params["wheel_radius"]
    wheel_height = 2  # fixed height for the wheels
    wheels = []
    for i in range(4):  # Assuming 4 wheels
        # Place wheels symmetrically around the body
        offset_x = params["body_dimensions"][0] / 2 if i % 2 == 0 else -params["body_dimensions"][0] / 2
        offset_y = params["body_dimensions"][1] / 2 if i < 2 else -params["body_dimensions"][1] / 2
        wheel = trimesh.primitives.Cylinder(radius=wheel_radius, height=wheel_height)
        wheel.apply_translation([offset_x, offset_y, -params["body_dimensions"][2] / 2])
        wheels.append(wheel)
    
    # Combine body and wheels
    all_parts = [body] + wheels
    car_model = trimesh.util.concatenate(all_parts)
    return car_model

# Function to visualize the 3D model using Plotly
def visualize_3d_model(model):
    # Convert the trimesh model to vertices and faces for Plotly visualization
    vertices = model.vertices
    faces = model.faces
    fig = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        opacity=0.8,
        color='lightblue'
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

# Button to generate 3D model
if st.button("Generate 3D Model"):
    if prompt:
        model_description = generate_3d_model(prompt)
        
        if model_description:
            params = extract_parameters(model_description)
            if not params.get("body_dimensions"):
                st.error("Could not extract valid dimensions from the AI model description.")
            else:
                model = create_3d_model_from_description(model_description)

                if model:
                    visualize_3d_model(model)
        else:
            st.error("AI failed to generate a valid model description.")
    else:
        st.error("Please enter a description for the 3D model.")
