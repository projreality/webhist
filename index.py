import maflib;
from os import listdir, mkdir;
from os.path import join;
from tld import get_tld;
from urlparse import urlsplit;
from whoosh.fields import DATETIME, ID, Schema, STORED, TEXT;
from whoosh.index import create_in, EmptyIndexError, open_dir;
from whoosh.qparser import QueryParser;
from whoosh.qparser.dateparse import DateParserPlugin;

class Index:

  def __init__(self, path):
    schema = Schema(id=ID(unique=True, stored=True), url=ID(stored=True), fqdn=ID, dn=ID, date=DATETIME(stored=True, sortable=True), title=TEXT(stored=True), content=TEXT);
    try:
      self.index = open_dir(path);
    except IOError:
      mkdir(path);
      self.index = create_in(path, schema);
    except EmptyIndexError:
      self.index = create_in(path, schema);

    self.writer = None;
    self.searcher = None;
    self.parser = None;
    self.default_field = "content";

  def __del__(self):
    if (self.writer is not None):
      self.writer.cancel();
    if (self.searcher is not None):
      self.searcher.close();
    self.index.close();

  def add(self, filename, update=False):
    if (self.writer is None):
      self.writer = self.index.writer();

    exists = not self.search("id:%s" % ( filename, )).is_empty();
    if (exists and not update):
      return False;

    ext = filename[filename.rfind(".")+1:];
    if (ext == "maff"):
      ( url, fqdn, dn, date, title, content ) = self.parse_maff(filename);
    else:
      print("Unrecognized file type: \"%s\"" % ( filename ));
      return False;

    if (exists):
      self.writer.update_document(id=unicode(filename, "UTF-8"), url=unicode(url, "UTF-8"), fqdn=unicode(fqdn, "UTF-8"), dn=unicode(dn, "UTF-8"), date=date, title=title, content=content);
    else:
      self.writer.add_document(id=unicode(filename, "UTF-8"), url=unicode(url, "UTF-8"), fqdn=unicode(fqdn, "UTF-8"), dn=unicode(dn, "UTF-8"), date=date, title=title, content=content);

    return True;

  def parse_maff(self, filename):
    fd = maflib.MAF(filename);
    url = fd.url;
    fqdn = urlsplit(url).netloc;
    dn = get_tld(url);
    date = fd.date;
    title = fd.title;
    content = fd.read_index();
    fd.close();

    return ( url, fqdn, dn, date, title, content );

  def add_path(self, path, update=False, verbose=False):
    i = 0;
    files = listdir(path);
    files.sort();
    added = [ ];
    skipped = [ ];
    error = [ ];
    for filename in files:
      if (filename[-5:] == ".maff"):
        try:
          fname = join(path, filename);
          res = self.add(fname, update);
          if (res):
            added.append(fname);
            if (verbose):
              print(fname);
          else:
            skipped.append(fname);
            if (verbose):
              print("-%s (already in index)" % ( fname, ));
        except Exception as e:
          error.append(fname);
          if (verbose):
            print("-%s (%s: %s)" % ( fname, e.__class__.__name__, e ));
        i = i + 1;
        if (i % 1000 == 0):
          self.commit();
    self.commit();

    return ( added, skipped, error );

  def commit(self):
    if (self.writer is not None):
      self.writer.commit();
      self.writer = None;
      if (self.searcher is not None):
        self.searcher.close();
        self.searcher = None;

  def cancel(self):
    if (self.writer is not None):
      self.writer.cancel();
      self.writer = None;

  def search(self, query, limit=10, default_field=None):
    if (self.searcher is None):
      self.searcher = self.index.searcher();

    if ((self.parser is None) or ((default_field is not None) and (self.default_field != default_field))):
      if (default_field is not None):
        self.default_field = default_field;
      self.parser = QueryParser(default_field, schema=self.index.schema);
      self.parser.add_plugin(DateParserPlugin(free=True));

    return self.searcher.search(self.parser.parse(unicode(query)), limit=limit);
