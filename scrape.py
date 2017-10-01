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

import sys, requests, locale
import lxml.html
import settings, json

from datetime import datetime, timedelta

# Change locale if needed (ie for French-language imports)
if settings.SCRAPE_DATE_LOCALE:
  locale.setlocale(locale.LC_ALL, settings.SCRAPE_DATE_LOCALE)


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
      
      # if the link on the listing was broken, we skip and move on
      # (TODO: setting to make this a fatal error instead?)
      if result2.status_code != 200:
        #raise Exception("fullpage url {0} was not valid: {1}".format(link.get('href'), result2.status_code))
        print "*** Fullpage url {0} was not valid: {1} ... skipping".format(link.get('href'), result2.status_code)
        continue


      # parse the page
      article_page = lxml.html.fromstring(result2.content)
      
      article_title = article_page.cssselect(settings.SCRAPE_ARTICLE_TITLE)[0].text_content()
      article_body = lxml.html.tostring(article_page.cssselect(settings.SCRAPE_ARTICLE_BODY)[0])
      #article_author = article_page.cssselect(settings.SCRAPE_ARTICLE_AUTHOR)[0].text_content()
      article_author = ""
      article_date = article_page.cssselect(settings.SCRAPE_ARTICLE_DATE)[0].text_content()

      # parse the date into a native Python datetime, with some locale-related retrying
      # (ie if a site that's supposed to be in French has some random English articles on it)
      try:
        article_date = datetime.strptime(article_date.strip().encode("iso-8859-1"), settings.SCRAPE_DATE_FORMAT)
      except:
        if settings.SCRAPE_DATE_LOCALE:
          try:
            locale.setlocale(locale.LC_ALL, '')
            article_date = datetime.strptime(article_date.strip().encode("iso-8859-1"), settings.SCRAPE_DATE_FORMAT)
            locale.setlocale(locale.LC_ALL, settings.SCRAPE_DATE_LOCALE)
          except:
            print "*** Can't parse date - skipping!"
            continue
        else:
          print "*** Can't parse date - skipping!"
          continue

      # add a time offset so the date is right
      # (normally it'd import as midnight GMT, which is the day before on ET/PT)      
      article_date = article_date + timedelta(hours=5)
      
      if settings.DEBUG:
        print u"      {0}".format(article_title)
        
      # insert into nationbuilder
      nb_id = nationbuilder_import(article_title, article_body, article_author, article_date)
      if settings.DEBUG:
        print u"      inserted to NationBuilder ({0})".format(nb_id)
        
    if settings.DEBUG:
      print u""

    # grab the next page of results
    pagination = index_page.cssselect(settings.SCRAPE_PAGINATION)
    if len(pagination):
      scrape_url = pagination[0].get('href')
    else:
      scrape_url = None



def nationbuilder_import(article_title, article_body, article_author, article_date):

  # if the source page had no content, we skip and move on
  # (TODO: setting to make this a fatal error instead?)
  if not article_title or not article_body:
    print "*** No article title/body - skipping!"
    return
        

  # set up the URL        
  url = u"https://{0}.nationbuilder.com/api/v1/sites/{1}/pages/blogs/{2}/posts".format(settings.NB_SLUG,
                                                                                       settings.NB_SITE_SLUG,
                                                                                       settings.NB_BLOG_ID)
  url = u"{0}?access_token={1}".format(url, settings.NB_KEY)
  

  # set up params  
  params = {'blog_post': {'name': article_title[0:175],
                          'status': 'published',
                          'content_before_flip': article_body,
                          'published_at': article_date.strftime("%Y-%m-%dT%H:%M:%S"),
                          'tags': [settings.NB_PAGE_TAG,]}}
  
  result = requests.post(url, json.dumps(params),
                         headers={'Content-type': 'application/json', 'Accept': 'application/json'})


  try:
    return result.json()['blog_post']['id']
    
  except:
    # this will still die as a fatal error
    # (TODO: setting to make this a recoverable/skip error instead?)
    # but the catch block prints the entire JSON response, so it's easier to debug
    print result.json()
    return result.json()['blog_post']['id']



# lil helper to retrieve and print all blogs, to find blog ID's
def nationbuilder_blogs():
  url = u"https://{0}.nationbuilder.com/api/v1/sites/{1}/pages/blogs/".format(settings.NB_SLUG,
                                                                                       settings.NB_SITE_SLUG)
  url = u"{0}?access_token={1}".format(url, settings.NB_KEY)
  result = requests.get(url, headers={'Content-type': 'application/json', 'Accept': 'application/json'})
  
  for blog in result.json()['results']:
    print u"{0}: {1}".format(blog['id'], blog['name'])
  #print result.json()



if __name__ == '__main__':
  do_scrape()

