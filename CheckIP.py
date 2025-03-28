import os
import sys
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
import logging

# Add the notification folder to the Python path
notification_folder = r'C:\Users\farha\PycharmProjects\PythonProject\.venv\Scripts\notifications'  # Update this path accordingly
sys.path.append(notification_folder)

from EmailIntegration import send_email
from SlackIntegration import send_slack_message
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

folder_path = r'C:\inetpub\logs\LogFiles\W3SVC2'
files_folder = r'files'  # Specify the folder where files will be saved
ip_log_file = os.path.join(files_folder, "suspicious_ips.log")
ip_threshold_file = os.path.join(files_folder, "threshold.txt")
suspicious_ip_file = os.path.join(files_folder, "suspicious_ips.txt")

# Make sure the folder exists
if not os.path.exists(files_folder):
    os.makedirs(files_folder)

def find_latest_file(folder_path):
    """Finds the most recent file in the given folder."""
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            logging.warning("No files found in the folder.")
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    except Exception as e:
        logging.error(f"Error finding the latest file: {e}")
        return None

def extract_ip_list(file_path):
    """Extracts the IP addresses in order from the log file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        ip_list = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 10:
                c_ip = parts[-5]  # Assuming the c-ip is in the 5th last column
                ip_list.append(c_ip)
        return ip_list
    except Exception as e:
        logging.error(f"Error extracting IPs: {e}")
        return []

def extract_ip_timestamps(file_path):
    """Extracts IP addresses and timestamps from the log file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        ip_list = []
        timestamp_list = []

        for line in lines:
            parts = line.split()
            if len(parts) >= 10:
                c_ip = parts[-5]
                timestamp = parts[0] + ' ' + parts[1]
                ip_list.append(c_ip)
                timestamp_list.append(timestamp)

        ip_df = pd.DataFrame({
            'c-ip': ip_list,
            'timestamp': timestamp_list
        })

        ip_df['timestamp'] = pd.to_datetime(ip_df['timestamp'], format='%Y-%m-%d %H:%M:%S')

        return ip_df

    except Exception as e:
        logging.error(f"Error extracting IPs and timestamps: {e}")
        return pd.DataFrame()

def filter_ips_within_timeframe(df, time_threshold=2):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values(by=['c-ip', 'timestamp'], inplace=True)
    df['time_diff'] = df.groupby('c-ip')['timestamp'].diff().dt.total_seconds()
    return df[df['time_diff'] <= time_threshold]

def analyze_ips(filtered_df):
    ip_counts = filtered_df.groupby("c-ip").size().reset_index(name="request_count")
    
    ip_counts = ip_counts.sort_values(by='request_count')
    ip_counts['index'] = range(len(ip_counts))
    model = LinearRegression()
    model.fit(ip_counts[['index']], ip_counts['request_count'])
    
    ip_counts['expected_count'] = model.predict(ip_counts[['index']])
    logging.info(f"Expected Counts: {ip_counts['expected_count'].head()}")
    ip_counts['residual'] = ip_counts['request_count'] - ip_counts['expected_count']
    logging.info(f"Residuals: {ip_counts['residual'].head()}")
    iso_forest = IsolationForest(contamination=0.2, random_state=10)
    ip_counts['iso_forest_anomaly'] = iso_forest.fit_predict(ip_counts[['residual']])
    logging.info(f"Anomalies: {ip_counts['iso_forest_anomaly'].head()}")
    
    ip_counts['threshold'] = ip_counts['expected_count'] + (ip_counts['expected_count'].std() * 1.5)
    logging.info(f"Threshold: {ip_counts['threshold'].head()}")
    ip_counts['regression_anomaly'] = ip_counts['request_count'] > ip_counts['threshold']
    
    suspicious_ips = ip_counts[(ip_counts['iso_forest_anomaly'] == -1) & (ip_counts['request_count'] > ip_counts['threshold'])]
    
    total_ips_detected = filtered_df["c-ip"].nunique()
    return suspicious_ips, total_ips_detected

def log_suspicious_ips(all_ips, suspicious_ips):
    """Appends each IP occurrence and suspicious IPs to a log file."""
    log_path = os.path.abspath(ip_log_file)
    logging.info(f"Appending IPs to {log_path}")
    
    # Open the file in write mode to clear its content before writing new data
    with open(ip_log_file, "w") as file:
        file.write("All IPs:\n")
        ip_counts = defaultdict(int)
        for ip in all_ips:
            ip_counts[ip] += 1
        
        for ip, count in ip_counts.items():
            file.write(f"IP: {ip} Occurrences {count}\n")
        
        if not suspicious_ips.empty:
            file.write("\nSuspicious IPs:\n")
            for index, row in suspicious_ips.iterrows():
                file.write(f"Suspicious IP: {row['c-ip']} with {row['request_count']} requests\n")
    
    logging.info(f"IPs and suspicious IPs appended successfully in {log_path}")

def log_suspicious_ips_to_file(suspicious_ips):
    """Logs suspicious IPs to a separate text file, just the IPs without occurrence or label."""
    log_path = os.path.abspath(suspicious_ip_file)
    logging.info(f"Logging suspicious IPs to {log_path}")
    
    # Open the file in write mode to clear its content before writing new data
    with open(log_path, "w") as file:
        for index, row in suspicious_ips.iterrows():
            file.write(f"{row['c-ip']}\n")  # Just the IP without any label or occurrences
    
    logging.info(f"Suspicious IPs logged successfully in {log_path}")

def log_threshold_ips(ip_counts):
    """Logs threshold data for IPs to a log file."""
    log_path = os.path.abspath(ip_threshold_file)
    logging.info(f"Appending threshold IPs to {log_path}")

    # Open the file in write mode to clear its content before writing new data
    with open(log_path, "w") as file:
        file.write("Threshold IPs:\n")
        for index, row in ip_counts.iterrows():
            file.write(f"IP: {row['c-ip']}, Requests: {row['request_count']}, "
                       f"Expected: {row['expected_count']}, Residual: {row['residual']}, "
                       f"Threshold: {row['threshold']}, Regression Anomaly: {row['regression_anomaly']}\n")

    logging.info(f"Threshold IPs logged successfully in {log_path}")

def process_logs():
    latest_file = find_latest_file(folder_path)
    if latest_file:
        logging.info(f"Most recent file found: {latest_file}")

        ip_list = extract_ip_list(latest_file)
        ip_df = extract_ip_timestamps(latest_file)
        filtered_df = filter_ips_within_timeframe(ip_df)

        if not filtered_df.empty:
            suspicious_ips, total_ips_detected = analyze_ips(filtered_df)
            logging.info(f"Total IPs detected in logs: {total_ips_detected}")

            if not suspicious_ips.empty:
                log_suspicious_ips(ip_list, suspicious_ips)
                log_suspicious_ips_to_file(suspicious_ips)  # Log only IPs to the file

                subject = "Suspicious Activity Detected for IPs with More Than 5 Requests"
                message = "High-Risk Suspicious IPs Detected:\n"
                for index, row in suspicious_ips.iterrows():
                    message += f"Suspicious IP: {row['c-ip']} with {row['request_count']} requests\n"
                send_email(subject, message)
                send_slack_message(message)
                logging.info(f"Suspicious IPs logged successfully.")
            else:
                logging.info("No suspicious IPs detected in the logs.")

            log_threshold_ips(suspicious_ips) 
            
            logging.info("Threshold IPs saved to threshold_ips.xlsx.")

        else:
            logging.warning("No valid c-ip found in the log file within the time threshold.")
    else:
        logging.warning("No latest file found.")

def additional_processing():
    """Placeholder function to simulate extended processing for line expansion."""
    logging.info("Performing additional processing...")
    for i in range(50):
        logging.debug(f"Processing step {i+1}...")
    logging.info("Additional processing completed.")

def extended_logging():
    """Logs additional details for debugging purposes."""
    logging.info("Extended logging begins...")
    for i in range(50):
        logging.debug(f"Logging extra detail {i+1}")
    logging.info("Extended logging completed.")

if __name__ == "__main__":
    process_logs()
    additional_processing()
    extended_logging()
