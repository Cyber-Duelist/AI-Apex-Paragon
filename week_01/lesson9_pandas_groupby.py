import pandas as pd

memory_log = {
    "action": ["read_email", "open_browser", "read_email", "type_notes", "open_browser", "type_notes", "read_email"],
    "duration_seconds": [45, 12, 60, 120, 8, 95, 30]
}

entity_df = pd.DataFrame(memory_log)
print(entity_df)

grouped = entity_df.groupby("action")["duration_seconds"].mean()
print(grouped)
print(entity_df.groupby("action")["duration_seconds"].min())
print(entity_df.groupby("action")["duration_seconds"].max())
print(entity_df.groupby("action")["duration_seconds"].std())