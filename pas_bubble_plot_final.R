################################################################################
# PAS BUBBLE PLOT
# Define all your data at the top, then run the entire script
################################################################################

library(ggplot2)
library(ggrepel)

# =============================================================================
# YOUR DATA - EDIT THIS SECTION ONLY
# =============================================================================

# 1. PAS SITES (polyadenylation site coordinates)
# Define your PAS names and their genomic coordinates
pas_df <- data.frame(
  pas = c("long", "medium", "short"),
  coord = c(40624962, 40627710, 40628724)
)

# 2. TRANSCRIPT INFO
# tx_id = transcript identifier
# start = 3' end coordinate (use 'start' for minus-strand genes, 'end' for plus-strand)
# PAS assignment happens automatically: each transcript assigned to nearest PAS within pas_window
tx_distances <- data.frame(
  tx_id = c("ENST00000431889.6", "ENST00000646448.1", "ENST00000450046.7",
            "ENST00000618765.5", "ENST00000494549.5", "ENST00000482308.5"),
  start = c(40628980, 40628724, 40627710, 40627652, 40625006, 40624962)
)

# 3. EXPRESSION DATA (wide format: one column per condition)
# tx_id = transcript identifier (must match tx_distances)
# Add one column for each condition with TPM values
tpm_summary <- data.frame(
  tx_id = c("ENST00000431889.6", "ENST00000646448.1", "ENST00000450046.7",
            "ENST00000618765.5", "ENST00000494549.5", "ENST00000482308.5"),
  WT = c(52.98, 14.75, 24.56, 19.87, 29.34, 27.65),
  KD = c(55.12, 16.23, 17.89, 13.45, 11.28, 9.87)
)

# FOR 3+ CONDITIONS: Just add more columns to tpm_summary
# Example with 4 conditions:
# tpm_summary <- data.frame(
#   tx_id = c("TX1", "TX2", ...),
#   Control = c(50, 30, ...),
#   Treatment_1h = c(45, 28, ...),
#   Treatment_6h = c(35, 22, ...),
#   Treatment_24h = c(20, 15, ...)
# )

# 4. SETTINGS
pas_window <- 100                          # Window size around each PAS (bp)
zoom_range <- c(40624500, 40629500)       # Zoom to region (or NULL for full range)
condition_order <- c("WT", "KD")          # Order of conditions top to bottom
                                          # For 3+ conditions: c("Control", "Treatment_1h", "Treatment_6h", "Treatment_24h")
show_labels <- TRUE                       # Show transcript ID labels?
label_condition <- "WT"                   # Which condition to label (usually first one)

# 5. COLORS (one color for each PAS class)
color_palette <- c(
  long = "#2A9D8F",
  medium = "#E76F51",
  short = "#4A90D9",
  unassigned = "grey50"
)

# 6. PLOT TITLES
plot_title <- "SMARCE1 transcript 3' ends relative to PAS sites"
plot_subtitle <- "Bubble size = TPM | Shaded = 100nt window"


# =============================================================================
# PLOTTING CODE - DON'T EDIT BELOW
# =============================================================================

# Auto-assign each transcript to nearest PAS within pas_window
cat("Auto-assigning transcripts to nearest PAS within", pas_window, "bp...\n")

tx_distances$nearest_pas <- "unassigned"
tx_distances$min_dist <- Inf

for (i in 1:nrow(tx_distances)) {
  for (j in 1:nrow(pas_df)) {
    dist <- abs(tx_distances$start[i] - pas_df$coord[j])
    if (dist < tx_distances$min_dist[i]) {
      tx_distances$min_dist[i] <- dist
      if (dist <= pas_window) {
        tx_distances$nearest_pas[i] <- as.character(pas_df$pas[j])
      }
    }
  }
}

cat("Assigned", sum(tx_distances$nearest_pas != "unassigned"), "transcripts\n")
cat("Unassigned:", sum(tx_distances$nearest_pas == "unassigned"), "transcripts\n\n")

# Merge transcript info with expression data
plot_data_merged <- merge(tx_distances, tpm_summary, by = "tx_id")

# Reshape from wide to long format
conditions <- condition_order
n_transcripts <- nrow(plot_data_merged)
n_conditions <- length(conditions)

plot_data_long <- data.frame(
  tx_id = rep(plot_data_merged$tx_id, n_conditions),
  start = rep(plot_data_merged$start, n_conditions),
  nearest_pas = rep(plot_data_merged$nearest_pas, n_conditions),
  condition = rep(conditions, each = n_transcripts),
  TPM = unlist(lapply(conditions, function(cond) plot_data_merged[[cond]]))
)

# Calculate y-position for each condition
plot_data_long$y_pos <- match(plot_data_long$condition, conditions) - 1

# Apply zoom if specified
if (!is.null(zoom_range)) {
  plot_data_long <- plot_data_long[
    plot_data_long$start >= zoom_range[1] & plot_data_long$start <= zoom_range[2],
  ]
}

# Build the plot
p <- ggplot() +
  # Shaded PAS windows
  geom_rect(
    data = pas_df,
    aes(xmin = coord - pas_window, xmax = coord + pas_window,
        ymin = -Inf, ymax = Inf, fill = pas),
    alpha = 0.08
  ) +
  # PAS vertical lines
  geom_vline(
    data = pas_df,
    aes(xintercept = coord, color = pas),
    linetype = "dashed", linewidth = 0.8
  ) +
  # PAS labels at top
  geom_text(
    data = pas_df,
    aes(x = coord, y = max(plot_data_long$y_pos) + 0.6,
        label = pas, color = pas),
    fontface = "bold", size = 3.5, hjust = 0.5
  ) +
  # Expression bubbles
  geom_point(
    data = plot_data_long,
    aes(x = start, y = y_pos, size = TPM, color = nearest_pas),
    alpha = 0.85
  )

# Add transcript labels if requested
if (show_labels) {
  label_data <- plot_data_long[plot_data_long$condition == label_condition, ]
  p <- p + geom_text_repel(
    data = label_data,
    aes(x = start, y = y_pos, label = tx_id, color = nearest_pas),
    size = 2.4,
    nudge_y = 0.25,
    segment.size = 0.25,
    segment.alpha = 0.5,
    segment.color = "grey60",
    box.padding = 0.4,
    point.padding = 0.3,
    max.overlaps = 20,
    show.legend = FALSE
  )
}

# Add scales and theme
p <- p +
  scale_color_manual(values = color_palette, name = "PAS class") +
  scale_fill_manual(values = color_palette) +
  scale_size_continuous(range = c(1, 14), name = "TPM") +
  scale_x_continuous(labels = scales::comma) +
  scale_y_continuous(
    breaks = 0:(n_conditions - 1),
    labels = conditions,
    limits = c(-0.5, n_conditions - 0.5 + 0.7)
  ) +
  labs(
    title = plot_title,
    subtitle = plot_subtitle,
    x = "Genomic coordinate",
    y = NULL
  ) +
  guides(fill = "none") +
  theme_bw(base_size = 12) +
  theme(
    panel.grid.minor = element_blank(),
    axis.ticks.y = element_blank(),
    legend.position = "right"
  )

# Apply zoom limits if specified
if (!is.null(zoom_range)) {
  p <- p + coord_cartesian(xlim = zoom_range)
}

# Display plot
print(p)

# Save plot (uncomment to save)
# ggsave("pas_bubble_plot.pdf", p, width = 10, height = 5)
# ggsave("pas_bubble_plot.png", p, width = 10, height = 5, dpi = 300)


# =============================================================================
# EXAMPLE WITH 4 CONDITIONS (commented out - uncomment to test)
# =============================================================================

# pas_df <- data.frame(
#   pas = c("proximal", "distal"),
#   coord = c(100000, 105000)
# )
# 
# tx_distances <- data.frame(
#   tx_id = c("TX1", "TX2", "TX3", "TX4"),
#   start = c(99950, 100050, 104900, 105100),
#   nearest_pas = c("proximal", "proximal", "distal", "distal")
# )
# 
# tpm_summary <- data.frame(
#   tx_id = c("TX1", "TX2", "TX3", "TX4"),
#   Control = c(50, 30, 40, 35),
#   Treatment_1h = c(48, 32, 38, 30),
#   Treatment_6h = c(42, 35, 30, 22),
#   Treatment_24h = c(35, 40, 20, 15)
# )
# 
# pas_window <- 200
# zoom_range <- NULL
# condition_order <- c("Control", "Treatment_1h", "Treatment_6h", "Treatment_24h")
# show_labels <- TRUE
# label_condition <- "Control"
# 
# color_palette <- c(proximal = "#4A90D9", distal = "#E76F51", unassigned = "grey50")
# 
# plot_title <- "Time-course APA dynamics"
# plot_subtitle <- "Bubble size = TPM"
