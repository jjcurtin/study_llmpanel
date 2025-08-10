import numpy as np
import pandas as pd
from itertools import product

SUBJECTS = 100

def generate_qualtrics_data(
    n_subjects = SUBJECTS,
    tones = ["value_affirmation", "norms", "acknowledging", "self_efficacy", "caring_supportive", "legitimizing"],
    styles = ["formal", "informal"],
    contexts = ["high_inc", "high_dec", "low_inc", "low_dec"],
    demographic_relationships = None,
    random_state = None
):
    if random_state is not None:
        np.random.seed(random_state)
    
    #===================================================================================================================
    # Initialize subjects
    subjects = pd.DataFrame({
        "sub_id": np.arange(1, n_subjects + 1),
        "age": np.round(np.random.normal(40, 12, n_subjects)).astype(int),
        "sex": np.random.choice(["Male", "Female"], size = n_subjects),
        "race_ethn": np.random.choice(["White", "Black", "Hispanic", "Asian", "Other"], size = n_subjects),
        "education": np.random.choice(["HS", "Some College", "Bachelor", "Graduate"], size = n_subjects),
        "income": np.random.choice(np.arange(20000, 150001, 5000), size = n_subjects),
        "no_in_household": np.random.randint(1, 7, size = n_subjects),
        "marital_status": np.random.choice(["Single", "Married", "Divorced"], size = n_subjects)
    })
    subjects["income_adj"] = subjects["income"] / subjects["no_in_household"]
    subjects["minoritized"] = subjects["race_ethn"] != "White"
    #===================================================================================================================
    
    #===================================================================================================================
    pref_rows = []
    for _, subj in subjects.iterrows():

        #---------------------------------------------------------------------------------------------------------------
        # Tones
        for tone in tones:
            base = np.random.normal(5, 1)
            demo_effect = 0
            if demographic_relationships:
                for rel in demographic_relationships:
                    if subj[rel["var"]] == rel["level"]:
                        demo_effect += rel["effect"]
            rating = int(np.clip(round(base + demo_effect), 1, 7))
            pref_rows.append({**subj, "type": "tone", "identifier": tone, "rating": rating})
        #---------------------------------------------------------------------------------------------------------------
        
        #---------------------------------------------------------------------------------------------------------------
        # Styles
        for style in styles:
            base = np.random.normal(5, 1)
            demo_effect = 0
            if demographic_relationships:
                for rel in demographic_relationships:
                    if subj[rel["var"]] == rel["level"]:
                        demo_effect += rel["effect"]
            rating = int(np.clip(round(base + demo_effect), 1, 7))
            pref_rows.append({**subj, "type": "style", "identifier": style, "rating": rating})
        #---------------------------------------------------------------------------------------------------------------
    
    pref_df = pd.DataFrame(pref_rows)
    #===================================================================================================================
    
    #===================================================================================================================
    # --- Messages (48 per subject) ---
    message_conditions = pd.DataFrame(list(product(tones, styles, contexts)), columns = ["tone", "style", "context"])
    df = subjects.assign(key = 1).merge(message_conditions.assign(key = 1), on = "key").drop("key", axis = 1)
    
    #---------------------------------------------------------------------------------------------------------------
    tone_pref_df = pref_df.query("type == 'tone'")[["sub_id", "identifier", "rating"]].rename(
        columns={"identifier": "tone", "rating": "pref_rating_tone"})
    style_pref_df = pref_df.query("type == 'style'")[["sub_id", "identifier", "rating"]].rename(
        columns={"identifier": "style", "rating": "pref_rating_style"})
    
    df = df.merge(tone_pref_df, on = ["sub_id", "tone"])
    df = df.merge(style_pref_df, on = ["sub_id", "style"])
    #---------------------------------------------------------------------------------------------------------------
    
    #---------------------------------------------------------------------------------------------------------------
    # Actual ratings: correlated with preferences + noise, integer 1–7
    base_actual = 0.99 * ((df["pref_rating_style"] + df["pref_rating_tone"]) / 2) + 0.3 * np.random.normal(5, 1, len(df))
    df["actual_rating"] = np.clip(np.round(base_actual), 1, 7).astype(int)
    #===================================================================================================================
    
    return pref_df, df

# Example usage
pref_df, msg_df = generate_qualtrics_data(
    n_subjects = 50,
    demographic_relationships = [{"var": "sex", "level": "Female", "effect": 0.3}],
    random_state = 42
)

pref_df.to_csv("preferences.csv", index=False)

msg_df_filtered = msg_df[
    [
        "sub_id", "age", "sex", "race_ethn", "education", "income", "no_in_household",
        "marital_status", "income_adj", "minoritized", "tone", "style", "context", "actual_rating"
    ]
]
msg_df_filtered.to_csv("messages.csv", index=False)

print("preferences.csv:", pref_df.shape)  # n_subjects * 8
print("messages.csv:", msg_df_filtered.shape)  # n_subjects * 48
