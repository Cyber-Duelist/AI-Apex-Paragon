import pandas as pd

data = {
    "title": ["NDA_2026", "Employment_Contract", "Lease_Agreement"],
    "word_count": [1500, 3200, 800]
}

data_df = pd.DataFrame(data)
print(data_df)


#-------Challenge-----------
memory_log = {"action": ["read_email", "open_browser", "type_notes"], "duration_seconds": [45,12,120]}
entity_df = pd.DataFrame(memory_log)
print(entity_df)
print(entity_df["duration_seconds"].mean())
print(entity_df["duration_seconds"].min())
print(entity_df["duration_seconds"].max())
print(entity_df.describe())

slow_actions = entity_df[entity_df["duration_seconds"] > 50]
print(slow_actions)

fast_actions =entity_df[entity_df["duration_seconds"] < 50]
print(fast_actions)