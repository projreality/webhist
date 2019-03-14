import maflib;
from tld import get_tld;
from urlparse import urlsplit;

from parser import Parser;

class MAFFParser(Parser):

  @staticmethod
  def parse(filename):
    fd = maflib.MAF(filename);
    url = unicode(fd.url, "UTF-8");
    fqdn = urlsplit(url).netloc;
    dn = get_tld(url);
    date = fd.date;
    title = fd.title;
    content = fd.read_index();
    fd.close();

    return ( url, fqdn, dn, date, title, content );

Parser.register("maff", MAFFParser);
