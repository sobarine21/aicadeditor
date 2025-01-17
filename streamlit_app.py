import streamlit as st
import google.generativeai as genai
import cadquery as cq
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
        model = genai.GenerativeModel("gemini-1.5-flash")
        
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

# Button to generate design based on AI's interpretation
if st.button("Generate CAD Design"):
    if prompt:
        # Step 1: Use Gemini AI to process the user's description
        design_details = process_user_input(prompt)
        if design_details:
            st.write("AI interpreted the design as: ", design_details)

            # Step 2: Extract the design dimensions from the AI's response
            dimensions = extract_dimensions(design_details)

            # Step 3: Generate the CAD design using cadquery
            result = cq.Workplane("XY").box(dimensions["length"], dimensions["width"], dimensions["height"])

            # Step 4: Export the design as an STL file
            stl_file = "design.stl"
            result.exportStl(stl_file)

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
