"""
NationBuilder Blog Importer

Copyright (c) 2017 franciskung.com consulting ltd.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. 
"""

import sys, requests
import lxml.html
import settings, json

from datetime import datetime


def do_scrape():
  scrape_url = settings.SCRAPE_URL

  # loop through index pages
  # (initially the scrape url comes from the settings file. each additional loop comes from detecting pagination)

  while scrape_url:

    # get the page
    result = requests.get(scrape_url)

    if result.status_code != 200:
      raise Exception("scrape url {0} was not valid: {1}".format(scrape_url, result.status_code))

    if settings.DEBUG:
      print u"Scraped {0}".format(scrape_url)

    # parse the page
    index_page = lxml.html.fromstring(result.content)
    
    # go through the page finding links to full-page articles
    for link in index_page.cssselect(settings.SCRAPE_LINK):
    
      if settings.DEBUG:
        print u"   Getting subpage {0}".format(link.get('href'))
      
      # fetch the article's pull page
      result2 = requests.get(link.get('href'))
      
      if result2.status_code != 200:
        raise Exception("fullpage url {0} was not valid: {1}".format(link.get('href'), result2.status_code))

      # parse the page
      article_page = lxml.html.fromstring(result2.content)
      
      article_title = article_page.cssselect(settings.SCRAPE_ARTICLE_TITLE)[0].text_content()
      article_body = lxml.html.tostring(article_page.cssselect(settings.SCRAPE_ARTICLE_BODY)[0])
      article_author = article_page.cssselect(settings.SCRAPE_ARTICLE_AUTHOR)[0].text_content()
      article_date = article_page.cssselect(settings.SCRAPE_ARTICLE_DATE)[0].text_content()
      
      article_date = datetime.strptime(article_date, settings.SCRAPE_DATE_FORMAT)
      
      if settings.DEBUG:
        print u"      {0}".format(article_title)
        
      # insert into nationbuilder
      nb_id = nationbuilder_import(article_title, article_body, article_author, article_date)
      if settings.DEBUG:
        print u"      inserted to NationBuilder ({0})".format(nb_id)
        
    if settings.DEBUG:
      print u""

    pagination = index_page.cssselect(settings.SCRAPE_PAGINATION)
    if len(pagination):
      scrape_url = pagination[0].get('href')
    else:
      scrape_url = None



def nationbuilder_import(article_title, article_body, article_author, article_date):
  
  url = u"https://{0}.nationbuilder.com/api/v1/sites/{1}/pages/blogs/{2}/posts".format(settings.NB_SLUG,
                                                                                       settings.NB_SITE_SLUG,
                                                                                       settings.NB_BLOG_ID)
  url = u"{0}?access_token={1}".format(url, settings.NB_KEY)
  
  
  params = {'blog_post': {'name': article_title,
                          'status': 'published',
                          'content_before_flip': article_body,
                          'published_at': article_date.strftime("%Y-%m-%dT%H:%M:%S"),
                          'tags': [settings.NB_PAGE_TAG,]}}
  
  result = requests.post(url, json.dumps(params),
                         headers={'Content-type': 'application/json', 'Accept': 'application/json'})

  return result.json()['blog_post']['id']


# lil helper to retrieve and print all blogs, to find blog ID's
def nationbuilder_blogs():
  url = u"https://{0}.nationbuilder.com/api/v1/sites/{1}/pages/blogs/".format(settings.NB_SLUG,
                                                                                       settings.NB_SITE_SLUG)
  url = u"{0}?access_token={1}".format(url, settings.NB_KEY)
  result = requests.get(url, headers={'Content-type': 'application/json', 'Accept': 'application/json'})
  print result.json()



if __name__ == '__main__':
  do_scrape()

