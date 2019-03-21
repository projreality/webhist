from os import listdir, mkdir;
from os.path import join;
from whoosh.fields import DATETIME, ID, Schema, STORED, TEXT;
from whoosh.index import create_in, EmptyIndexError, open_dir;
from whoosh.qparser import QueryParser;
from whoosh.qparser.dateparse import DateParserPlugin;

from parser.parser import Parser;
from parser.maff_parser import MAFFParser;
from parser.html_parser import HTMLParser;

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
    try:
      parser = Parser.parsers[ext];
      ( url, fqdn, dn, date, title, content ) = parser.parse(filename);
    except KeyError:
      raise Exception("Unrecognized file type: \"%s\"" % ( filename ));

    if (exists):
      self.writer.update_document(id=unicode(filename, "UTF-8"), url=url, fqdn=fqdn, dn=dn, date=date, title=title, content=content);
    else:
      self.writer.add_document(id=unicode(filename, "UTF-8"), url=url, fqdn=fqdn, dn=dn, date=date, title=title, content=content);

    return True;

  def add_path(self, path, update=False, verbose=False):
    i = 0;
    files = listdir(path);
    files.sort();
    added = [ ];
    skipped = [ ];
    error = [ ];
    for filename in files:
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
