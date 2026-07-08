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
  
  score
}