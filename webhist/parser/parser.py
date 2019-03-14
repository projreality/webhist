class Parser:

  parsers = { };

  @staticmethod
  def parse(filename):
    raise NotImplementedError();

  @classmethod
  def register(cls, ext, parser):
    cls.parsers[ext] = parser;
