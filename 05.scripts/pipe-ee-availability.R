# GENERATED FILE. Do not edit.
# Written from 01.manuscript/manuscript.qmd by the pipe-purl chunk.
# Edit the chunk in the manuscript and regenerate; edits here are lost.
# Run from the repository root.

# Scene counts per mission and year over British Columbia, growing season.
# This is metadata about the archive, not an outcome, and it is what
# establishes the coverage the design must work within. It is the evidence
# for the 2012 gap: with Landsat 7 excluded that year has no scenes at all.
local({
  root <- if (file.exists("01.manuscript")) normalizePath(".") else normalizePath("..")
  # A table the manuscript cites, so it belongs in 03.outputs/tables where
  # grab() reads, not in 02.inputs/derived which holds intermediate data.
  out <- file.path(root, "03.outputs", "tables", "landsat-availability.csv")
  if (file.exists(out)) return(invisible(NULL))
  bc <- ee$Geometry$Rectangle(c(-139.1, 48.2, -114.0, 60.0), "EPSG:4326", FALSE)
  cols <- c(`L5 TM` = "LANDSAT/LT05/C02/T1_L2", `L7 ETM+` = "LANDSAT/LE07/C02/T1_L2",
            `L8 OLI` = "LANDSAT/LC08/C02/T1_L2", `L9 OLI-2` = "LANDSAT/LC09/C02/T1_L2")
  rows <- list()
  for (y in 1984:2025) {
    for (nm in names(cols)) {
      n <- tryCatch(
        ee$ImageCollection(cols[[nm]])$filterBounds(bc)$
          filterDate(sprintf("%d-06-15", y), sprintf("%d-09-15", y))$size()$getInfo(),
        error = function(e) NA_integer_)
      rows[[length(rows) + 1]] <- data.frame(year = y, mission = nm, scenes = n)
    }
    utils::write.csv(do.call(rbind, rows), out, row.names = FALSE)
  }
})
