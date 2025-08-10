# Load libraries
library(dplyr)
library(lme4)

# ==== Load data ====
messages <- read.csv("messages.csv", stringsAsFactors = FALSE)
preferences <- read.csv("preferences.csv", stringsAsFactors = FALSE)

# ==== Prepare data ====

# Convert relevant columns to factors
messages <- messages %>%
  mutate(
    tone = factor(tone),
    style = factor(style),
    sex = factor(sex),
    race_ethn = factor(race_ethn),
    context = factor(context),
    marital_status = factor(marital_status),
    minoritized = as.logical(minoritized)
  )

preferences <- preferences %>%
  mutate(
    type = factor(type),
    identifier = factor(identifier),
    sex = factor(sex),
    race_ethn = factor(race_ethn),
    marital_status = factor(marital_status),
    minoritized = as.logical(minoritized)
  )

# Split preferences into tone and style
pref_tone <- filter(preferences, type == "tone")
pref_style <- filter(preferences, type == "style")

# ==== 1. Do people have message tone and/or style preferences? (stated preferences) ====

m1 <- lm(rating ~ identifier, data = pref_style)
cat("\n--- Style Preferences Model ---\n")
print(summary(m1))

m2 <- lm(rating ~ identifier, data = pref_tone)
cat("\n--- Tone Preferences Model ---\n")
print(summary(m2))