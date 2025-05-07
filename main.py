from collections import defaultdict
import json
import os
from code_loader import load_code_files
from chunker import chunk_code
from llm_analyzer import analyze_chunk, build_final_output  # Import final output builder
from db import codebase_files, chunks, analysis_results


# Function to merge analysis results by filename
def merge_results_by_filename(results):
    merged = {}

    for result in results:
        filename = result["filename"]

        if filename not in merged:
            merged[filename] = {
                "filename": filename,
                "description": result.get("description", ""),
                "lines_of_code": result.get("lines_of_code", 0),
                "key_imports": set(result.get("key_imports", [])),
                "classes": []
            }

        merged[filename]["key_imports"].update(result.get("key_imports", []))

        for new_class in result.get("classes", []):
            existing_class = next((cls for cls in merged[filename]["classes"]
                                   if cls["name"] == new_class["name"]), None)
            if existing_class:
                existing_class["annotations"] = list(set(existing_class.get("annotations", []) + new_class.get("annotations", [])))
                existing_class["methods"].extend(new_class.get("methods", []))
            else:
                merged[filename]["classes"].append(new_class)

    for file_data in merged.values():
        file_data["key_imports"] = list(file_data["key_imports"])

    return list(merged.values())


# Main function to run the analysis
def run_analysis(project_path):
    java_files = load_code_files(project_path)
    raw_results = []

    codebase_files.delete_many({})
    chunks.delete_many({})
    analysis_results.delete_many({})

    for file in java_files:
        file_id = codebase_files.insert_one({
            "filename": file["filename"],
            "file_path": file["path"],
            "file_content": file["content"]
        }).inserted_id

        file_chunks = chunk_code(file["content"])

        for i, chunk in enumerate(file_chunks):
            chunk_id = chunks.insert_one({
                "file_id": file_id,
                "chunk_content": chunk,
                "chunk_number": i,
                "processed": False
            }).inserted_id

            result = analyze_chunk(file["filename"], chunk)

            try:
                json_result = json.loads(result)

                analysis_results.insert_one({
                    "chunk_id": chunk_id,
                    "json_result": json_result
                })

                chunks.update_one({"_id": chunk_id}, {"$set": {"processed": True}})

                raw_results.append(json_result)

            except Exception as e:
                print(f"[WARN] JSON decode failed for chunk {i} of {file['filename']}: {e}")
                continue

    # Merge results by file
    merged_results = merge_results_by_filename(raw_results)

    # Build final JSON output with project overview
    final_output = build_final_output(merged_results)

    # Save to disk
    output_path = os.path.join(project_path, "final_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    return output_path, final_output
