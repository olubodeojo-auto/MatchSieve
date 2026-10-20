# CSV columns supported

Generic fixture columns: `competition`, `season`, `kickoff_utc`, `home_team`, `away_team`, `status`, `home_score`, `away_score`, `source_ref`, `source_url`.

Football-Data.co.uk aliases handled: `Div`, `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, plus any additional columns which are retained as source-field observations. Dates like `dd/mm/yyyy` are accepted. A file without a kickoff/date or both teams is rejected row by row with a visible error.
