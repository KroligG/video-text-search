import Queue
import base64

from autobahn.twisted.websocket import connectWS
from twisted.internet import ssl, reactor

from sttClient import WSInterfaceFactory, WSInterfaceProtocol, Utils


def recognize(fileBytes, model='en-US_BroadbandModel', contentType='audio/wav', tokenauth=False, cred=["1faaa40f-ad36-412d-8493-9503f6be1283", "TkcaECCb2Lew"]):
    hostname = "stream.watsonplatform.net"
    url = "wss://" + hostname + "/speech-to-text/api/v1/recognize?model=" + model

    headers = {}
    # authentication header
    if tokenauth:
        headers['X-Watson-Authorization-Token'] = Utils.getAuthenticationToken("https://" + hostname, 'speech-to-text', cred[0], cred[1])
    else:
        string = cred[0] + ":" + cred[1]
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

    # successful = 0
    # emptyHypotheses = 0
    # for key, value in (sorted(summary.items())):
    #     if value['status']['code'] == 1000:
    #         print key, ": ", value['status']['code'], " ", value['hypothesis'].encode('utf-8')
    #         successful += 1
    #         if value['hypothesis'][0] == "":
    #             emptyHypotheses += 1
    #     else:
    #         print str(key) + ": ", value['status']['code'], " REASON: ", value['status']['reason']
    # print "successful sessions: ", successful, " (", len(summary) - successful, " errors) (" + str(emptyHypotheses) + " empty hypotheses)"
if __name__ == '__main__':
    s = recognize("0001.wav")
    print s