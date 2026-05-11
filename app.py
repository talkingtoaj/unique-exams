import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
from unique_exams.main import load_in_template, make_choices, create_new_document
from unique_exams.token_hash import to_hash, from_hash

# Page configuration
st.set_page_config(
    page_title="Unique Exams Generator",
    page_icon="📝",
    layout="wide"
)

# Title and description
st.title("📝 Unique Exams Generator")
st.markdown("""
Generate randomized exam papers where each student receives a unique set of questions
while maintaining equivalent difficulty. Upload your exam template(s) and generate
multiple unique versions with traceable hash codes.
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")
num_exams = st.sidebar.number_input(
    "Number of exams to generate",
    min_value=1,
    max_value=100,
    value=3,
    help="How many unique exam versions to create"
)

# Main content area
st.header("1️⃣ Upload Template Files")
st.markdown("""
Upload one or more Word document (.docx) templates. If you upload multiple templates
(e.g., Student Version and Examiner Version), they must have identical structure.

**Template Requirements:**
- Use `Question Alternate` or `Alternatif Soru 1` to mark alternative questions
- Use `END ALTERNATES` or `Alternatif Sonu` to close each alternative section
- See TEMPLATE_DESIGN.md for detailed guidance
""")

uploaded_files = st.file_uploader(
    "Choose Word document(s)",
    type=['docx'],
    accept_multiple_files=True,
    help="Upload .docx template files with marked alternative questions"
)

# Initialize session state for generated exams
if 'generated_exams' not in st.session_state:
    st.session_state.generated_exams = []
if 'temp_output_dir' not in st.session_state:
    st.session_state.temp_output_dir = None

# Generate button
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} template file(s) uploaded")

    # Display uploaded file names
    with st.expander("View uploaded files"):
        for file in uploaded_files:
            st.write(f"- {file.name}")

    st.header("2️⃣ Generate Exams")

    if st.button("🚀 Generate Exams", type="primary", use_container_width=True):
        try:
            # Create temporary directories
            temp_input_dir = tempfile.mkdtemp()
            temp_output_dir = tempfile.mkdtemp()
            st.session_state.temp_output_dir = temp_output_dir

            # Save uploaded files to temp input directory
            exam_paths = []
            exam_names = []

            with st.spinner("Saving uploaded files..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_input_dir, uploaded_file.name)
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    exam_paths.append(file_path)
                    exam_names.append(os.path.splitext(uploaded_file.name)[0])

            # Load templates
            with st.spinner("Loading templates and analyzing structure..."):
                loaded_contents = []
                for exam_path in exam_paths:
                    loaded_content = load_in_template(exam_path)
                    loaded_contents.append(loaded_content)

                # Verify all templates have the same structure
                exam_structures = []
                for loaded_content in loaded_contents:
                    exam_structures.append([len(choice['alternatives']) for choice in loaded_content['choices']])

                if not exam_structures[0]:
                    st.error("❌ Error: No alternative sections were detected.")
                    st.error("Check that your templates use markers like `Question Alternate` / `END ALTERNATES` or `Alternatif Soru 1` / `Alternatif Sonu`.")
                    raise Exception("No alternative sections were detected in the uploaded templates.")

                # Check structure consistency
                for i in range(len(exam_structures)):
                    if exam_structures[i] != exam_structures[0]:
                        st.error("❌ Error: All uploaded templates must have identical structure!")
                        st.error(f"Structure mismatch detected between templates.")
                        raise Exception("The structure of the exam versions are not the same.")

                # Display structure info
                st.info(f"📊 Exam structure: {len(loaded_contents[0]['choices'])} alternative sections detected")
                for idx, num_alts in enumerate(exam_structures[0]):
                    st.write(f"  - Section {idx + 1}: {num_alts} alternatives")

            # Generate exams
            progress_bar = st.progress(0)
            status_text = st.empty()
            generated_exams = []

            for i in range(num_exams):
                status_text.text(f"Generating exam {i + 1} of {num_exams}...")

                # Make random choices
                choices = make_choices(loaded_contents[0])
                hash_code = to_hash(choices)

                # Create documents for each template
                exam_files = []
                for j, loaded_content in enumerate(loaded_contents):
                    exam_name = exam_names[j]
                    output_filename = f"{exam_name} - version {hash_code}.docx"
                    output_path = os.path.join(temp_output_dir, output_filename)

                    create_new_document(loaded_content, choices, output_path, original=exam_paths[j])
                    exam_files.append({
                        'name': exam_name,
                        'filename': output_filename,
                        'path': output_path
                    })

                generated_exams.append({
                    'version': i + 1,
                    'hash': hash_code,
                    'choices': choices,
                    'files': exam_files
                })

                progress_bar.progress((i + 1) / num_exams)

            status_text.text("✅ Generation complete!")
            st.session_state.generated_exams = generated_exams

            # Clean up temp input directory
            shutil.rmtree(temp_input_dir)

            st.balloons()
            st.success(f"🎉 Successfully generated {num_exams} unique exam version(s)!")

        except Exception as e:
            st.error(f"❌ Error during generation: {str(e)}")
            st.exception(e)

# Display generated exams
if st.session_state.generated_exams:
    st.header("3️⃣ Download Generated Exams")

    for exam_data in st.session_state.generated_exams:
        with st.expander(f"📄 Exam Version {exam_data['version']} - Hash: `{exam_data['hash']}`", expanded=True):
            col1, col2 = st.columns([2, 3])

            with col1:
                st.markdown("**Version Details:**")
                st.write(f"Hash Code: `{exam_data['hash']}`")
                st.write(f"Choices: `{exam_data['choices']}`")

                # Verify hash reversibility
                reversed_choices = from_hash(exam_data['hash'])
                if reversed_choices == exam_data['choices']:
                    st.success("✅ Hash verified (reversible)")
                else:
                    st.warning("⚠️ Hash verification failed")

            with col2:
                st.markdown("**Download Files:**")
                for file_info in exam_data['files']:
                    # Read file for download
                    with open(file_info['path'], 'rb') as f:
                        file_bytes = f.read()

                    st.download_button(
                        label=f"⬇️ Download {file_info['name']}",
                        data=file_bytes,
                        file_name=file_info['filename'],
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        key=f"download_{exam_data['version']}_{file_info['name']}"
                    )

# Footer with instructions
st.markdown("---")
st.markdown("""
### 📚 How to Use
1. **Prepare Templates**: Create Word documents with alternative questions marked using `Question Alternate` / `END ALTERNATES` or `Alternatif Soru 1` / `Alternatif Sonu`
2. **Upload**: Upload one or more template files (must have identical structure if multiple)
3. **Configure**: Set the number of unique exams to generate
4. **Generate**: Click the generate button to create randomized versions
5. **Download**: Download each generated exam version with its unique hash code

### 🔑 Hash Codes
Each exam version has a unique hash code that can be used to:
- Identify which version a student received
- Regenerate the exact same exam if needed
- Track and manage different exam versions

### ℹ️ Need Help?
- See `TEMPLATE_DESIGN.md` for guidance on creating equivalent-difficulty alternatives
- Visit the [GitHub repository](https://github.com/anthropics/unique-exams) for more information
""")
