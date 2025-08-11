set.seed(123)

# --- Parameters ---
n_participants <- 100

# Tone, style, and context categories
tones <- c("legitimizing", "caring_supportive", "self_efficacy",
           "acknowledging", "value_affirmation", "norms")
styles <- c("formal", "informal")
contexts <- c(
  "high_increasing", "high_decreasing",
  "low_increasing", "low_decreasing"
)

# 1 ------------------------------------------------------------------
# We should see clear differences in actual ratings of messages.
# Within each tone/style, people's ratings should be pretty similar
# to one another (low variance) but between tone/style ratings
# should be noticeably different (high variance).

# Example:
# People might rate the norms tone at around a 6/7
# but the self-efficacy tone at around a 3/7.
tone_means <- c(
  legitimizing      = 1,
  caring_supportive = 2,
  self_efficacy     = 3,
  acknowledging     = 4,
  value_affirmation = 5,
  norms             = 6
)
style_means <- c(
  formal            = 3,
  informal          = 5
)

# here we set the desired means and adjustment based on style

# 2 ------------------------------------------------------------------

# 3 ------------------------------------------------------------------
# We want to observe a demographic difference.
# Create a sex variable (male/female) where there
# is a clear difference in tone/style preferences.

# Example: prefer "norms" messages and women prefer "legitimizing" messages.
tone_sex_adj <- list(
  male = c(
    legitimizing = -0.3,
    norms        =  0.8
  ),
  female = c(
    legitimizing =  0.8,
    norms        = -0.3
  )
)
# Males rate "norms" higher, "legitimizing" lower
# Females rate "legitimizing" higher, "norms" lower
style_sex_adj <- list(
  male = c(
    formal       = -0.3,
    informal     =  0.8
  ),
  female = c(
    formal       = 0.8,
    informal     =  -0.3
  )
)

# 4 ------------------------------------------------------------------


# ================ Participant Generation ================
n <- n_participants
repeat_even <- function(x, total) {
    rep(x, length.out = total)
}
participant_id <- 1:n
age               <- sample(repeat_even(18:65, n))
sex               <- sample(repeat_even(c("male", "female"), n))
gender_id         <- sample(repeat_even(c("man", "woman", "nonbinary"), n))
sexual_orientation<- sample(repeat_even(c("heterosexual", "gay/lesbian", "bisexual", "other"), n))
race_ethn         <- sample(repeat_even(c("white", "black", "asian", "hispanic", "other"), n))
education         <- sample(repeat_even(c("high_school", "bachelor", "master", "phd"), n))
income            <- sample(repeat_even(seq(20000, 100000, by = 20000), n))
marital_status    <- sample(repeat_even(c("single", "married", "divorced", "widowed"), n))
no_in_household   <- sample(repeat_even(1:6, n))
minoritized       <- sample(repeat_even(c("yes", "no"), n))
income_adj        <- income / no_in_household
participants <- data.frame(
    participant_id,
    age,
    sex,
    gender_id,
    sexual_orientation,
    race_ethn,
    education,
    income,
    marital_status,
    no_in_household,
    minoritized,
    income_adj
)
write.csv(participants, file = 'participants.csv', row.names = FALSE)

# ================ Tone Preference Generation ================
participant_id <- rep(participants$participant_id, each = length(tones))
participant_sex <- rep(participants$sex, each = length(tones))
tone <- rep(tones, times = nrow(participants))

# Create a function to get adjusted tone mean
get_adjusted_tone_mean <- function(tone, sex) {
  base_mean <- tone_means[tone]
  adj <- 0
  if (!is.null(tone_sex_adj[[sex]])) {
    adj <- tone_sex_adj[[sex]][tone]
    if (is.na(adj)) adj <- 0  # If no adjustment for that tone, set to 0
  }
  return(base_mean + adj)
}

# Generate adjusted tone means vector
adjusted_means <- mapply(get_adjusted_tone_mean, tone, participant_sex)

tone_rating <- rnorm(length(tone), mean = adjusted_means, sd = 0.45)
tone_rating <- pmin(pmax(tone_rating, 1), 7)
tone_rating <- round(tone_rating)
tone_preferences <- data.frame(
  participant_id = participant_id,
  tone = tone,
  tone_rating = tone_rating
)
# Join demographics by participant_id
tone_preferences <- merge(tone_preferences, participants, by = "participant_id", all.x = TRUE)
write.csv(tone_preferences, file = 'tone_preferences.csv', row.names = FALSE)
# ================ Tone Preference Generation ================


# ================ Tone Preference Analysis ================
# analyze the mean and sd of tone ratings
library(dplyr)
data_summary <- tone_preferences %>%
    group_by(tone) %>%
    summarise(
        mean_rating = mean(tone_rating),
        sd_rating   = sd(tone_rating),
        n           = n()
    ) %>%
    arrange(mean_rating)
print(data_summary)

library(dplyr)
library(tidyr)

# Summary by tone and sex
data_summary_sex <- tone_preferences %>%
  group_by(tone, sex) %>%
  summarise(
    mean_rating = mean(tone_rating),
    sd_rating = sd(tone_rating),
    n = n(),
    .groups = 'drop'
  ) %>%
  arrange(tone, sex)
# Calculate mean difference between sexes per tone
mean_diff_sex <- data_summary_sex %>%
  select(tone, sex, mean_rating) %>%
  pivot_wider(names_from = sex, values_from = mean_rating) %>%
  mutate(
    mean_diff = male - female
  )

print(mean_diff_sex)
# ================ Tone Preference Analysis ================


# ================ Style Preference Generation ================
participant_id <- rep(participants$participant_id, each = length(styles))
participant_sex <- rep(participants$sex, each = length(styles))
style <- rep(styles, times = nrow(participants))

# Create a function to get adjusted style mean
get_adjusted_style_mean <- function(style, sex) {
  base_mean <- style_means[style]
  adj <- 0
  if (!is.null(style_sex_adj[[sex]])) {
    adj <- style_sex_adj[[sex]][style]
    if (is.na(adj)) adj <- 0  # If no adjustment for that style, set to 0
  }
  return(base_mean + adj)
}

# Generate adjusted style means vector
adjusted_means <- mapply(get_adjusted_style_mean, style, participant_sex)

style_rating <- rnorm(length(style), mean = adjusted_means, sd = 0.45)
style_rating <- pmin(pmax(style_rating, 1), 7)
style_rating <- round(style_rating)
style_preferences <- data.frame(
  participant_id = participant_id,
  style = style,
  style_rating = style_rating
)
# Join demographics by participant_id
style_preferences <- merge(style_preferences, participants, by = "participant_id", all.x = TRUE)
write.csv(style_preferences, file = 'style_preferences.csv', row.names = FALSE)
# ================ Style Preference Generation ================

# ================ Style Preference Analysis ================
# analyze the mean and sd of style ratings
library(dplyr)
data_summary <- style_preferences %>%
    group_by(style) %>%
    summarise(
        mean_rating = mean(style_rating),
        sd_rating   = sd(style_rating),
        n           = n()
    ) %>%
    arrange(mean_rating)
print(data_summary)

library(dplyr)
library(tidyr)

# Summary by style and sex
data_summary_sex <- style_preferences %>%
  group_by(style, sex) %>%
  summarise(
    mean_rating = mean(style_rating),
    sd_rating = sd(style_rating),
    n = n(),
    .groups = 'drop'
  ) %>%
  arrange(style, sex)
# Calculate mean difference between sexes per style
mean_diff_sex <- data_summary_sex %>%
  select(style, sex, mean_rating) %>%
  pivot_wider(names_from = sex, values_from = mean_rating) %>%
  mutate(
    mean_diff = male - female
  )

print(mean_diff_sex)
# ================ Style Preference Analysis ================


# # ================ Message Preference Generation for tonesxstylexcontext ================
# participant_id <- rep(participants$participant_id, each = length(tones) * length(styles) * length(contexts))
# tone <- rep(rep(tones, each = length(styles) * length(contexts)), times = nrow(participants))
# style <- rep(rep(styles, each = length(contexts)), times = length(tones) * nrow(participants))
# context <- rep(contexts, times = length(tones) * length(styles) * nrow(participants))
# message_rating <- rnorm(length(tone), mean = tone_means[tone] + style_means[style], sd = 0.65)
# message_rating <- pmin(pmax(message_rating, 1), 7)
# message_rating <- round(message_rating)
# message_preferences <- data.frame(
#     participant_id = participant_id,
#     tone = tone,
#     style = style,
#     context = context,
#     message_rating = message_rating
# )
# # Join demographics by participant_id
# message_preferences <- merge(message_preferences, participants, by = "participant_id", all.x = TRUE)
# # analyze the mean and sd of message ratings
# library(dplyr)
# data_summary <- message_preferences %>%
#     group_by(tone, style, context) %>%
#     summarise(
#         mean_rating = mean(message_rating),
#         sd_rating   = sd(message_rating),
#         n           = n()
#     ) %>%
#     arrange(mean_rating)
# print(data_summary)
# write.csv(message_preferences, file = 'message_preferences.csv', row.names = FALSE)