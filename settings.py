# Print debug statements...
DEBUG = False


# NationBuilder slugs
NB_SLUG = None          # nation slug
NB_SITE_SLUG = None     # site slug (if the nation only has one site, it's the same as the nation slug)

# NationBuilder API key
NB_KEY = None

# NationBuilder blog ID that these articles should be inserted into
# note: this is NOT the page id that the blog is associated with.
# you may need to use scrape.nationbuilder_blogs to find the blog id's, as I haven't found
# a place in the NB UI where this is ever revealed...
NB_BLOG_ID = None

# NationBuilder tag for auto-created pages (in case there's a glitch and you need to bulk-delete them)
NB_PAGE_TAG = None



# URL of index page to scrape from
SCRAPE_URL = None

# Selector to indicate an individual story on the index page
SCRAPE_ARTICLE = None

# Selector to indicate the "read more" link within a story on the index page
SCRAPE_LINK = None

# Selector to indicate the "next page" pagination link
SCRAPE_PAGINATION = None

# Selector to indicate the article details, on a "read more" page
SCRAPE_ARTICLE_TITLE = None
SCRAPE_ARTICLE_BODY = None
SCRAPE_ARTICLE_AUTHOR = None
SCRAPE_ARTICLE_DATE = None

# A strptime string to parse the incoming article dates
SCRAPE_DATE_FORMAT = None


# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass


