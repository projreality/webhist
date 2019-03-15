from setuptools import find_packages, setup;

fd = open("README");
long_description = fd.read();
fd.close();

setup(name              = "webhist",
      version           = "1.0.0",
      packages          = find_packages(),
      author            = "Samuel Li",
      author_email      = "sli@projreality.com",
      url               = "http://www.projreality.com/webhist",
      description       = "Saved webpage index and search",
      long_description  = long_description,
      license           = "https://www.gnu.org/licenses/lgpl.html",
      install_requires  = [ "bs4", "python-dateutil", "maflib", "tld", "whoosh" ]
     );
