# 3-way comparison histogram for suspicion index
compare_plot <- function(var,
                         top = NULL,
                         mid = NULL,
                         bot = NULL,
                         top_label = "Rejected    (n = 43)",
                         mid_label = "Total    (n = 499)",
                         bot_label = "Eligible   (n = 456)",
                         bins = 10,
                         display = "none",
                         stat = "median",
                         labels = "right")
{defaults <- c(top = "p_rejected", mid = "p_full", bot = "p_eligible")
for (nm in names(defaults)) {
  if (is.null(get(nm))) {
    if (!exists(defaults[[nm]], envir = globalenv()))
      stop("Default object '", defaults[[nm]],
           "' not found. Either create it or pass a data frame to `", nm, "`.")
    assign(nm, get(defaults[[nm]], envir = globalenv()))
  }
}
panel_labels <- c(top = top_label, mid = mid_label, bot = bot_label)
panels <- list(top = top, mid = mid, bot = bot)
panel_names <- c("top", "mid", "bot"
)
stat_fn <- if (stat == "mean") mean else median
stat_label <- if (stat == "mean") "Mean" else "Median"

combined <- bind_rows(
  lapply(panel_names, \(nm) panels[[nm]] |> mutate(panel = panel_labels[[nm]]))
) |>
  mutate(panel = factor(panel, levels = panel_labels))

x_range <- range(combined[[var]], na.rm = TRUE)
bin_breaks <- seq(x_range[1], x_range[2], length.out = bins + 1)

stats <- bind_rows(
  lapply(panel_names, \(nm) {
    panels[[nm]] |>
      summarise(
        center = stat_fn(.data[[var]], na.rm = TRUE),
        min_val = min(.data[[var]], na.rm = TRUE),
        max_val = max(.data[[var]], na.rm = TRUE),
        panel = nm
      )
  })
) |>
  mutate(
    panel = factor(panel_labels[panel], levels = panel_labels),
    label = case_when(
      display == "min" ~ paste0(stat_label, ": ", round(center, 2), "\nMin: ", round(min_val, 2)),
      display == "max" ~ paste0(stat_label, ": ", round(center, 2), "\nMax: ", round(max_val, 2)),
      .default = paste0(stat_label, ": ", round(center, 2))
    )
  )

fill_colors <- setNames(c("red3", "darkgoldenrod2", "chartreuse4"), panel_labels)

ggplot(combined, aes(x = .data[[var]], fill = panel)) +
  geom_histogram(breaks = bin_breaks, alpha = 0.7) +
  geom_vline(data = stats, aes(xintercept = center),
             linetype = "dashed", linewidth = 0.8) +
  geom_text(data = stats,
            aes(x = if (labels == "left") -Inf else Inf, y = Inf, label = label),
            vjust = 1.2, hjust = if (labels == "left") -0.05 else 1.05,
            size = 3.5, lineheight = 0.9) +
  stat_bin(breaks = bin_breaks, geom = "text",
           aes(label = after_stat(ifelse(count > 0, count, ""))),
           vjust = -0.3, size = 3) +
  facet_wrap(~panel, ncol = 1, scales = "free_y") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  scale_fill_manual(values = fill_colors) +
  labs(x = var, y = "Count") +
  guides(fill = "none")
}
#-----------------------------------------------------------------------------

# Custom 3-way split for suspicion index
split_panel <- function(data = panel) {
  p_full     <- data |> filter(!is.na(gps_diff)) |> 
    filter(!grepl("_dupe", flag, fixed = TRUE))
  p_eligible <- p_full |> filter(is.na(flag))
  p_rejected <- p_full |>
    filter(!response_id %in% p_eligible$response_id) |>
    filter(!grepl("_dupe", flag, fixed = TRUE))
    
  
  assign("p_full",     p_full,     envir = parent.frame())
  assign("p_eligible", p_eligible, envir = parent.frame())
  assign("p_rejected", p_rejected, envir = parent.frame())
}
#-----------------------------------------------------------------------------

# Proportion summary table for suspicion index
prop_table <- function(var, full = NULL, eligible = NULL, rejected = NULL) {
  defaults <- c(full = "p_full", eligible = "p_eligible", rejected = "p_rejected")
  for (nm in names(defaults)) {
    if (is.null(get(nm))) {
      if (!exists(defaults[[nm]], envir = globalenv()))
        stop("Default object '", defaults[[nm]],
             "' not found. Either create it or pass a data frame to `", nm, "`.")
      assign(nm, get(defaults[[nm]], envir = globalenv()))
    }
  }

  bind_rows(
    rejected |> mutate(group = paste0("Rejected n=", nrow(rejected))),
    full     |> mutate(group = paste0("Full n=",     nrow(full))),
    eligible |> mutate(group = paste0("Eligible n=", nrow(eligible)))
  ) |>
    summarise(
      n_true = sum(.data[[var]], na.rm = TRUE),
      prop   = mean(.data[[var]], na.rm = TRUE),
      .by = group
    )
}
#----------------------------------------------------------------------------