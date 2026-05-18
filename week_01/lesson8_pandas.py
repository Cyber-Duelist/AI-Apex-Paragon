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