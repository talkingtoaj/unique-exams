#!/usr/bin/env python3
"""
Command-line interface for Unique-Exams
Maintains backward compatibility with the original CLI workflow
"""
import os
from unique_exams.main import load_in_template, make_choices, create_new_document
from unique_exams.token_hash import to_hash, from_hash

if __name__ == '__main__':
    # new_exams = int(input("How many new exams do you want to generate? "))
    new_exams = 3
    print(os.getcwd())
    if "unique_exams" in os.getcwd():
        INPUT_FOLDER = os.path.join(os.getcwd(), "input")
        OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")
    else:
        INPUT_FOLDER = os.path.join(os.getcwd(), "unique_exams", "input")
        OUTPUT_FOLDER = os.path.join(os.getcwd(), "unique_exams", "output")

    exam_names = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    exam_paths = [os.path.join(INPUT_FOLDER, f) for f in exam_names]
    # remove file endings
    exam_names = [os.path.splitext(f)[0] for f in exam_names]
    loaded_contents = [load_in_template(os.path.join(INPUT_FOLDER, f)) for f in exam_paths]
    exam_structures = []
    for loaded_content in loaded_contents:
        exam_structures.append([len(choice['alternatives']) for choice in loaded_content['choices']])
    if not exam_structures or not exam_structures[0]:
        raise Exception("No alternative sections were detected. Add [[UE_ALT]] before each alternative and [[UE_END]] after each alternative section.")
    for i in range(len(exam_structures)):
        if exam_structures[i] != exam_structures[0]:
            raise Exception("The structure of the exam versions are not the same. Please check the files")
    for i in range(new_exams):
        choices = make_choices(loaded_contents[0])
        hash = to_hash(choices)
        reversed_from_hash = from_hash(hash)
        print (f"Choices: {choices} -> {hash} -> {reversed_from_hash}")
        for j, loaded_content in enumerate(loaded_contents):
            exam_name = exam_names[j]
            output_path = os.path.join(OUTPUT_FOLDER, f"{exam_name} - version {hash}.docx")
            create_new_document(loaded_content, choices, output_path, original=exam_paths[j])
