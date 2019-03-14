from dateutil import parser;
from tld import get_tld;
from urlparse import urlsplit;

from parser import Parser;

class HTMLParser:

  @staticmethod
  def parse(filename):
    with open(filename) as fd:
      content = fd.read();

    if (type(content) != unicode):
      content = unicode(content, "UTF-8");

    for line in content.split("\n"):
      if (line[:39] == "    <meta name=\"savepage-url\" content=\""):
        url = line[39:-2];
        fqdn = urlsplit(url).netloc;
        dn = get_tld(url);
      elif (line[:41] == "    <meta name=\"savepage-title\" content=\""):
        title = line[41:-2];
      elif (line[:40] == "    <meta name=\"savepage-date\" content=\""):
        date_str = line[40:-2];
        date_str = date_str[:date_str.find("(")-1];
        date = parser.parse(date_str);

    return ( url, fqdn, dn, date, title, content );

Parser.register("html", HTMLParser);
