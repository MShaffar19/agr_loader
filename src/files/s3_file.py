import logging
logger = logging.getLogger(__name__)

import os
import urllib.request

class S3File(object):

    def __init__(self, filename, savepath):
        self.filename = filename
        self.savepath = savepath

    def download(self):
        if not os.path.exists(os.path.dirname(self.savepath + "/" + self.filename)):
            logger.info("Making temp file storage: %s" % (self.savepath))
            os.makedirs(os.path.dirname(self.savepath + "/" + self.filename))
        url = "https://download.alliancegenome.org/" + self.filename
        if not os.path.exists(self.savepath + "/" + self.filename):
            logger.info("Downloading data from s3 (https://download.alliancegenome.org/%s -> %s/%s) ..." % (self.filename, self.savepath, self.filename))
            urllib.request.urlretrieve(url, self.savepath + "/" + self.filename)
        else:
            logger.info("File: %s/%s already exists, not downloading" % (self.savepath, self.filename))
        return self.savepath + "/" + self.filename

    def download_new(self):
        if not os.path.exists(os.path.dirname(self.savepath + "/" + self.filename)):
            logger.info("Making temp file storage: %s" % (self.savepath))
            try: 
                os.makedirs(os.path.dirname(self.savepath + "/" + self.filename))
            except FileExistsError:
                # Occassionally, two threads can create the directory at almost the exact same time.
                # This allows except should allow this condition to pass without issue.
                pass
        url = "https://download.alliancegenome.org/" + self.filename
        if not os.path.exists(self.savepath + "/" + self.filename):
            logger.info("Downloading data from s3 (https://download.alliancegenome.org/%s -> %s/%s) ..." % (self.filename, self.savepath, self.filename))
            urllib.request.urlretrieve(url, self.savepath + "/" + self.filename)
            return False
        else:
            logger.debug("File: %s/%s already exists, not downloading" % (self.savepath, self.filename))
            return True

    def list_files(self):
        pass
