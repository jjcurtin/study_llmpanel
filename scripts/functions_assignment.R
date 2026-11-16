# Shared helpers for the tone assignment scripts.
#
# These functions expect the following objects to exist in the calling script:
#   tone_levels: character vector of the five tones
#   P:           respondent x tone matrix of stated preferences (columns = tone_levels),
#                rows in the same order as the rating matrices
# Written for final_checks.qmd. candidate_methods.qmd and robustness_analyses.qmd
# still carry their own copies of the earlier versions of these functions.

# Same weights for everyone: `weights` go to the top-ranked tones in order
fixed <- function(weights) {
  force(weights)
  function(top, rows) {
    w <- purrr::set_names(numeric(length(tone_levels)), tone_levels)
    w[top[seq_along(weights)]] <- weights
    matrix(w, nrow = length(rows), ncol = length(w), byrow = TRUE,
           dimnames = list(NULL, tone_levels))
  }
}

# Assign `w_sorted` (largest first) by preference order; tied tones share their weights
pref_ordered_weights <- function(p, w_sorted) {
  w <- numeric(length(p))
  w[order(-p)] <- w_sorted
  ave(w, p)
}

# Sample's top three tones, weighted by the person's own preference order.
#   norms: "none"   no norms rule
#          "tier"   norms replaces the third tone when norms is in the person's highest
#                   preference tier (ties for highest count), unless all five are tied
#          "strict" norms replaces the third tone only when norms is preferred strictly
#                   above every other tone
#   ties:  "share"              tied tones split their weights equally
#          "sample"             tied tones are ordered by the sample ranking
#          "sample_if_all_tied" sample ranking only when all three tones are tied;
#                               partial ties still share
own_order <- function(w_sorted, norms = c("none", "tier", "strict"),
                      ties = c("share", "sample", "sample_if_all_tied")) {
  norms <- match.arg(norms)
  ties <- match.arg(ties)
  force(w_sorted)
  function(top, rows) {
    t(vapply(rows, \(i) {
      tones <- top[1:3]
      p_all <- P[i, ]
      others <- p_all[names(p_all) != "norms"]
      swap <- switch(norms,
        none = FALSE,
        tier = p_all[["norms"]] == max(p_all) && min(p_all) < max(p_all),
        strict = p_all[["norms"]] > max(others))
      if (swap && !("norms" %in% tones)) tones[3] <- "norms"

      p <- p_all[tones]                       # `tones` is in sample-rank order
      by_sample <- function() {
        ws <- numeric(length(p))
        ws[order(-p, seq_along(p))] <- w_sorted
        ws
      }
      w_tones <- switch(ties,
        share = pref_ordered_weights(p, w_sorted),
        sample = by_sample(),
        sample_if_all_tied = if (length(unique(p)) == 1) by_sample() else
          pref_ordered_weights(p, w_sorted))

      w <- purrr::set_names(numeric(length(tone_levels)), tone_levels)
      w[tones] <- w_tones
      w
    }, numeric(length(tone_levels))))
  }
}

# Repeated k-fold over respondents: a list of test-row vectors
make_respondent_folds <- function(n, folds, repeats) {
  purrr::map(seq_len(repeats), \(r) {
    fold_id <- sample(rep(seq_len(folds), length.out = n))
    purrr::map(seq_len(folds), \(k) which(fold_id == k))
  }) |> unlist(recursive = FALSE)
}

# Held-out weights and expected ratings for every respondent under every method.
#   methods: named list of functions(top, rows) returning a rows x tone weight matrix
#   M:       respondent x tone matrix of mean ratings (columns = tone_levels)
#   folds:   from make_respondent_folds(); repeats = number of repeats used there
# Tones are ranked on training respondents only.
evaluate_methods <- function(methods, M, folds, repeats) {
  n <- nrow(M)
  W_bar <- purrr::map(methods, \(f) matrix(0, n, length(tone_levels),
                                           dimnames = list(NULL, tone_levels)))
  for (test in folds) {
    train <- setdiff(seq_len(n), test)
    top <- names(sort(colMeans(M[train, , drop = FALSE]), decreasing = TRUE))
    for (nm in names(methods)) {
      W_bar[[nm]][test, ] <- W_bar[[nm]][test, ] + methods[[nm]](top, test) / repeats
    }
  }
  list(values = sapply(W_bar, \(W) rowSums(W * M)),
       weights = W_bar,
       uniform = rowMeans(M))
}

# Mean, gain over an even rotation, and noise-corrected shares worse off, for one method
# on a set of respondents.
#   e:          result of evaluate_methods()
#   sd_resid:   residual SD from the mixed model; n_per_tone: messages per tone mean
#   harm:       threshold for "clearly worse off" (points below an even rotation)
method_metrics <- function(e, nm, sd_resid, n_per_tone, harm = 0.25,
                           idx = seq_len(nrow(e$values))) {
  gain <- e$values[idx, nm] - e$uniform[idx]
  W <- e$weights[[nm]][idx, , drop = FALSE]
  noise_var <- sd_resid^2 / n_per_tone * rowSums((W - 1 / ncol(W))^2)
  true_sd <- sqrt(max(var(gain) - mean(noise_var), 0))
  c(mean = mean(e$values[idx, nm]),
    gain = mean(gain),
    pct_worse = if (true_sd == 0) NA_real_ else pnorm(0, mean(gain), true_sd),
    pct_clearly = if (true_sd == 0) NA_real_ else pnorm(-harm, mean(gain), true_sd),
    pct_worse_raw = mean(gain < 0))
}

# A short label for a weight vector, e.g. "SE 50 / VA 30 / Leg 20"
rotation_label <- function(w) {
  short <- c(norms = "Norms", acknowledging = "Ack", legitimizing = "Leg",
             self_efficacy = "SE", value_affirmation = "VA")
  keep <- w[w > 0]
  keep <- keep[order(-keep, names(keep))]
  paste(sprintf("%s %s", short[names(keep)], round(100 * keep)), collapse = " / ")
}
