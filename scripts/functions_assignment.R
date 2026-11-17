# Shared helpers for the held-out tone assignment scripts: methods_candidates.qmd,
# methods_heldout.qmd and prereg_models_glmnet.qmd (and the archived scripts they were
# merged from). This file is the only place these functions are defined.
#
# Source after functions_llmpanel.R, which defines tone_levels and pref_cols.
# Requires tidyverse; prep_style() also needs lme4.
#
# Several functions read objects from the calling script:
#   panel_long: one row per message rating (from format_eda(long = TRUE))
#   ids:        respondent ids in a fixed order (from prep_preferences())
#   P:          respondent x tone matrix of stated preferences, rows in the order of `ids`
#
# Contents
#   1. Data:        prep_preferences(), prep_style()
#   2. Methods:     fixed(), pref_ordered_weights(), own_order(), own_top_three()
#   3. Resampling:  make_folds(), make_respondent_folds()
#   4. Scoring:     evaluate_methods(), method_metrics(), group_test()
#   5. Labels:      rotation_label()

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------

# Stated preferences in the shapes the assignment scripts use. Returns a list:
#   pref_wide:    one row per respondent (subid plus the five preference scores), by subid
#   ids, n:       respondent ids in that order, and how many there are
#   P:            respondent x tone matrix of preference scores (columns = tone_levels)
#   pref_by_tone: long format (subid, tone, pref)
prep_preferences <- function(panel_long) {
  pref_wide <- panel_long |>
    dplyr::distinct(subid, dplyr::across(dplyr::all_of(pref_cols))) |>
    dplyr::arrange(subid)
  stopifnot(!anyDuplicated(pref_wide$subid), !anyNA(pref_wide))

  P <- as.matrix(pref_wide[, pref_cols])
  colnames(P) <- tone_levels

  list(
    pref_wide = pref_wide,
    ids = pref_wide$subid,
    n = nrow(pref_wide),
    P = P,
    pref_by_tone = pref_wide |>
      tidyr::pivot_longer(-subid, names_to = "tone", names_prefix = "pref_",
                          values_to = "pref"))
}

# Ratings for one style setting ("both" pools formal and informal; "informal" uses
# informal messages only). Fits a mixed model that separates stable person-by-tone
# differences from message-level noise. Returns a list:
#   styles:         the setting
#   M:              respondent x tone matrix of mean ratings, rows in the order of `ids`
#   n_per_tone:     messages behind each respondent's tone mean (3 informal, 6 pooled)
#   sd_person_tone: SD of stable person-by-tone differences
#   sd_resid:       residual (message-level) SD, used for the noise-corrected metrics
prep_style <- function(styles) {
  d <- if (styles == "informal") dplyr::filter(panel_long, style == "informal") else panel_long

  wide <- d |>
    dplyr::summarise(rating = mean(rating_num, na.rm = TRUE), .by = c(subid, tone)) |>
    tidyr::pivot_wider(names_from = tone, values_from = rating) |>
    dplyr::arrange(subid)
  stopifnot(identical(wide$subid, ids), !anyNA(wide[, tone_levels]))

  form <- if (styles == "informal") {
    rating_num ~ tone + context + (1 | subid) + (1 | subid:tone)
  } else {
    rating_num ~ tone + context + style + (1 | subid) + (1 | subid:tone)
  }
  m <- lme4::lmer(form, data = dplyr::mutate(d, subid = factor(subid)), REML = TRUE)

  list(
    styles = styles,
    M = as.matrix(wide[, tone_levels]),
    n_per_tone = nrow(d) / (dplyr::n_distinct(d$subid) * length(tone_levels)),
    sd_person_tone = attr(lme4::VarCorr(m)[["subid:tone"]], "stddev")[[1]],
    sd_resid = sigma(m))
}

# ---------------------------------------------------------------------------
# 2. Methods
# ---------------------------------------------------------------------------
# A method is a function(top, rows) that returns a rows x tone matrix of weights (each
# row sums to 1). `top` is the tones ranked by mean rating among training respondents;
# `rows` are row numbers of P and the rating matrices.

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

# Each person's OWN top three tones by stated preference (ties broken by the sample
# ranking), weighted by their preference order. Unlike own_order(), the set of tones is
# personal too, so nothing but tie-breaking comes from the sample.
own_top_three <- function(w_sorted) {
  force(w_sorted)
  function(top, rows) {
    t(vapply(rows, \(i) {
      p_ranked <- P[i, top]                       # in sample-rank order
      tones <- top[order(-p_ranked, seq_along(top))[1:3]]
      w <- purrr::set_names(numeric(length(tone_levels)), tone_levels)
      w[tones] <- pref_ordered_weights(P[i, tones], w_sorted)
      w
    }, numeric(length(tone_levels))))
  }
}

# ---------------------------------------------------------------------------
# 3. Resampling
# ---------------------------------------------------------------------------

# Repeated k-fold over `items` (respondent ids or row numbers). Returns a list with one
# element per fold: list(rep, fold, test), where `test` holds the held-out items.
make_folds <- function(items, v, repeats) {
  purrr::map(seq_len(repeats), \(r) {
    fold_id <- sample(rep(seq_len(v), length.out = length(items)))
    purrr::map(seq_len(v), \(k) list(rep = r, fold = k, test = items[fold_id == k]))
  }) |>
    unlist(recursive = FALSE)
}

# Repeated k-fold over respondent rows 1..n: a list of test-row vectors
make_respondent_folds <- function(n, folds, repeats) {
  purrr::map(make_folds(seq_len(n), folds, repeats), "test")
}

# ---------------------------------------------------------------------------
# 4. Scoring
# ---------------------------------------------------------------------------

# Held-out weights and expected ratings for every respondent under every method.
#   methods: named list of functions(top, rows) returning a rows x tone weight matrix
#   M:       respondent x tone matrix of mean ratings (columns = tone_levels)
#   folds:   from make_respondent_folds(); repeats = number of repeats used there
# Tones are ranked on training respondents only. Returns a list:
#   values:  respondent x method matrix of expected ratings
#   weights: for each method, the respondent x tone weights, averaged over the repeats
#            in which the respondent was held out
#   uniform: each respondent's rating under an even rotation of all five tones
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

# Summary of one method on a set of respondents. "Gain" is the expected rating under
# the method minus the rating under an even rotation. Rating noise is removed from the
# spread of gains using the mixed model's residual SD, assuming true gains are normal.
#   e:          result of evaluate_methods()
#   sd_resid:   residual SD from prep_style(); n_per_tone: messages per tone mean
#   harm:       threshold for "clearly worse off" (points below an even rotation)
#   idx:        rows (respondents) to summarise
# Returns a named vector:
#   mean, gain:    mean expected rating and mean gain
#   sd_gain:       SD of true gains, after removing rating noise
#   pct_worse:     estimated share whose true expected rating is below an even rotation
#   pct_clearly:   the same, for at least `harm` points below
#   pct_worse_raw: share with an observed gain below 0 (not noise-corrected)
method_metrics <- function(e, nm, sd_resid, n_per_tone, harm = 0.25,
                           idx = seq_len(nrow(e$values))) {
  gain <- e$values[idx, nm] - e$uniform[idx]
  W <- e$weights[[nm]][idx, , drop = FALSE]
  noise_var <- sd_resid^2 / n_per_tone * rowSums((W - 1 / ncol(W))^2)
  true_sd <- sqrt(max(var(gain) - mean(noise_var), 0))
  c(mean = mean(e$values[idx, nm]),
    gain = mean(gain),
    sd_gain = true_sd,
    pct_worse = if (true_sd == 0) NA_real_ else pnorm(0, mean(gain), true_sd),
    pct_clearly = if (true_sd == 0) NA_real_ else pnorm(-harm, mean(gain), true_sd),
    pct_worse_raw = mean(gain < 0))
}

# Does a value differ between the levels of a grouping variable? Levels with fewer than
# 30 respondents are left out. Returns one row: the number of levels kept, the gap
# between the best- and worst-served level, their names, and a Welch one-way test p-value.
group_test <- function(y, g) {
  keep <- !is.na(g) & g %in% names(which(table(g) >= 30))
  y <- y[keep]; g <- factor(g[keep])
  means <- tapply(y, g, mean)
  tibble::tibble(levels = nlevels(g), gap = max(means) - min(means),
                 best = names(which.max(means)), worst = names(which.min(means)),
                 p = if (nlevels(g) < 2) NA_real_ else oneway.test(y ~ g)$p.value)
}

# ---------------------------------------------------------------------------
# 5. Labels
# ---------------------------------------------------------------------------

# A short label for a weight vector, e.g. "SE 50 / VA 30 / Leg 20"
rotation_label <- function(w) {
  short <- c(norms = "Norms", acknowledging = "Ack", legitimizing = "Leg",
             self_efficacy = "SE", value_affirmation = "VA")
  keep <- w[w > 0]
  keep <- keep[order(-keep, names(keep))]
  paste(sprintf("%s %s", short[names(keep)], round(100 * keep)), collapse = " / ")
}
