from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import os
import shutil
import time
import psutil
import requests
import subprocess

# ✅ Path to Elasticsearch Hadoop Connector JAR
ES_HADOOP_JAR = "file:///C:/hadoop/lib/elasticsearch-spark-30_2.12-8.17.0.jar"

# ✅ HDFS Binary Path (Fix for Windows)
HDFS_CMD = "C:\\hadoop\\bin\\hdfs.cmd"  # ✅ Force full path

# ✅ Elasticsearch Authentication
ES_USER = "elastic"
ES_PASS = "rc5t-rQhGYoxyG3cP4Nb"

# ✅ Function to check if a process is running
def is_process_running(process_name):
    """Check if a given process is running"""
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False

# ✅ Function to wait for Elasticsearch
def wait_for_elasticsearch(host="localhost", port=9200, retries=10, delay=5):
    """Wait for Elasticsearch to be ready before starting Spark"""
    url = f"http://{host}:{port}"
    auth = (ES_USER, ES_PASS)  # ✅ Use authentication

    for i in range(retries):
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                print(f"✅ Elasticsearch is running! Proceeding with Spark processing...")
                return True
            else:
                print(f"⚠️ Elasticsearch returned {response.status_code}, retrying...")
        except requests.ConnectionError:
            print(f"⚠️ Elasticsearch not available, retrying in {delay} seconds... ({i+1}/{retries})")
        time.sleep(delay)

    print("❌ Elasticsearch is not available. Exiting...")
    exit(1)

# ✅ Function to check if HDFS is running (Fixed for Windows)
def is_hdfs_running():
    """Check if Hadoop HDFS is running"""
    try:
        result = subprocess.run([HDFS_CMD, "dfsadmin", "-report"], capture_output=True, text=True, timeout=5)

        if "Live datanodes" in result.stdout:
            return True
        else:
            print(f"❌ HDFS Check Failed: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ HDFS Check Error: {e}")
        return False

# ✅ Function to wait for HDFS
def wait_for_hdfs(retries=10, delay=5):
    """Wait for HDFS to be ready before saving files"""
    for i in range(retries):
        if is_hdfs_running():
            print("✅ HDFS is running! Proceeding with Spark processing...")
            return True
        print(f"⚠️ HDFS not available, retrying in {delay} seconds... ({i+1}/{retries})")
        time.sleep(delay)

    print("❌ HDFS is not running. Exiting...")
    exit(1)

# ✅ Ensure Elasticsearch & HDFS are ready
wait_for_elasticsearch()
wait_for_hdfs()

# ✅ Initialize Spark Session
spark = SparkSession.builder \
    .appName("WeatherAnalysis") \
    .config("spark.jars", ES_HADOOP_JAR) \
    .config("spark.es.nodes", "localhost") \
    .config("spark.es.port", "9200") \
    .config("spark.es.net.http.auth.user", ES_USER) \
    .config("spark.es.net.http.auth.pass", ES_PASS) \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()

try:
    # ✅ Read weather data from Elasticsearch
    weather_df = spark.read.format("org.elasticsearch.spark.sql") \
        .option("es.resource", "weather_data") \
        .option("es.nodes", "localhost") \
        .option("es.port", "9200") \
        .option("es.net.http.auth.user", ES_USER) \
        .option("es.net.http.auth.pass", ES_PASS) \
        .option("es.nodes.wan.only", "true") \
        .load()

    # ✅ Compute average weather metrics per city
    weather_transformed = weather_df.groupBy("location").agg(
        avg("t_2m:C").alias("avg_temperature"),
        avg("wind_speed_10m:ms").alias("avg_wind_speed"),
        avg("msl_pressure:hPa").alias("avg_pressure")
    )

    # ✅ Save results to Elasticsearch
    weather_transformed.write.format("org.elasticsearch.spark.sql") \
        .option("es.resource", "weather_analysis") \
        .option("es.nodes", "localhost") \
        .option("es.port", "9200") \
        .option("es.net.http.auth.user", ES_USER) \
        .option("es.net.http.auth.pass", ES_PASS) \
        .option("es.nodes.wan.only", "true") \
        .mode("overwrite") \
        .save()

    # ✅ Save to CSV locally
    csv_path_local = "weather_analysis.csv"
    weather_transformed.write.csv(csv_path_local, header=True, mode="overwrite")

    # ✅ Save to HDFS (Fixed for Windows)
    hdfs_path = "/weather_analysis.csv"
    os.system(f'"{HDFS_CMD}" dfs -put -f {csv_path_local} {hdfs_path}')

    print("✔️ Spark Processing Completed. Results saved to Elasticsearch and", csv_path_local)

finally:
    # ✅ Stop Spark
    spark.stop()
    
    # ✅ Ensure Java (Spark) is fully stopped
    print("🔴 Stopping all Java processes (Spark)...")
    subprocess.run(["taskkill", "/F", "/IM", "java.exe"], capture_output=True, text=True)

    # ✅ Wait before cleanup
    print("⏳ Waiting for Spark to release file locks...")
    time.sleep(5)

    # ✅ Unlock & Delete Temp Files
    def unlock_file(file_path):
        """Unlock a locked file by killing the process using it"""
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                for item in proc.open_files():
                    if file_path in item.path:
                        print(f"🔴 Killing process {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
                        time.sleep(2)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    # ✅ Delete Spark Temp Files
    spark_temp_dir = os.path.expanduser("~/AppData/Local/Temp/")
    for folder in os.listdir(spark_temp_dir):
        if folder.startswith("spark-"):
            temp_path = os.path.join(spark_temp_dir, folder)
            unlock_file(temp_path)  # 🚀 Unlock before deleting
            try:
                shutil.rmtree(temp_path, ignore_errors=False)
                print(f"✅ Deleted Spark Temp Folder: {temp_path}")
            except Exception as e:
                print(f"⚠️ Could not delete {temp_path}: {e}")

print("✅ Cleanup Completed: No leftover Spark temp files.")
