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

def summarize_project_purpose(file_summaries):
    """
    Analyzes and generates a project overview based on descriptions from analyzed files.
    It gives a meaningful, human-readable summary of the project’s purpose.
    """
    if not file_summaries:
        return "This project contains source code files analyzed for structure and functionality."

    # Accumulate file descriptions and key terms
    project_purpose = []
    domain_terms = []
    classes_found = 0
    files_analyzed = len(file_summaries)
    total_lines_of_code = 0

    for file in file_summaries:
        file_desc = file.get("description", "")
        filename = file.get("filename", "")
        total_lines_of_code += file.get("lines_of_code", 0)

        # Collect descriptions of the files
        if file_desc:
            project_purpose.append(file_desc)

        # Identify domain-specific terms or key concepts
        for cls in file.get("classes", []):
            class_desc = cls.get("description", "").lower()
            classes_found += 1
            project_purpose.append(class_desc)

            # Extract domain-related terms
            domain_terms.extend(re.findall(r"\b[a-zA-Z_]{4,}\b", class_desc.lower()))

            for method in cls.get("methods", []):
                method_desc = method.get("description", "").lower()
                project_purpose.append(method_desc)
                domain_terms.extend(re.findall(r"\b[a-zA-Z_]{4,}\b", method_desc.lower()))

    # Filter domain terms 
    stop_words = {"class", "method", "name", "code", "file", "handles", "returns", "object", "from", "with", "get", "set", "using"}
    filtered_domain_terms = [term for term in domain_terms if term not in stop_words]

    # Count frequency of domain terms
    term_counts = Counter(filtered_domain_terms)
    top_terms = ", ".join([term for term, _ in term_counts.most_common(5)])

    # Create the summary based on the collected descriptions
    if project_purpose:
        overview = f"This project includes source code that focuses on {top_terms}. "
        overview += " ".join(project_purpose)
    else:
        overview = "This project contains source code files that were analyzed for structure and functionality."

    # Add high-level project information
    project_overview = {
        "description": overview,
        "total_files_analyzed": files_analyzed
    }
    return project_overview


def build_final_output(merged_results):
    total_classes = 0
    total_lines = 0
    file_count = len(merged_results)

    for file in merged_results:
        total_classes += len(file.get("classes", []))
        total_lines += file.get("lines_of_code", 0)

    project_description = summarize_project_purpose(merged_results)

    return {
        "files": merged_results,
        "project_overview": {
            "description": project_description,
            "total_files_analyzed": file_count
        }
    }
