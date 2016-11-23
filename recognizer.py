import Queue
import base64

from autobahn.twisted.websocket import connectWS
from twisted.internet import ssl, reactor

from sttClient import WSInterfaceFactory, WSInterfaceProtocol, Utils
from utils import processify


@processify
def recognize(fileBytes, model='en-US_BroadbandModel', contentType='audio/wav', tokenauth=False, login='', password=''):
    hostname = "stream.watsonplatform.net"
    url = "wss://" + hostname + "/speech-to-text/api/v1/recognize?model=" + model

    headers = {}
    # authentication header
    if tokenauth:
        headers['X-Watson-Authorization-Token'] = Utils.getAuthenticationToken("https://" + hostname, 'speech-to-text', login, password)
    else:
        string = login + ":" + password
        headers["Authorization"] = "Basic " + base64.b64encode(string)

    q = Queue.Queue()
    q.put((0, fileBytes))
    summary = {}
    factory = WSInterfaceFactory(q, summary, contentType, model, url, headers, debug=False)
    factory.protocol = WSInterfaceProtocol

    factory.prepareUtterance()

    if factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None
    connectWS(factory, contextFactory)

    reactor.run()

    return summary[0]
