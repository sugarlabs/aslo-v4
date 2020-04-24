import ssl
from urllib.request import urlopen

HttpsContext = ssl.create_default_context()

def Download(Url):
    return urlopen(Url, context=HttpsContext).read()
 
