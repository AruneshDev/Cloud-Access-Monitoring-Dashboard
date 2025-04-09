import pandas as pd
from scipy.stats import zscore
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('parsed_cloudtrail_events.csv')
df['eventTime'] = pd.to_datetime(df['eventTime'])

# Filter only login events
login_df = df[df['eventName'].isin(['ConsoleLogin', 'AssumeRole'])].copy()

# Assign user roles (you can expand this logic)
def categorize_user(user):
    user = str(user).lower()
    if 'admin' in user:
        return 'Admin'
    elif 'dev' in user:
        return 'Developer'
    elif 'ext' in user:
        return 'External'
    else:
        return 'Unknown'

login_df['role'] = login_df['userName'].apply(categorize_user)

# Group by timestamp + role
login_df['hour'] = login_df['eventTime'].dt.floor('H')
grouped = login_df.groupby(['hour', 'role']).size().reset_index(name='count')

# Pivot for plotting
pivot_df = grouped.pivot(index='hour', columns='role', values='count').fillna(0)

# Anomaly Detection using z-score
z_scores = pivot_df.apply(zscore)
anomalies = (z_scores.abs() > 2)

# Save anomaly table
anomaly_df = pivot_df[anomalies.any(axis=1)]
anomaly_df.to_csv("anomaly_events.csv")
print(f"Found {len(anomaly_df)} anomalous login times.")

# Plot
pivot_df.plot(figsize=(12, 6), title='Hourly Logins by Role')
plt.axhline(y=pivot_df.mean().max() + 2*pivot_df.std().max(), color='r', linestyle='--', label='Z-score Threshold')
plt.legend()
plt.xlabel("Hour")
plt.ylabel("Logins")
plt.tight_layout()
plt.savefig("screenshots/login_anomaly_plot.png")
plt.show()
