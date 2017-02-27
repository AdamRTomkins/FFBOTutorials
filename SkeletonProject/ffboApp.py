from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

import time

class AppSession(ApplicationSession):

    start_time = time.time()
    log = Logger()
    server_list = {}


    @inlineCallbacks
    def onJoin(self, details):

        # CALL a remote procedure
        # Ask Processor for the latest connected server lists.
        try:     
            res = yield self.call('ffbo.processor.server_information')
            self.log.info("'server_information' called with result: {result}",
                                     result=res)
            server_list = res
        except ApplicationError as e:
            # ignore errors due to the frontend not yet having
            # registered the procedure we would like to call
            if e.error != 'wamp.error.no_such_procedure':
                raise e


        # SUBSCRIBE to a topic and receive events
        # Recieve updates to the server list
        def on_server_update(msg):
            self.log.info("server update recieved: {msg}", msg=msg)

        yield self.subscribe(on_server_update, 'ffbo.server.update')
        self.log.info("subscribed to topic 'ffbo.server.update'")
    
        # PUBLISH to a topic
        # Altert the world to your presence with a hello message
        yield self.publish('ffbo.ffboApp.hello', 'world')
        self.log.info("published to 'hello' with message 'world'")

        # REGISTER a procedure for remote calling
        # 
        def get_uptime():
            return "--- %s seconds ---" % (time.time() - start_time)

        yield self.register(get_uptime, 'ffbo.ffboApp.get_uptime')
        self.log.info("procedure get_uptime() registered")

