# filmweb_scraping

Important files:
- `selenium/` - running selenium scraper
- `a/` - running scrapy scraper

To run scrapy:
```
cd a
rm movies.csv
scrapy crawl -o movies.csv movies
```

Output is saved in `scrapy/movies.csv` file

To run selenium:

Open file selenium/run.py and run. Output is saved in `selenium/movies.csv` file.