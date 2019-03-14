import maflib;
import os;
import readline;
import tempfile;
import webbrowser;
import zipfile;

import webhist;

class Shell:

  def __init__(self, name, location, histfile="~/.web_history_shell_history"):
    self.index = webhist.Index(name);
    self.location = location;
    self.prompt = "web> ";
    self.histfile = os.path.expanduser(histfile);
    try:
      readline.read_history_file(self.histfile);
    except IOError:
      pass;

    self.pages = [ ];
    self.tempdirs = [ ];

  def __del__(self):
    print(self.tempdirs);

  def run(self):
    while True:
      try:
        cmd = raw_input(self.prompt).split(" ");
      except EOFError:
        print("");
        break;
      readline.write_history_file(self.histfile);
      self.execute(cmd);

  def execute(self, cmd):
    if ((cmd[0] == "s") or (cmd[0] == "search")):
      self.search(" ".join(cmd[1:]));
    elif ((cmd[0] == "o") or (cmd[0] == "open")):
      self.open(int(cmd[1]));
    elif (cmd[0] == ""):
      return;
    else:
      self.err(cmd);

  def err(self, cmd):
    print("Invalid command");

  def search(self, query):
    results = self.index.search(query, default_field="content");
    self.pages = [ ];
    for result in results:
      if (len(result["title"]) > 50):
        title = result["title"][:50] + "...";
      else:
        title = result["title"];
      print("%d: [%s] %s" % ( len(self.pages), result["date"].strftime("%Y-%m-%d %H:%M:%S"), title ));
      self.pages.append(result["id"]);

  def open(self, id):
    path = os.path.join(self.location, self.pages[id]);
    ext = path[path.rfind(".")+1:];
    print(path);
    print(ext);

    if (ext == "html"):
      webbrowser.open(path);
    elif (ext == "maff"):
      tempdir = tempfile.mkdtemp();
      self.tempdirs.append(tempdir);
      fd = zipfile.ZipFile(path);
      fd.extractall(tempdir);
      fd.close();

      subdir = os.listdir(tempdir)[0];
      path = os.path.join(tempdir, subdir, "index.html");
      webbrowser.open(path);
    else:
      print("Error: unrecognized file type for \"%s\"" % ( self.pages[id] ));

if (__name__ == "__main__"):
  shell = Shell("/var/lib/annex/web_history/index", "/var/lib/annex/web_history");
  shell.run();
