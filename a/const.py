# Define constants and setting for running 
# Authentication and scraper specification

run_params = {
    # Facebook credentials
    'email': 'xxxxxxxxxxxx',
    'pwd': 'xxxxxxxxxxxxxx',
    # If run scraper logged in. 
    # If this is disabled, only 30 movies per user are fetched 
    'try_login': True,
    # Limit pages scrpaed per user.
    # Each page has  30 movies. 
    'limit_pages_per_user': 3,
    'limit_users_to_scrape': 3
}