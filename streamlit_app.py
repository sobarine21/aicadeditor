import streamlit as st
import google.generativeai as genai
import trimesh
import numpy as np
import tempfile
from trimesh.exchange.gltf import export_glb

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("3D Mesh Generation and Visualization with Gemini AI")
st.write("Generate 3D meshes based on your prompt using Google's Gemini AI model.")

# Prompt input field
prompt = st.text_input("Enter your prompt:", "Create a 3D model of a table.")

# Button to generate response
if st.button("Generate Mesh"):
    try:
        # Load and configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate response from the model (e.g., OBJ format for a 3D model)
        response = model.generate_content(prompt)
        st.write("Raw response from Gemini AI:", response)

        # Check if the response contains 3D model data
        if 'text' in response:
            mesh_text = response.text
            st.text_area("Generated OBJ Data", mesh_text)
        else:
            st.error("No 3D model returned from the AI.")

        # Proceed with further processing only if OBJ data is valid
        if mesh_text:
            try:
                # Save the mesh to a temporary OBJ file
                temp_file = tempfile.NamedTemporaryFile(suffix=".obj", delete=False).name
                with open(temp_file, "w") as f:
                    f.write(mesh_text)

                st.write(f"Saved OBJ file to {temp_file}")

                # Load the mesh using trimesh
                mesh = trimesh.load_mesh(temp_file)
                st.write(f"Mesh loaded with {len(mesh.vertices)} vertices.")

                # Button to visualize the 3D mesh
                if st.button("Visualize 3D Mesh"):
                    # Apply gradient coloring to the mesh
                    glb_path = apply_gradient_color(temp_file)
                    st.write(f"3D Mesh with Gradient Coloring generated. Download GLB file here:")

                    # Display the 3D mesh download link
                    st.write(f"[Download GLB]({glb_path})")

            except Exception as e:
                st.error(f"Error processing mesh: {e}")

    except Exception as e:
        st.error(f"Error: {e}")

# Function to apply gradient coloring to the mesh based on Y-axis values
def apply_gradient_color(temp_file):
    try:
        # Load the mesh
        mesh = trimesh.load_mesh(temp_file)

        # Apply gradient coloring based on the Y-axis of the vertices
        vertices = mesh.vertices
        y_values = vertices[:, 1]  # Y-axis values
        y_normalized = (y_values - y_values.min()) / (y_values.max() - y_values.min())

        # Create colors from the normalized Y-values (gradient from blue to red)
        colors = np.zeros((len(vertices), 4))  # RGBA
        colors[:, 0] = y_normalized  # Red channel
        colors[:, 2] = 1 - y_normalized  # Blue channel
        colors[:, 3] = 1.0  # Alpha channel

        # Attach colors to mesh vertices
        mesh.visual.vertex_colors = colors

        # Save the mesh as GLB
        glb_path = temp_file + ".glb"
        with open(glb_path, "wb") as f:
            f.write(export_glb(mesh))

        return glb_path

    except Exception as e:
        st.error(f"Error applying gradient color: {e}")
        return None
