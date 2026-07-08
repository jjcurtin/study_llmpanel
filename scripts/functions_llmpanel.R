
# filter_value is used to screen our respondents based on a valid or threshhold
#value for a variety of variables (timing/attention checks, etc.)
filter_value <- function(data, col, valid = NULL, threshold = NULL, keep_col = FALSE, print = FALSE, num = FALSE) {
  if (num) data <- data |> mutate(!!col := as.numeric(.data[[col]]))
  
  if (!is.null(threshold)) {
    keep <- \(x) is.na(x) | x >= threshold
    drop <- \(x) !is.na(x) & x < threshold
  } else if (is.na(valid)) {
    keep <- \(x) is.na(x)
    drop <- \(x) !is.na(x)
  } else {
    keep <- \(x) x == valid
    drop <- \(x) x != valid
  }
  
  flow <<- flow |> full_join(tibble(
    flow        = col,
    n_remaining = data |> filter(keep(.data[[col]])) |> nrow(),
    n_failed    = data |> filter(drop(.data[[col]])) |> nrow()
  ))
  
  if (print) print(flow, n = 100)
  
  data |>
    filter(keep(.data[[col]])) |>
    (\(d) if (!keep_col) select(d, -all_of(col)) else d)()
}

# extract_field pulls information from a geocode() large list object and binds it to the panel
extract_field <- function(gps_list, i, field) {
  res <- tryCatch(gps_list[[i]]$results[[1]], error = function(e) NULL)
  switch(field,
         formatted_address = if (is.null(res)) NA_character_ else res$formatted_address %||% NA_character_,
         lat               = if (is.null(res)) NA_real_      else res$geometry$location$lat %||% NA_real_,
         lng               = if (is.null(res)) NA_real_      else res$geometry$location$lng %||% NA_real_
  )
}

# build_suspicion_index constructs a single value from a list of numeric and categorical variables of concern
build_suspicion_index <- function(data,
                                  numeric_high = NULL,
                                  numeric_med  = NULL,
                                  numeric_low  = NULL,
                                  flag_high    = NULL,
                                  flag_med     = NULL,
                                  flag_low     = NULL,
                                  numeric_weights = c(high = 3, med = 2, low = 1),
                                  flag_values    = c(high = 3, med = 2, low = 1)) {
  
  score <- rep(0, nrow(data))
  
  # Weighted standardized numeric variables
  for (priority in c("high", "med", "low")) {
    vars <- switch(priority, high = numeric_high, med = numeric_med, low = numeric_low)
    if (!is.null(vars)) {
      score <- score + rowSums(data[vars] * numeric_weights[[priority]], na.rm = TRUE)
    }
  }
  
  # Fixed-value flag variables
  for (priority in c("high", "med", "low")) {
    vars <- switch(priority, high = flag_high, med = flag_med, low = flag_low)
    if (!is.null(vars)) {
      score <- score + rowSums(data[vars] * flag_values[[priority]], na.rm = TRUE)
    }
  }
  
  data |> mutate(suspicion_index = score)
}

# add_grocer_code makes a new column in the panel that codes for a variety of
#failures with grocer address verifcations, using a csv created by manual review.
add_grocer_code <- function(panel, grocer_codes) {
  lookup <- grocer_codes |>
    pivot_longer(everything(), names_to = "grocer_code", values_to = "subid") |>
    drop_na(subid)
  
  dupe_ids <- lookup$subid[duplicated(lookup$subid)]
  if (length(dupe_ids) > 0) warning("Duplicate subids in grocer_codes: ", paste(dupe_ids, collapse = ", "))
  
  panel |>
    select(-any_of("grocer_code")) |>
    left_join(lookup, by = "subid") |>
    mutate(grocer_code = replace_na(grocer_code, "valid"))
}