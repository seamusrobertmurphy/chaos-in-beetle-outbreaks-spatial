#!/usr/bin/env Rscript
# HAND-WRITTEN design tooling, not generated from the manuscript. Runs before the
# manuscript exists, so it is numbered and documented in 05.scripts/README.md.
#
# Resolution analysis for the analysis design, run BEFORE any estimator is chosen
# and BEFORE any outcome value is read. It touches no beetle data. Its only input
# is the British Columbia natural resource region boundary, which fixes the study
# geometry, and the record structure confirmed by an availability check: 65
# distinct capture years spanning 1959 to 2025.
#
# It answers three questions the design must not assume:
#   1. How many distinct values can a front-speed estimator return, over what
#      range, on this geometry and this record length?
#   2. What true speed would be indistinguishable from no front at all?
#   3. What does survey positional error do to the estimate?
#
# Writes 03.outputs/tables/resolution-analysis.csv and
#        03.outputs/tables/resolution-null-case.csv

suppressPackageStartupMessages({
  library(terra)
  library(sf)
})

set.seed(20260818)

# Run from the repository root, or from 05.scripts; both resolve.
ROOT <- if (dir.exists("02.inputs")) "." else ".."
stopifnot(dir.exists(file.path(ROOT, "02.inputs")))
REGIONS  <- file.path(ROOT, "02.inputs", "derived", "bc-nr-regions.geojson")
OUTDIR   <- file.path(ROOT, "03.outputs", "tables")
dir.create(OUTDIR, recursive = TRUE, showWarnings = FALSE)

# Record structure, confirmed by availability check on 2026-08-18 against the
# sibling repository's extracted layer. Not assumed.
N_YEARS   <- 65L
YEAR_MIN  <- 1959L
YEAR_MAX  <- 2025L

# Survey positional error. Johnson and Ross 2008 report spatial accuracy of 61,
# 68 and 79 percent at tolerances of 0, 50 and 500 m, quoted here from Bright et
# al. 2020 because the primary is unopened. The mixture below is this study's
# model OF those three numbers and is stated as a model, not as a measurement:
# 61 percent displaced not at all, 7 percent uniformly within 50 m, 11 percent
# uniformly within 500 m, and the remaining 21 percent displaced beyond 500 m
# with an exponential tail of mean 1000 m.
jitter_offsets <- function(n) {
  u <- runif(n)
  d <- numeric(n)
  d[u < 0.61] <- 0
  i <- u >= 0.61 & u < 0.68; d[i] <- runif(sum(i), 0, 50)
  i <- u >= 0.68 & u < 0.79; d[i] <- runif(sum(i), 50, 500)
  i <- u >= 0.79;            d[i] <- 500 + rexp(sum(i), rate = 1 / 1000)
  th <- runif(n, 0, 2 * pi)
  cbind(dx = d * cos(th), dy = d * sin(th))
}

grid_centroids <- function(res_m) {
  v <- terra::vect(REGIONS)
  r <- terra::rast(v, resolution = res_m)
  r <- terra::rasterize(v, r, field = 1)
  xy <- terra::as.data.frame(r, xy = TRUE)
  as.matrix(xy[, c("x", "y")])
}

# Distance regression, the estimator of Tobin et al. 2015 as compared by Gilbert
# and Liebhold 2010: regress year of first detection on distance from the located
# origin, and invert the slope. Speed is km per year.
speed_distance_regression <- function(dist_km, first_year) {
  ok <- is.finite(first_year) & is.finite(dist_km)
  n <- sum(ok)
  if (n < 10) return(c(speed = NA_real_, slope = NA_real_, p = NA_real_))
  x <- dist_km[ok]; y <- first_year[ok]
  mx <- mean(x); my <- mean(y)
  sxx <- sum((x - mx)^2)
  if (!is.finite(sxx) || sxx <= 0) return(c(speed = NA_real_, slope = NA_real_, p = NA_real_))
  b <- sum((x - mx) * (y - my)) / sxx
  a <- my - b * mx
  resid <- y - (a + b * x)
  s2 <- sum(resid^2) / (n - 2)
  se <- sqrt(s2 / sxx)
  tstat <- b / se
  p <- 2 * stats::pt(-abs(tstat), df = n - 2)
  c(speed = if (is.finite(b) && b > 0) 1 / b else NA_real_, slope = b, p = p)
}

# Boundary displacement, the second estimator, kept as a cross-check because it
# is the one most exposed to positional error.
speed_boundary_displacement <- function(dist_km, first_year) {
  ok <- is.finite(first_year) & is.finite(dist_km)
  if (sum(ok) < 10) return(NA_real_)
  d <- dist_km[ok]; y <- first_year[ok]
  yrs <- sort(unique(y))
  if (length(yrs) < 3) return(NA_real_)
  q <- vapply(yrs, function(k) stats::quantile(d[y == k], 0.95, names = FALSE), 0)
  mx <- mean(yrs); my <- mean(q)
  sxx <- sum((yrs - mx)^2)
  if (!is.finite(sxx) || sxx <= 0) return(NA_real_)
  b <- sum((yrs - mx) * (q - my)) / sxx
  if (is.finite(b)) b else NA_real_
}

# One planted wave: a radial front leaving the origin in year one at a known
# speed, observed on annual steps, with positional error and omission applied.
simulate_wave <- function(xy, origin, speed_kmyr, omission = 0.41) {
  off <- jitter_offsets(nrow(xy))
  obs <- xy + off
  d_true <- sqrt((xy[, 1] - origin[1])^2 + (xy[, 2] - origin[2])^2) / 1000
  d_obs  <- sqrt((obs[, 1] - origin[1])^2 + (obs[, 2] - origin[2])^2) / 1000
  yr <- ceiling(d_true / speed_kmyr)
  yr[yr < 1] <- 1
  yr[yr > N_YEARS] <- NA_real_
  drop <- runif(nrow(xy)) < omission
  yr[drop] <- NA_real_
  list(dist = d_obs, year = yr)
}

# The null case the estimator must not report as a wave: every cell erupts in the
# same year, with only detection noise spreading first-damage year.
simulate_eruption <- function(xy, origin, spread_years = 5, omission = 0.41) {
  off <- jitter_offsets(nrow(xy))
  obs <- xy + off
  d_obs <- sqrt((obs[, 1] - origin[1])^2 + (obs[, 2] - origin[2])^2) / 1000
  yr <- sample.int(spread_years, nrow(xy), replace = TRUE)
  drop <- runif(nrow(xy)) < omission
  yr[drop] <- NA_real_
  list(dist = d_obs, year = as.numeric(yr))
}

RESOLUTIONS <- c(1000, 2000, 5000, 12000)
SPEEDS      <- c(1, 2, 5, 10, 20, 50, 100)
REPS        <- 60L

cat("Building grids and running the resolution simulation\n")
rows <- list()
null_rows <- list()

for (res_m in RESOLUTIONS) {
  xy <- grid_centroids(res_m)
  n_cells <- nrow(xy)
  # Origin placed in west-central British Columbia, the area Aukema et al. 2006
  # identify, approximated here as the 25th percentile of easting and the median
  # northing of the province. The resolution result is insensitive to this.
  origin <- c(unname(quantile(xy[, 1], 0.25)), unname(median(xy[, 2])))
  dmax <- max(sqrt((xy[, 1] - origin[1])^2 + (xy[, 2] - origin[2])^2)) / 1000

  cat(sprintf("  %d m grid: %d cells, max distance from origin %.0f km\n",
              res_m, n_cells, dmax))

  for (v in SPEEDS) {
    est_dr <- numeric(REPS); est_bd <- numeric(REPS); pvals <- numeric(REPS)
    for (i in seq_len(REPS)) {
      s <- simulate_wave(xy, origin, v)
      dr <- speed_distance_regression(s$dist, s$year)
      est_dr[i] <- dr["speed"]; pvals[i] <- dr["p"]
      est_bd[i] <- speed_boundary_displacement(s$dist, s$year)
    }
    covered <- v * N_YEARS >= dmax
    rows[[length(rows) + 1]] <- data.frame(
      grid_m = res_m, n_cells = n_cells, max_dist_km = round(dmax, 1),
      true_speed = v,
      dr_mean = mean(est_dr, na.rm = TRUE), dr_sd = sd(est_dr, na.rm = TRUE),
      dr_bias_pct = 100 * (mean(est_dr, na.rm = TRUE) - v) / v,
      bd_mean = mean(est_bd, na.rm = TRUE), bd_sd = sd(est_bd, na.rm = TRUE),
      frac_p_lt_05 = mean(pvals < 0.05, na.rm = TRUE),
      province_crossed_within_record = covered
    )
  }

  # Null case at this resolution.
  est_dr <- numeric(REPS); pvals <- numeric(REPS)
  for (i in seq_len(REPS)) {
    s <- simulate_eruption(xy, origin)
    dr <- speed_distance_regression(s$dist, s$year)
    est_dr[i] <- dr["speed"]; pvals[i] <- dr["p"]
  }
  null_rows[[length(null_rows) + 1]] <- data.frame(
    grid_m = res_m, n_cells = n_cells,
    dr_mean_speed = mean(est_dr, na.rm = TRUE),
    frac_finite_speed = mean(is.finite(est_dr)),
    frac_p_lt_05_naive = mean(pvals < 0.05, na.rm = TRUE)
  )
}

res <- do.call(rbind, rows)
nul <- do.call(rbind, null_rows)
write.csv(res, file.path(OUTDIR, "resolution-analysis.csv"), row.names = FALSE)
write.csv(nul, file.path(OUTDIR, "resolution-null-case.csv"), row.names = FALSE)

cat("\n--- Planted wave, distance regression ---\n")
print(res[, c("grid_m", "n_cells", "true_speed", "dr_mean", "dr_sd",
              "dr_bias_pct", "frac_p_lt_05", "province_crossed_within_record")],
      row.names = FALSE, digits = 3)
cat("\n--- Null case, simultaneous eruption ---\n")
print(nul, row.names = FALSE, digits = 3)
cat("\nwrote", file.path(OUTDIR, "resolution-analysis.csv"), "\n")
