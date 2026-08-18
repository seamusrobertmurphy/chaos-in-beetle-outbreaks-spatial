# Generate the root README from the rendered manuscript.
#
# The README carries the title, the abstract, and then every figure and table
# the manuscript contains, in the order the manuscript declares them, and
# nothing else. It is extracted from `01.manuscript/manuscript.html` rather
# than rebuilt from the derived data, so it cannot disagree with the paper:
# whatever the manuscript renders is what the front page shows.
#
# Tables are emitted as GitHub-flavoured pipe tables. GitHub renders the README,
# not Pandoc, and it prints Pandoc grid tables verbatim as a wall of plus signs.
# Figures are referenced as committed PNGs under 03.outputs/figures rather than
# embedded, so the README stays small.
#
# Centring and width, tested against `gh api /markdown` in gfm mode and measured
# against GitHub's live stylesheet, rather than assumed.
#
# GitHub styles README tables with `.markdown-body table{width:max-content;
# max-width:100%;display:block;overflow:auto}`. A `width` attribute on <table>
# is a presentational hint and loses to that author rule, so it does nothing;
# percentage widths on cells fail too, resolving against an indefinite width.
# Oversized PIXEL hints on the header cells work with max-content instead of
# against it: they inflate the table's intrinsic width past any viewport and
# max-width:100% clamps it back to exactly the container. The hints are soft, so
# the table shrinks to fit and never scrolls.
#
# Measured at container widths 600, 800 and 1012 px: a plain pipe table stayed at
# 187.1 px at every width; the same table with <th width="2000"> measured 600,
# 800 and 1012 px exactly, no overflow.
#
# The cost is that a full-width table cannot be a GFM pipe table; it must be raw
# HTML. That is a deliberate departure from the pipe-table rule, taken because
# the alternative is a table sized to its content. Figures use
# <p align="center"> with <img width="100%">; GitHub adds max-width itself.
#
# Usage: Rscript 05.scripts/04-build-readme.R

suppressMessages({
  library(xml2)
  library(rvest)
})

root <- normalizePath(".")
html_path <- file.path(root, "01.manuscript", "manuscript.html")
stopifnot(file.exists(html_path))
doc <- read_html(html_path)

# Quarto separates the float label from its number with a non-breaking space,
# U+00A0, which [[:space:]] does not match. Normalise it first or every
# caption fails a "Figure 1" test and the headings fall back to raw ids.
squash <- function(x) {
  x <- gsub("\u00a0", " ", x, useBytes = FALSE)
  trimws(gsub("[[:space:]]+", " ", x))
}

# Emit a data frame as a GFM pipe table, escaping any pipe in a cell.
gfm <- function(df) {
  cell <- function(v) gsub("|", "\\|", squash(as.character(v)), fixed = TRUE)
  hdr <- paste0("| ", paste(vapply(names(df), cell, ""), collapse = " | "), " |")
  sep <- paste0("|", paste(rep("---", ncol(df)), collapse = "|"), "|")
  rows <- vapply(seq_len(nrow(df)), function(i)
    paste0("| ", paste(vapply(df[i, ], cell, ""), collapse = " | "), " |"), "")
  paste(c(hdr, sep, rows), collapse = "\n")
}

# Emit a data frame as a full-width HTML table. The pixel hint on each header
# cell is what fills the column; see the note at the top of this file. HTML is
# escaped because these cells carry arbitrary caption and data text.
esc <- function(v) {
  x <- squash(as.character(v))
  x <- gsub("&", "&amp;", x, fixed = TRUE)
  x <- gsub("<", "&lt;", x, fixed = TRUE)
  x <- gsub(">", "&gt;", x, fixed = TRUE)
  gsub("\"", "&quot;", x, fixed = TRUE)
}
wide_table <- function(df, hint = 2000) {
  th <- paste0(sprintf("<th width=\"%d\">%s</th>", hint,
                       vapply(names(df), esc, "")), collapse = "")
  tr <- vapply(seq_len(nrow(df)), function(i)
    paste0("<tr>", paste0(sprintf("<td>%s</td>",
                                  vapply(df[i, ], esc, "")), collapse = ""),
           "</tr>"), "")
  paste0("<table width=\"100%\">\n<thead><tr>", th, "</tr></thead>\n<tbody>\n",
         paste(tr, collapse = "\n"), "\n</tbody>\n</table>")
}

title <- squash(html_text(html_element(doc, "h1.title")))
abstract <- squash(html_text(html_element(doc, "section.abstract, div.abstract")))
abstract <- sub("^Abstract\\s*", "", abstract)

# Every float, in document order, so the README follows the paper rather than a
# list maintained by hand that will fall behind it.
floats <- html_elements(doc, "div[id^='tbl-'], div[id^='fig-']")

blocks <- lapply(floats, function(el) {
  id <- xml_attr(el, "id")
  cap <- html_element(el, "figcaption, caption")
  # length() on an xml_node counts child nodes, so a caption holding only text
  # returns zero and a length test silently discards it. Test the class.
  has_cap <- !inherits(cap, "xml_missing")
  cap_txt <- if (has_cap) squash(html_text(cap)) else id
  # Quarto numbers the float inside the caption; keep it as the heading.
  head_txt <- sub("^(Table [0-9]+|Figure [0-9]+)[:.]?\\s*", "", cap_txt)
  num <- regmatches(cap_txt, regexpr("^(Table|Figure) [0-9]+", cap_txt))
  heading <- if (length(num)) num else id

  if (startsWith(id, "fig-")) {
    img <- html_element(el, "img")
    # The rendered document embeds the figure; the README points at the
    # committed file of the same name instead.
    body <- sprintf(
      "<p align=\"center\"><img src=\"03.outputs/figures/%s-1.png\" alt=\"%s\" width=\"100%%\"></p>",
      id, gsub('"', "&quot;", head_txt, fixed = TRUE))
  } else {
    tb <- html_element(el, "table")
    if (inherits(tb, "xml_missing")) return(NULL)
    df <- html_table(tb, header = TRUE)
    df <- as.data.frame(df, check.names = FALSE)
    names(df) <- ifelse(names(df) == "" | is.na(names(df)),
                        paste0("V", seq_along(df)), names(df))
    body <- wide_table(df)
  }
  paste0("## ", heading, "\n\n", head_txt, "\n\n", body, "\n")
})
blocks <- Filter(Negate(is.null), blocks)

out <- c(paste0("# ", title), "", "## Abstract", "", abstract, "",
         unlist(lapply(blocks, function(b) c(b, ""))))
writeLines(out, file.path(root, "README.md"))

cat("wrote README.md\n")
cat("  title:    ", substr(title, 1, 70), "\n")
cat("  abstract: ", nchar(abstract), "characters\n")
cat("  floats:   ", length(blocks), "\n")
