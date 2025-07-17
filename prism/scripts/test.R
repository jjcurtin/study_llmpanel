args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
  stop("Two arguments are required: job_start and job_stop")
}

job_start <- as.numeric(args[1])
job_stop <- as.numeric(args[2])

if (is.na(job_start) || is.na(job_stop)) {
  stop("Both arguments must be numeric values")
}

cat("Sample script run with args job_start:", job_start, "and job_stop:", job_stop, "\n")