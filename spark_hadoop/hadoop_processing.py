import requests
import json
import os
import subprocess

# ✅ Elasticsearch Configuration
ES_HOST = "http://localhost:9200"
ES_INDEX = "weather_data"
ES_USER = "elastic"
ES_PASS = "rc5t-rQhGYoxyG3cP4Nb"

# ✅ HDFS Paths
HDFS_INPUT_PATH = "/weather_data.json"
HDFS_OUTPUT_PATH = "/output_weather_analysis"

# ✅ Hadoop Paths
HADOOP_HOME = "C:\\hadoop"
HADOOP_BIN = os.path.join(HADOOP_HOME, "bin")
HDFS_CMD = os.path.join(HADOOP_BIN, "hdfs.cmd")
HADOOP_CMD = os.path.join(HADOOP_BIN, "hadoop.cmd")
HADOOP_STREAMING_JAR = os.path.join(HADOOP_HOME, "share", "hadoop", "tools", "lib", "hadoop-streaming-2.9.2.jar")

if not os.path.exists(HADOOP_STREAMING_JAR):
    print(f"❌ ERROR: Hadoop Streaming JAR not found at: {HADOOP_STREAMING_JAR}")
    exit(1)

# ✅ Fetch Weather Data from Elasticsearch
print("🔄 Fetching weather data from Elasticsearch...")
url = f"{ES_HOST}/{ES_INDEX}/_search?size=10000"
headers = {"Content-Type": "application/json"}
auth = (ES_USER, ES_PASS)

response = requests.get(url, headers=headers, auth=auth)

if response.status_code == 200:
    data = response.json()
    hits = data["hits"]["hits"]

    # ✅ Write data to a local file
    local_json_file = "weather_data.json"
    with open(local_json_file, "w", encoding="utf-8") as f:
        for hit in hits:
            json.dump(hit["_source"], f)
            f.write("\n")

    # ✅ Ensure HDFS input directory exists
    subprocess.run([HDFS_CMD, "dfs", "-mkdir", "-p", "/"], check=True)

    # ✅ Upload JSON file to HDFS
    print(f"🚀 Uploading {local_json_file} to HDFS at {HDFS_INPUT_PATH}...")
    subprocess.run([HDFS_CMD, "dfs", "-put", "-f", local_json_file, HDFS_INPUT_PATH], check=True)
    print(f"✅ Data successfully indexed in HDFS at {HDFS_INPUT_PATH}")

    # ✅ Remove existing output directory in HDFS (if exists)
    subprocess.run([HDFS_CMD, "dfs", "-rm", "-r", HDFS_OUTPUT_PATH], stderr=subprocess.DEVNULL)

    # ✅ Run Hadoop Streaming Job
    print("🔄 Running Hadoop Streaming Job...")

    hadoop_cmd = [
        HADOOP_CMD, "jar", HADOOP_STREAMING_JAR,
        "-D", "mapreduce.job.reduces=1",
        "-input", HDFS_INPUT_PATH,
        "-output", HDFS_OUTPUT_PATH,
        "-mapper", "python temperature_mapper.py",
        "-reducer", "python temperature_reducer.py",
        "-file", "temperature_mapper.py",
        "-file", "temperature_reducer.py"
    ]

    process = subprocess.run(hadoop_cmd, capture_output=True, text=True)

    if process.returncode == 0:
        print(f"✅ Hadoop Streaming Processing Completed. Results saved in HDFS at {HDFS_OUTPUT_PATH}")
    else:
        print(f"❌ Hadoop Streaming Failed!\nError:\n{process.stderr}")

else:
    print(f"❌ Failed to retrieve data from Elasticsearch: {response.status_code}, {response.text}")
