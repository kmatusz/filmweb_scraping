# filmweb_scraping

Important files:
- `selenium/` - running selenium scraper
- `a/` - running scrapy scraper

To run scrapy:

1. Add your facebook credentials in file `const.py`
2. Run from cmd:

```
cd a
rm movies.csv
scrapy crawl login

scrapy crawl -o movies.csv movies
```

Output is saved in `scrapy/movies.csv` file

To run selenium:

Open file selenium/run.py and run. Output is saved in `selenium/movies.csv` file.