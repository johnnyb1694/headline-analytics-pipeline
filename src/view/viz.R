library(ggplot2)

open_connection <- function(
    user,
    password,
    dbname = "publications",
    host = "localhost",
    port = 5432
) {

  conn <- RPostgres::dbConnect( 
      RPostgres::Postgres(),
      dbname = dbname, 
      host = host, 
      port = port, 
      user = user,
      password = password
  )
  
  return(conn)
  
}

get_top_trending <- function(
    conn, 
    sql_template = 'trending_topics.sql', 
    as_at = '2025-01-01', 
    n_trending = 10
) {
  
  sql <- readr::read_file(file = sql_template)
  param_sql <- glue::glue_sql(sql, .con = conn)
  
  res <- RPostgres::dbGetQuery(conn, param_sql)
  
  return(res)
}

construct_viz_theme <- function() {
  
  growth_theme <- theme(plot.background = element_rect(fill = "grey35"),
                        text = element_text(colour = "grey95"),
                        line = element_line(colour = "grey30"),
                        axis.line = element_blank(),
                        axis.ticks = element_blank(),
                        axis.text = element_text(colour = "grey95"),
                        axis.title = element_text(size = 10),
                        plot.title = element_text(face = "bold"),
                        plot.subtitle = element_text(size = 10),
                        panel.grid = element_blank(),
                        panel.grid.major.y = element_line(colour = "grey50"),
                        panel.border = element_blank(),
                        panel.background = element_blank(),
                        strip.background = element_rect(fill = "black"),
                        plot.caption = element_text(colour = "gray70"))
  
  return(growth_theme)
  
}

# Plot

conn <- open_connection(user = Sys.getenv("DB_USER"), password = Sys.getenv("DB_PWD"))

growth_theme <- construct_viz_theme()

# 1: Growing

top_trending_df <- get_top_trending(conn)

top_trending_plot <- top_trending_df |>
  ggplot(mapping = aes(publication_date, relative_frequency, colour = headline_term)) +
  geom_line(alpha = 0.80, show.legend = FALSE, linewidth = 1.2) +
  facet_wrap(~headline_term) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(x = NULL,
       y = "Relative frequency",
       colour = "Term",
       title = "Trending topics as at '2025-01-01' (to 6 months prior)",
       subtitle = "Jimmy Carter amongst other candidates for top trending topic",
       caption = "Source: New York Times API (Archive Search)") +
  scale_colour_brewer(type = 'div', palette = 'Set3') +
  theme_minimal() +
  theme(plot.title = element_text(face="bold"))

ggplot2::ggsave(
  filename="./plots/top_trending_202501.png",
  plot = top_trending_plot,
  dpi = 300
)

# 2: Shrinking

top_shrinking_df <- get_top_trending(conn, sql_template = "shrinking_topics.sql")

top_shrinking_plot <- top_shrinking_df |>
  ggplot(mapping = aes(publication_date, relative_frequency, colour = headline_term)) +
  geom_line(alpha = 0.80, show.legend = FALSE, linewidth = 1.2) +
  facet_wrap(~headline_term) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(x = NULL,
       y = "Relative frequency",
       colour = "Term",
       title = "Shrinking topics as at '2025-01-01' (to 6 months prior)",
       subtitle = "Hurricane 'Helene', Kamala and Rafah are fading from the headlines",
       caption = "Source: New York Times API (Archive Search)") +
  scale_colour_brewer(type = 'div', palette = 'Set3') +
  theme_minimal() +
  theme(plot.title = element_text(face="bold"))

ggplot2::ggsave(
  filename="./plots/top_shrinking_202501.png",
  plot = top_shrinking_plot,
  dpi = 300
)
