import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from collections import Counter


# === Setup ===
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# === Prompt Template ===
prompt_template = PromptTemplate.from_template("""
You are an expert AI code analyzer. Analyze the following source code and extract structured metadata.
Output must be strictly in valid JSON format with no extra text. Follow this structure:

{{
  "filename": "{filename}",
  "description": "Brief description of what this file or class does",
  "lines_of_code": <number of lines in the full code>,
  "key_imports": ["..."],
  "classes": [
    {{
      "name": "ClassName",
      "annotations": ["..."],
      "description": "What the class does",
      "methods": [
        {{
          "signature": "full method signature",
          "description": "what the method does",
          "complexity": {{
            "level": "Low | Medium | High"
          }}
        }}
      ]
    }}
  ]
}}

Only include the actual content inside the JSON brackets. Do not explain anything outside it.

Code:
{code_chunk}
""")

# === LLM Setup ===
llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    temperature=0.3,
    model_name="gpt-3.5-turbo"
)
chain = LLMChain(llm=llm, prompt=prompt_template)

total_input_tokens = 0
total_output_tokens = 0

# === Analyze Single Chunk ===
def analyze_chunk(filename, code_chunk):
    global total_input_tokens, total_output_tokens
    try:
        with get_openai_callback() as cb:
            response = chain.run({
                "filename": filename,
                "code_chunk": code_chunk
            })
            total_input_tokens += cb.prompt_tokens or 0
            total_output_tokens += cb.completion_tokens or 0
        print(f"[TOKENS] {filename} → Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens}")
        return response
    except Exception as e:
        print(f"[ERROR] Failed to analyze {filename}: {str(e)}")
        return f"Error: {str(e)}"
    
import re
from collections import Counter

def generate_project_purpose_with_llm(file_summaries, llm):
    """
    Uses LLM to generate a clear, 2-3 line natural project purpose from structured file summaries.
    """
    text_blob = []

    for file in file_summaries:
        desc = file.get("description", "")
        text_blob.append(f"File: {file['filename']}\n{desc}")
        for cls in file.get("classes", []):
            class_desc = cls.get("description", "")
            text_blob.append(f"Class: {cls['name']}\n{class_desc}")
            for method in cls.get("methods", []):
                method_desc = method.get("description", "")
                if method_desc:
                    text_blob.append(method_desc)

    full_context = "\n".join(text_blob)

    prompt = f"""
You are an expert software analyst. Given the following structured metadata from source code files, write a clear, natural, 2–3 line project purpose description.

Only describe what this project is about — don't explain structure or implementation.

Metadata:
{full_context}

Project Purpose:
"""
    try:
        result = llm.invoke(prompt)
        return result.strip()
    except Exception as e:
        print(f"[ERROR] LLM purpose generation failed: {str(e)}")
        return "This project provides backend functionality for a domain-specific application, including business logic and authentication."


def build_final_output(merged_results):
    total_classes = 0
    total_lines = 0
    file_count = len(merged_results)

    for file in merged_results:
        total_classes += len(file.get("classes", []))
        total_lines += file.get("lines_of_code", 0)

    # Use LLM to generate a proper project purpose
    project_purpose_description = generate_project_purpose_with_llm(merged_results, llm)

    return {
        "files": merged_results,
        "project_overview": {
            "description": project_purpose_description,
            "total_files_analyzed": file_count,
        }
    }

