import streamlit as st
import google.generativeai as genai
import trimesh
import plotly.graph_objects as go
import re

# Set up Gemini API key securely from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit app UI
st.title("AI-Powered CAD Tool")
st.write("Create 3D models from text descriptions.")

# User input for CAD model description
prompt = st.text_area("Describe your 3D model (e.g., 'Create a toy car with length 100mm, width 50mm, height 30mm'):")

# Function to generate 3D model description via Gemini API
def generate_model_description(prompt):
    try:
        # Requesting model description from Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        model_description = response.text
        st.write("AI Response:", model_description)
        return model_description
    except Exception as e:
        st.error(f"Error generating model: {e}")
        return None

# Function to extract parameters (dimensions and wheel sizes) from the description
def extract_parameters(description):
    # Using regular expressions to extract dimensions
    car_dimensions = re.findall(r'length\s?(\d+\.?\d*)\s?mm.*?width\s?(\d+\.?\d*)\s?mm.*?height\s?(\d+\.?\d*)\s?mm', description)
    wheel_radius = re.findall(r'wheel\s?radius\s?(\d+\.?\d*)\s?mm', description)
    
    # If parameters are found, return them
    if car_dimensions:
        length, width, height = map(float, car_dimensions[0])
        wheel_radius = float(wheel_radius[0]) if wheel_radius else 5  # Default if not specified
        return {"shape": "toy_car", "body_dimensions": [length, width, height], "wheel_radius": wheel_radius}
    
    # Default values if no valid input is found
    return {"shape": "toy_car", "body_dimensions": [100, 50, 30], "wheel_radius": 5}

# Function to create a 3D model of the toy car using Trimesh
def create_3d_model_from_description(description):
    params = extract_parameters(description)
    
    # Create the car body as a box (simple 3D shape)
    body = trimesh.primitives.Box(extents=params["body_dimensions"])
    
    # Create the wheels as cylinders (default 4 wheels if not specified)
    wheel_radius = params["wheel_radius"]
    wheel_height = 5  # Fixed wheel height
    wheels = []
    for i in range(4):
        offset_x = params["body_dimensions"][0] / 2 if i % 2 == 0 else -params["body_dimensions"][0] / 2
        offset_y = params["body_dimensions"][1] / 2 if i < 2 else -params["body_dimensions"][1] / 2
        wheel = trimesh.primitives.Cylinder(radius=wheel_radius, height=wheel_height)
        wheel.apply_translation([offset_x, offset_y, -params["body_dimensions"][2] / 2])
        wheels.append(wheel)
    
    # Combine body and wheels into one mesh
    all_parts = [body] + wheels
    car_model = trimesh.util.concatenate(all_parts)
    return car_model

# Function to visualize 3D model using Plotly
def visualize_3d_model(model):
    # Convert Trimesh model to vertices and faces for Plotly visualization
    vertices = model.vertices
    faces = model.faces
    fig = go.Figure(data=[go.Mesh3d(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        opacity=0.7,
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

# Button to generate the model
if st.button("Generate 3D Model"):
    if prompt:
        # Step 1: Use Gemini AI to generate a description
        model_description = generate_model_description(prompt)
        
        # Step 2: Generate the 3D model from the description
        if model_description:
            model = create_3d_model_from_description(model_description)
            # Step 3: Visualize the generated model
            if model:
                visualize_3d_model(model)
    else:
        st.error("Please enter a description for the 3D model.")
