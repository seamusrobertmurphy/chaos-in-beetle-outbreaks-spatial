# GENERATED FILE. Do not edit.
# Written from 01.manuscript/manuscript.qmd by the pipe-purl chunk.
# Edit the chunk in the manuscript and regenerate; edits here are lost.
# Run from the repository root.

# Earth Engine session. rgee wraps the Python earthengine-api through
# reticulate, so the interpreter is pinned explicitly: this machine carries
# ee under both python3 (3.12) and python (3.14) and the project convention
# is 3.12. Credentials already exist under ~/.config/earthengine; what
# ee.Initialize() requires in addition is a registered Cloud project, and
# omitting it produces the misleading error "Not signed up for Earth Engine".
local({
  Sys.setenv(RETICULATE_PYTHON = "/opt/local/bin/python3")
  suppressMessages(library(reticulate))
  ee <- reticulate::import("ee")
  ee$Initialize(project = "murphys-deforisk")
  assign("ee", ee, envir = .GlobalEnv)
  invisible(NULL)
})
