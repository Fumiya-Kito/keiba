from scraping import scrape_kaisai_date, scrape_race_ids

if __name__ == "__main__":
  from_, to_ = "2023-01", "2023-12"
  date_list = scrape_kaisai_date(from_, to_)
  print(date_list)
  race_id_list = scrape_race_ids(date_list)
  print(race_id_list)