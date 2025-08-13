# random seed logic

# qualtrics looks like
# Q1,Q2,Q3,Q4,Q5_6,Q6,Q7,Q8,Q9,Q10,Q1_1,Q2_1,Q3_1,Q4_1,Q5_1.1,Q6_1,Q7_1,Q8_1,_1,_1.1,_1.2,_1.3,_1.4,_1.5,_1.6,_1.7,_1.8,_1.9,_1.10,_1.11,_1.12,_1.13,_1.14,_1.15,_1.16,_1.17,_1.18,_1.19,_1.20,_1.21,_1.22,_1.23,_1.24,_1.25,_1.26,_1.27,_1.28,_1.29,_1.30,_1.31,_1.32,_1.33,_1.34,_1.35,_1.36,_1.37,_1.38,_1.39,_1.40,_1.41,_1.42,_1.43,_1.44,_1.45,_1.46,_1.47
if (!file.exists("times_run.txt")) {
  writeLines("1", "times_run.txt")
}
file_conn <- file("times_run.txt", "r")
times_run <- as.integer(readLines(file_conn))
print(times_run)
close(file_conn)
set.seed(times_run)
times_run <- times_run + 1
writeLines(as.character(times_run), "times_run.txt")

n_participants <- 100
standard_deviation <- 0.3

tones <- c("legitimizing", "caring_supportive", "self_efficacy",
           "acknowledging", "value_affirmation", "norms")
styles <- c("formal", "informal")
contexts <- c(
  "high_increasing", "high_decreasing",
  "low_increasing", "low_decreasing"
)

# ================ Preferences Setup ================
tone_means <- c(
  legitimizing      = 1,
  caring_supportive = 2,
  self_efficacy     = 3,
  acknowledging     = 4,
  value_affirmation = 5,
  norms             = 6
)
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
get_adjusted_tone_mean <- function(tone, sex) {
  base_mean <- tone_means[tone]
  adj <- 0
  if (!is.null(tone_sex_adj[[sex]])) {
    adj <- tone_sex_adj[[sex]][tone]
    if (is.na(adj)) adj <- 0
  }
  return(base_mean + adj)
}

style_means <- c(
  formal            = 3,
  informal          = 5
)
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
get_adjusted_style_mean <- function(style, sex) {
  base_mean <- style_means[style]
  adj <- 0
  if (!is.null(style_sex_adj[[sex]])) {
    adj <- style_sex_adj[[sex]][style]
    if (is.na(adj)) adj <- 0
  }
  return(base_mean + adj)
}
# ================ Preferences Setup ================


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
income_adj <- as.integer(income / no_in_household)
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
# ================ Participant Generation ================


# ================ Tone Preference Generation ================
participant_id <- rep(participants$participant_id, each = length(tones))
participant_sex <- rep(participants$sex, each = length(tones))
tone <- rep(tones, times = nrow(participants))

adjusted_means <- mapply(get_adjusted_tone_mean, tone, participant_sex)

tone_rating <- rnorm(length(tone), mean = adjusted_means, sd = standard_deviation)
tone_rating <- pmin(pmax(tone_rating, 1), 7)
tone_rating <- round(tone_rating)
tone_preferences <- data.frame(
  participant_id = participant_id,
  tone = tone,
  tone_rating = tone_rating
)
# tone_preferences <- merge(tone_preferences, participants, by = "participant_id", all.x = TRUE)
write.csv(tone_preferences, file = 'tone/tone_preferences.csv', row.names = FALSE)
# ================ Tone Preference Generation ================


# ================ Style Preference Generation ================
participant_id <- rep(participants$participant_id, each = length(styles))
participant_sex <- rep(participants$sex, each = length(styles))
style <- rep(styles, times = nrow(participants))

adjusted_means <- mapply(get_adjusted_style_mean, style, participant_sex)

style_rating <- rnorm(length(style), mean = adjusted_means, sd = standard_deviation)
style_rating <- pmin(pmax(style_rating, 1), 7)
style_rating <- round(style_rating)
style_preferences <- data.frame(
  participant_id = participant_id,
  style = style,
  style_rating = style_rating
)
# style_preferences <- merge(style_preferences, participants, by = "participant_id", all.x = TRUE)
write.csv(style_preferences, file = 'style/style_preferences.csv', row.names = FALSE)
# ================ Style Preference Generation ================




# # ================ Message Preference Generation for tonesxstylexcontext ================

participant_id <- rep(participants$participant_id, each = length(tones))
participant_sex <- rep(participants$sex, each = length(tones))
tone <- rep(rep(tones, each = length(styles) * length(contexts)), times = nrow(participants))
style <- rep(rep(styles, each = length(contexts)), times = length(tones) * nrow(participants))

adjusted_tone_means <- mapply(get_adjusted_tone_mean, tone, participant_sex)
adjusted_style_means <- mapply(get_adjusted_style_mean, style, participant_sex)

message_rating_tone <- rnorm(length(tone), mean = adjusted_tone_means, sd = standard_deviation)
message_rating_style <- rnorm(length(style), mean = adjusted_style_means, sd = standard_deviation)
message_rating <- (message_rating_tone + message_rating_style) / 2

message_rating <- pmin(pmax(message_rating, 1), 7)
message_rating <- round(message_rating)
message_preferences <- data.frame(
  participant_id = participant_id,
  tone = tone,
  style = style,
  message_rating = message_rating
)
# message_preferences <- merge(message_preferences, participants, by = "participant_id", all.x = TRUE)
write.csv(message_preferences, file = 'messages/message_preferences.csv', row.names = FALSE)
# # ================ Message Preference Generation for tonesxstylexcontext ================


library(dplyr)

combined <- participants |>
  left_join(message_preferences, by = "participant_id") |>
  left_join(style_preferences, by = c("participant_id", "style")) |>
  left_join(tone_preferences, by = c("participant_id", "tone"))
write.csv(participants, file = 'participants.csv', row.names = FALSE)







# Analysis

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
write.csv(data_summary, file = 'tone/tone_summary.csv', row.names = FALSE)

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

write.csv(mean_diff_sex, file = 'tone/tone_mean_diff_sex.csv', row.names = FALSE)
# ================ Tone Preference Analysis ================


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
write.csv(data_summary, file = 'style/style_summary.csv', row.names = FALSE)

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

write.csv(mean_diff_sex, file = 'style/style_mean_diff_sex.csv', row.names = FALSE)
# ================ Style Preference Analysis ================


# ================ Message Preference Analysis ================
# Summary by tone
data_summary_tone <- message_preferences %>%
  group_by(tone) %>%
  summarise(
    mean_rating = mean(message_rating),
    sd_rating = sd(message_rating),
    n = n()
  ) %>%
  arrange(mean_rating)

write.csv(data_summary_tone, file = 'messages/message_summary_tone.csv', row.names = FALSE)

# Summary by style
data_summary_style <- message_preferences %>%
  group_by(style) %>%
  summarise(
    mean_rating = mean(message_rating),
    sd_rating = sd(message_rating),
    n = n()
  ) %>%
  arrange(mean_rating)

write.csv(data_summary_style, file = 'messages/message_summary_style.csv', row.names = FALSE)

# Summary by tone and sex
data_summary_sex_tone <- message_preferences %>%
  group_by(tone, sex) %>%
  summarise(
    mean_rating = mean(message_rating),
    sd_rating = sd(message_rating),
    n = n(),
    .groups = "drop"
  ) %>%
  arrange(tone, sex)

sex_mean_diff_tone <- data_summary_sex_tone %>%
  select(tone, sex, mean_rating) %>%
  pivot_wider(names_from = sex, values_from = mean_rating) %>%
  mutate(mean_diff = male - female)

write.csv(sex_mean_diff_tone, file = "messages/message_sex_mean_diff_tone.csv", row.names = FALSE)

# Summary by style and sex
data_summary_sex_style <- message_preferences %>%
  group_by(style, sex) %>%
  summarise(
    mean_rating = mean(message_rating),
    sd_rating = sd(message_rating),
    n = n(),
    .groups = "drop"
  ) %>%
  arrange(style, sex)

sex_mean_diff_style <- data_summary_sex_style %>%
  select(style, sex, mean_rating) %>%
  pivot_wider(names_from = sex, values_from = mean_rating) %>%
  mutate(mean_diff = male - female)

write.csv(sex_mean_diff_style, file = "messages/message_sex_mean_diff_style.csv", row.names = FALSE)

# ================ Message Preference Analysis ================

# now check between tone preferences and messages preferences
tone_message_comparison <- merge(tone_preferences, message_preferences, by = c("participant_id", "tone"), suffixes = c("_tone", "_message"))
tone_message_comparison <- tone_message_comparison %>%
  group_by(tone) %>%
  summarise(
    mean_tone_rating = mean(tone_rating),
    mean_message_rating = mean(message_rating),
    sd_tone_rating = sd(tone_rating),
    sd_message_rating = sd(message_rating),
    n = n()
  ) %>%
  arrange(mean_tone_rating)
write.csv(tone_message_comparison, file = 'tone/tone_message_comparison.csv', row.names = FALSE)