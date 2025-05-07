import os
import sys
import json
import re
import shutil
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, send_file
from main import run_analysis
from code_loader import load_code_files
from db import codebase_files, chunks, analysis_results
from bson import json_util
import redis

# === Setup Logging ===
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "app.log")

# File handler
file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=2)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)

# Console handler (optional)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Also log Werkzeug (Flask's HTTP logger) to file
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(file_handler)

# === Flask App ===
app = Flask(__name__)
#redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

BASE_TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(BASE_TEMP_DIR, exist_ok=True)

def serialize_cursor(cursor):
    return json.loads(json_util.dumps(cursor))

@app.route("/")
def index():
    logging.info("Accessed index page")
    return render_template("index.html")

def get_folder_structure(path):
    logging.info(f"Getting folder structure for: {path}")
    folder_dict = {"name": os.path.basename(path), "type": "folder", "children": []}
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                folder_dict["children"].append(get_folder_structure(full_path))
            else:
                folder_dict["children"].append({"name": entry, "type": "file"})
    except Exception as e:
        logging.error(f"Error reading folder structure: {e}")
        folder_dict["error"] = str(e)
    return folder_dict

def clone_repo_and_get_subpath(full_url):
    logging.info(f"Cloning repo from: {full_url}")
    match = re.match(r"https://github\.com/([^/]+/[^/]+)(/tree/([^/]+)(/.+)?)?", full_url)
    if not match:
        return None, None, "Invalid GitHub URL format"

    repo_path = match.group(1)
    branch = match.group(3) if match.group(3) else "master"
    subdir = match.group(4)[1:] if match.group(4) else ""

    repo_url = f"https://github.com/{repo_path}.git"
    repo_name = repo_path.split("/")[-1]
    repo_dir = os.path.join(BASE_TEMP_DIR, repo_name)

    if not os.path.exists(repo_dir):
        try:
            subprocess.run(["git", "clone", "-b", branch, "--depth", "1", repo_url, repo_dir], check=True)
            logging.info(f"Repo cloned to: {repo_dir}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Git clone failed: {e}")
            return None, None, f"Git clone failed: {str(e)}"

    final_path = os.path.join(repo_dir, subdir)
    if not os.path.exists(final_path):
        logging.warning(f"Subpath '{subdir}' does not exist in repo")
        return None, None, f"Subpath '{subdir}' does not exist in repo"

    return final_path, repo_dir, None

@app.route("/fetch", methods=["POST"])
def fetch_structure():
    path = request.form["repo_path"]
    logging.info(f"Fetching structure for: {path}")

    if path.startswith("http://") or path.startswith("https://"):
        subpath, _, err = clone_repo_and_get_subpath(path)
        if err:
            logging.error(f"Fetch error: {err}")
            return jsonify({"error": err}), 400
        folder_tree = get_folder_structure(subpath)
    else:
        folder_tree = get_folder_structure(path)

    return jsonify({"structure": folder_tree})

@app.route("/analyze", methods=["POST"])
def analyze():
    path = request.json["repo_path"]
    logging.info(f"Analyzing: {path}")
    cache_key = f"analysis:{path}"

    cached_result = redis_client.get(cache_key)
    if cached_result:
        logging.info("Returning cached result")
        cached_data = json.loads(cached_result)
        return jsonify({
            "status": "cached",
            "json_path": cached_data["json_path"],
            "json_data": cached_data["json_data"]
        })

    if path.startswith("http://") or path.startswith("https://"):
        final_path, _, err = clone_repo_and_get_subpath(path)
        if err:
            logging.error(f"Analysis error: {err}")
            return jsonify({"error": err}), 400
    else:
        final_path = path

    if not os.path.exists(final_path):
        msg = f"Path '{final_path}' does not exist"
        logging.error(msg)
        return jsonify({"error": msg}), 400

    try:
        json_path, result = run_analysis(final_path)
        logging.info(f"Analysis complete. Result at: {json_path}")
    except Exception as e:
        logging.exception("Analysis failed")
        return jsonify({"error": str(e)}), 500

    redis_client.set(cache_key, json.dumps({
        "json_path": json_path,
        "json_data": result
    }))

    return jsonify({
        "status": "complete",
        "json_path": json_path,
        "json_data": result
    })

@app.route("/download_json")
def download_json():
    path = request.args.get("path")
    logging.info(f"Download requested for: {path}")
    return send_file(path, as_attachment=True)

@app.route("/refresh_db")
def refresh_db():
    logging.info("Refreshing database data")
    return jsonify({
        "codebase_files": serialize_cursor(codebase_files.find()),
        "chunks": serialize_cursor(chunks.find()),
        "analysis_results": serialize_cursor(analysis_results.find())
    })

@app.route("/clear_db", methods=["POST"])
def clear_db():
    logging.warning("Clearing MongoDB and Redis")
    codebase_files.delete_many({})
    chunks.delete_many({})
    analysis_results.delete_many({})
    redis_client.flushdb()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    logging.info("Starting Flask app...")
    app.run(host="0.0.0.0", port=8000, debug=True)
