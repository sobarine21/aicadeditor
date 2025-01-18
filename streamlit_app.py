import streamlit as st
import google.generativeai as genai
import os
import numpy as np
import math

# Configure the Gemini API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to estimate cutting force (simplified model based on cutting speed, tool diameter, and material)
def calculate_cutting_force(diameter, cutting_speed, feed_rate, material):
    material_properties = {
        "Aluminum": 100,  # N/mm^2
        "Steel": 200,
        "Titanium": 300,
        "Brass": 150,
        "Plastic": 50,
        "Other": 120
    }
    
    material_strength = material_properties.get(material, 120)  # Default to "Other" if not found
    force = (cutting_speed * feed_rate * diameter) / 1000  # Simplified formula for estimation
    
    # Adjust based on material strength
    force *= material_strength / 100
    return force

# Function to estimate tool life based on cutting force and tool diameter
def estimate_tool_life(cutting_force, tool_diameter):
    # A simplified formula for tool life estimation
    tool_life = (tool_diameter ** 2) / (cutting_force * 0.1)
    return tool_life

# Streamlit App UI
st.title("CNC VMC Design Copilot")
st.write("Use Generative AI to design CNC VMC models and generate G-code files with enhanced features.")

# Part Specifications
st.header("Part Specifications")
shape = st.selectbox("Select Part Shape:", ["Cylinder", "Cube", "Cone", "Sphere"])
diameter = st.number_input("Enter diameter (mm):", min_value=1, value=50)
height = st.number_input("Enter height (mm):", min_value=1, value=100)
length = st.number_input("Enter length (mm):", min_value=1, value=100) if shape == "Cube" else 0

material = st.selectbox("Select material:", ["Aluminum", "Steel", "Titanium", "Brass", "Plastic", "Other"])

# Tolerance and Finish
tolerance = st.number_input("Enter tolerance (mm):", min_value=0.01, value=0.1)
finish_type = st.selectbox("Select finish type:", ["Rough", "Fine", "Ultra-Fine"])

# Tooling Information
st.header("Tooling Information")
tool_type = st.selectbox("Select tool type:", ["End Mill", "Ball End Mill", "Face Mill", "Drill", "Tap"])
tool_diameter = st.number_input("Enter tool diameter (mm):", min_value=1, value=10)
tool_length = st.number_input("Enter tool length (mm):", min_value=1, value=50)
cutting_speed = st.number_input("Enter cutting speed (mm/min):", min_value=1, value=150)
feed_rate = st.number_input("Enter feed rate (mm/min):", min_value=1, value=100)
depth_of_cut = st.number_input("Enter depth of cut (mm):", min_value=0.1, value=5.0)

# Advanced Machining Options
workpiece_orientation = st.selectbox("Select workpiece orientation:", ["Flat", "Vertical", "Tilted"])
coolant_option = st.radio("Use coolant?", ("Yes", "No"))
spindle_speed = st.number_input("Enter spindle speed (RPM):", min_value=500, value=1500)
chip_load = st.number_input("Enter chip load (mm/tooth):", min_value=0.01, value=0.1)

# Operations and Sequence
st.header("Operations Sequence")
operations = st.multiselect("Select operations:", ["Roughing", "Drilling", "Finishing", "Tapping"])
operation_sequence = st.text_input("Define operation sequence (comma-separated, e.g., Roughing, Drilling):")

# Button to generate model and G-code
if st.button("Generate Design and G-code"):
    try:
        # Step 1: Generate CNC Model using Gemini API
        prompt = f"Create a 3D {shape} CNC VMC model with diameter {diameter}mm, height {height}mm, material {material}, using tool {tool_type}, with cutting speed {cutting_speed}mm/min, feed rate {feed_rate}mm/min, depth of cut {depth_of_cut}mm. Apply {finish_type} finish."
        
        # Interact with Gemini API for design generation (simulate with a mock response)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        # Simulate Toolpath Generation
        toolpath = f"Generating toolpath for {material} part with {tool_type}."

        # Advanced Cutting Force Estimation
        cutting_force = calculate_cutting_force(diameter, cutting_speed, feed_rate, material)
        tool_life = estimate_tool_life(cutting_force, tool_diameter)

        # Step 3: Generate G-code (simplified)
        gcode = f"""
        G21 ; Set units to mm
        G17 ; Select XY plane
        G90 ; Absolute positioning
        ; Toolpath for {material} part with {tool_type}
        {toolpath}
        M30 ; End of program
        """
        
        # Step 4: Handle file generation for CAD (mocked content)
        gcode_filename = f"part_{diameter}x{height}_gcode.gcode"
        with open(gcode_filename, 'w') as file:
            file.write(gcode)

        cad_filename = f"part_{diameter}x{height}_model.step"
        with open(cad_filename, 'w') as file:
            file.write(f"CAD file for {material} part with diameter {diameter}mm and height {height}mm.")

        # Step 5: Provide download links
        st.write("Design Generation and Toolpath Complete!")
        st.download_button(label="Download G-code", data=open(gcode_filename, "rb").read(), file_name=gcode_filename, mime="application/gcode")
        st.download_button(label="Download CAD Model (STEP format)", data=open(cad_filename, "rb").read(), file_name=cad_filename, mime="application/step")

        # Display advanced features
        st.write(f"Estimated Cutting Force: {cutting_force:.2f} N")
        st.write(f"Tool Life Estimation: {tool_life:.2f} hours based on parameters.")

    except Exception as e:
        st.error(f"Error: {e}")
