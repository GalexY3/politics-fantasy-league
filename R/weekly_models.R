# Politics Fantasy Laboratory — statistical analysis TEMPLATE only.
# Requires curated person-week table. Does not download official data.
# Columns: person_id, week, observed_count, eligible_opportunities,
#           role, parliamentary_group, time_as_known (TRUE/FALSE).
# Dependencies: MASS; optional ggplot2.

fit_weekly_baselines <- function(df, cutoff_week) {
  required <- c('person_id','week','observed_count','eligible_opportunities',
                'role','parliamentary_group','time_as_known')
  stopifnot(all(required %in% names(df)))
  stopifnot(all(df$observed_count >= 0, na.rm=TRUE),
            all(df$eligible_opportunities >= 0, na.rm=TRUE))
  train <- df[df$week < cutoff_week & df$time_as_known &
                df$eligible_opportunities > 0, ]
  test <- df[df$week >= cutoff_week & df$time_as_known, ]
  if(nrow(train) < 10L || nrow(test) < 1L) stop('insufficient chronological data')
  # NOTE: role/group can themselves change over time: provide as-of correct values.
  poisson <- glm(observed_count ~ role + parliamentary_group +
                   offset(log(eligible_opportunities)), family=poisson(), data=train)
  negbin <- MASS::glm.nb(observed_count ~ role + parliamentary_group +
                         offset(log(eligible_opportunities)), data=train)
  list(poisson=poisson, negbin=negbin,
       test_rows=nrow(test), caveat='NOT VALIDATED: single temporal split, not causal')
}
