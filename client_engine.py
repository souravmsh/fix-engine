import quickfix as fix
import quickfix44 as fix44
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class ClientApplication(fix.Application):
    def __init__(self):
        super().__init__()
        self.sessionID = None

    def onCreate(self, sessionID):
        self.sessionID = sessionID
        logger.info(f"Session created: {sessionID}")

    def onLogon(self, sessionID):
        logger.info(f"Logon: {sessionID}")
        self.sendNewOrder()

    def onLogout(self, sessionID):
        logger.info(f"Logout: {sessionID}")

    def toAdmin(self, message, sessionID):
        pass

    def fromAdmin(self, message, sessionID):
        pass

    def toApp(self, message, sessionID):
        logger.debug(f"Sending message: {message}")

    def fromApp(self, message, sessionID):
        logger.info(f"Received message: {message}")

    def sendNewOrder(self):
        order = fix44.NewOrderSingle()
        order.getHeader().setField(fix.BeginString(fix.BeginString_FIX44))
        order.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        order.setField(fix.ClOrdID("ORDER_1"))
        order.setField(fix.Symbol("COMPANY_SYMBOL"))
        order.setField(fix.Side(fix.Side_BUY))
        order.setField(fix.OrdType(fix.OrdType_LIMIT))
        order.setField(fix.Price(150.00))
        order.setField(fix.OrderQty(100))
        order.setField(fix.TimeInForce(fix.TimeInForce_DAY))
        order.setField(fix.TransactTime())

        fix.Session.sendToTarget(order, self.sessionID)
        logger.info("Sent NewOrderSingle")

def main():
    settings = fix.SessionSettings("cfg/client.cfg")
    application = ClientApplication()
    storeFactory = fix.FileStoreFactory(settings)
    logFactory = fix.FileLogFactory(settings)
    initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
    
    initiator.start()
    time.sleep(10)  # Run for 10 seconds
    initiator.stop()

if __name__ == '__main__':
    main()