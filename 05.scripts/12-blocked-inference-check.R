#!/usr/bin/env Rscript
# HAND-WRITTEN design tooling. Second stage of the resolution analysis. Touches
# no beetle data; its only input is the province boundary.
#
# The first stage showed the distance-regression estimator recovering a planted
# deterministic front to better than one percent on every candidate grid. That
# result is not reassuring on its own, because a deterministic front has no
# residual structure, and the naive standard error treats hundreds of thousands
# of spatially dependent cells as independent observations. This stage measures
# what that costs.
#
#   1. Plants a STOCHASTIC front: a true speed plus a spatially correlated
#      arrival-time anomaly, so residuals are dependent as the real ones will be.
#   2. Compares the naive standard error against a spatial block bootstrap at
#      three block sizes, giving the design effect and the effective sample size.
#   3. Reruns the null case, a simultaneous eruption, under blocked inference,
#      and records how often a wave is falsely declared.
#
# Writes 03.outputs/tables/blocked-inference.csv
#        03.outputs/tables/blocked-null-case.csv

suppressPackageStartupMessages({ library(terra) })
set.seed(20260818)

ROOT <- if (dir.exists("02.inputs")) "." else ".."
REGIONS <- file.path(ROOT, "02.inputs", "derived", "bc-nr-regions.geojson")
OUTDIR  <- file.path(ROOT, "03.outputs", "tables")
dir.create(OUTDIR, recursive = TRUE, showWarnings = FALSE)

N_YEARS <- 65L
GRID_M  <- 5000
BLOCK_KM <- c(50, 100, 200)
REPS    <- 25L
BOOT    <- 200L
OMISSION <- 0.41

v <- terra::vect(REGIONS)
r <- terra::rast(v, resolution = GRID_M)
r <- terra::rasterize(v, r, field = 1)
xy <- as.matrix(terra::as.data.frame(r, xy = TRUE)[, c("x", "y")])
n_cells <- nrow(xy)
origin <- c(unname(quantile(xy[, 1], 0.25)), unname(median(xy[, 2])))
d_km <- sqrt((xy[, 1] - origin[1])^2 + (xy[, 2] - origin[2])^2) / 1000

# Spatially correlated arrival anomaly, built as a coarse random field at a
# stated correlation length and resampled to the cell centroids. Cheap, explicit,
# and its correlation length is a declared parameter rather than an accident.
corr_field <- function(sd_years, corr_km = 60) {
  cr <- terra::rast(v, resolution = corr_km * 1000)
  terra::values(cr) <- rnorm(terra::ncell(cr), 0, sd_years)
  terra::extract(cr, xy)[, 1]
}

jitter_offsets <- function(n) {
  u <- runif(n); d <- numeric(n)
  d[u < 0.61] <- 0
  i <- u >= 0.61 & u < 0.68; d[i] <- runif(sum(i), 0, 50)
  i <- u >= 0.68 & u < 0.79; d[i] <- runif(sum(i), 50, 500)
  i <- u >= 0.79;            d[i] <- 500 + rexp(sum(i), rate = 1 / 1000)
  th <- runif(n, 0, 2 * pi)
  cbind(d * cos(th), d * sin(th))
}

slope_fit <- function(x, y) {
  ok <- is.finite(x) & is.finite(y); n <- sum(ok)
  if (n < 10) return(c(b = NA, se = NA, n = n))
  x <- x[ok]; y <- y[ok]
  mx <- mean(x); my <- mean(y); sxx <- sum((x - mx)^2)
  if (!is.finite(sxx) || sxx <= 0) return(c(b = NA, se = NA, n = n))
  b <- sum((x - mx) * (y - my)) / sxx
  s2 <- sum((y - (my - b * mx + b * x))^2) / (n - 2)
  c(b = b, se = sqrt(s2 / sxx), n = n)
}

block_id <- function(xy, block_km) {
  bx <- floor(xy[, 1] / (block_km * 1000))
  by <- floor(xy[, 2] / (block_km * 1000))
  paste(bx, by, sep = "_")
}

# The block index is built once per call with split(), not rebuilt inside the
# bootstrap loop. Rebuilding it per resample is O(blocks x n) and turns a
# five-minute job into an overnight one.
block_boot_se <- function(d, y, blocks, B) {
  idx_by_block <- split(seq_along(blocks), blocks)
  nb <- length(idx_by_block)
  bs <- numeric(B)
  for (i in seq_len(B)) {
    pick <- sample.int(nb, nb, replace = TRUE)
    idx <- unlist(idx_by_block[pick], use.names = FALSE)
    bs[i] <- slope_fit(d[idx], y[idx])["b"]
  }
  sd(bs, na.rm = TRUE)
}

simulate <- function(true_speed, sd_years, eruption = FALSE) {
  off <- jitter_offsets(n_cells)
  d_obs <- sqrt((xy[, 1] + off[, 1] - origin[1])^2 +
                (xy[, 2] + off[, 2] - origin[2])^2) / 1000
  if (eruption) {
    yr <- sample.int(5, n_cells, replace = TRUE) + round(corr_field(sd_years))
  } else {
    yr <- ceiling(d_km / true_speed + corr_field(sd_years))
  }
  yr[!is.finite(yr) | yr < 1] <- 1
  yr[yr > N_YEARS] <- NA_real_
  yr[runif(n_cells) < OMISSION] <- NA_real_
  list(d = d_obs, y = as.numeric(yr))
}

cat(sprintf("grid %d m, %d cells, max distance %.0f km\n", GRID_M, n_cells, max(d_km)))

rows <- list()
for (v_true in c(5, 10, 20, 50)) {
  for (sd_y in c(2, 5)) {
    for (bk in BLOCK_KM) {
      naive <- numeric(REPS); blocked <- numeric(REPS); est <- numeric(REPS)
      nb <- NA_integer_
      for (i in seq_len(REPS)) {
        s <- simulate(v_true, sd_y)
        f <- slope_fit(s$d, s$y)
        ok <- is.finite(s$d) & is.finite(s$y)
        blocks <- block_id(xy[ok, , drop = FALSE], bk)
        nb <- length(unique(blocks))
        naive[i] <- f["se"]
        est[i] <- if (is.finite(f["b"]) && f["b"] > 0) 1 / f["b"] else NA_real_
        blocked[i] <- block_boot_se(s$d[ok], s$y[ok], blocks, BOOT)
      }
      de <- mean(blocked, na.rm = TRUE) / mean(naive, na.rm = TRUE)
      rows[[length(rows) + 1]] <- data.frame(
        true_speed = v_true, arrival_sd_years = sd_y, block_km = bk,
        n_blocks = nb, n_cells = n_cells,
        speed_mean = mean(est, na.rm = TRUE),
        speed_bias_pct = 100 * (mean(est, na.rm = TRUE) - v_true) / v_true,
        se_naive = mean(naive, na.rm = TRUE),
        se_blocked = mean(blocked, na.rm = TRUE),
        design_effect = de,
        effective_n = n_cells / de^2
      )
      cat(sprintf("  v=%3d sd=%d block=%3d km: blocks=%4d  DE=%6.1f  speed=%.2f\n",
                  v_true, sd_y, bk, nb, de, mean(est, na.rm = TRUE)))
    }
  }
}

cat("\nnull case, simultaneous eruption, blocked inference\n")
nullrows <- list()
for (bk in BLOCK_KM) {
  declared <- 0L; finite_speed <- 0L; speeds <- numeric(0)
  for (i in seq_len(REPS)) {
    s <- simulate(NA, 3, eruption = TRUE)
    ok <- is.finite(s$d) & is.finite(s$y)
    f <- slope_fit(s$d[ok], s$y[ok])
    blocks <- block_id(xy[ok, , drop = FALSE], bk)
    se_b <- block_boot_se(s$d[ok], s$y[ok], blocks, BOOT)
    z <- f["b"] / se_b
    if (is.finite(z) && abs(z) > 1.96 && f["b"] > 0) declared <- declared + 1L
    if (is.finite(f["b"]) && f["b"] > 0) {
      finite_speed <- finite_speed + 1L; speeds <- c(speeds, 1 / f["b"])
    }
  }
  nullrows[[length(nullrows) + 1]] <- data.frame(
    block_km = bk, reps = REPS,
    frac_positive_slope = finite_speed / REPS,
    median_absurd_speed = if (length(speeds)) median(speeds) else NA_real_,
    frac_wave_declared_blocked = declared / REPS
  )
  cat(sprintf("  block=%3d km: positive slope in %.0f%% of reps, wave declared in %.0f%%\n",
              bk, 100 * finite_speed / REPS, 100 * declared / REPS))
}

out <- do.call(rbind, rows); nul <- do.call(rbind, nullrows)
write.csv(out, file.path(OUTDIR, "blocked-inference.csv"), row.names = FALSE)
write.csv(nul, file.path(OUTDIR, "blocked-null-case.csv"), row.names = FALSE)
cat("\nwrote blocked-inference.csv and blocked-null-case.csv\n")
