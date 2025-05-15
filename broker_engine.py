import quickfix as fix
import quickfix44 as fix44
import logging
import time
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)03d %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class BrokerApplication(fix.Application):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.order_book = {}  # Simple in-memory order storage

    def onCreate(self, sessionID):
        """Called when a new session is created."""
        self.session_id = sessionID
        logger.info(f"Session created: {sessionID}")

    def onLogon(self, sessionID):
        """Called when a session logs on."""
        logger.info(f"Logon: {sessionID}")

    def onLogout(self, sessionID):
        """Called when a session logs out."""
        logger.info(f"Logout: {sessionID}")

    def toApp(self, message, sessionID):
        """Called before sending a message to the counterparty."""
        logger.debug(f"Sending message: {message}")

    def fromApp(self, message, sessionID):
        """Called when a message is received from the counterparty."""
        logger.debug(f"Received message: {message}")
        self.process_message(message, sessionID)

    def toAdmin(self, message, sessionID):
        """Called before sending an admin message."""
        logger.debug(f"Sending admin message: {message}")

    def fromAdmin(self, message, sessionID):
        """Called when an admin message is received."""
        logger.debug(f"Received admin message: {message}")

    def process_message(self, message, sessionID):
        """Process incoming FIX messages."""
        msg_type = message.getHeader().getField(fix.MsgType())
        
        if msg_type == fix.MsgType_NewOrderSingle:
            self.handle_new_order_single(message, sessionID)

    def handle_new_order_single(self, message, sessionID):
        """Handle NewOrderSingle messages."""
        try:
            cl_ord_id = message.getField(fix.ClOrdID())
            symbol = message.getField(fix.Symbol())
            side = message.getField(fix.Side())
            ord_type = message.getField(fix.OrdType())
            price = float(message.getField(fix.Price())) if message.isSetField(fix.Price()) else None
            order_qty = float(message.getField(fix.OrderQty()))

            # Store order in order book
            self.order_book[cl_ord_id] = {
                'symbol': symbol,
                'side': side,
                'ord_type': ord_type,
                'price': price,
                'order_qty': order_qty,
                'status': 'NEW'
            }

            logger.info(f"New order received: ClOrdID={cl_ord_id}, Symbol={symbol}, Side={side}, Qty={order_qty}, Price={price}")

            # Send Execution Report - New
            self.send_execution_report(
                sessionID,
                cl_ord_id,
                symbol,
                side,
                order_qty,
                price,
                fix.OrdStatus_NEW,
                fix.ExecType_NEW
            )

            # Simulate order execution (in a real system, this would interact with a matching engine)
            time.sleep(1)  # Simulate processing delay
            self.order_book[cl_ord_id]['status'] = 'FILLED'

            # Send Execution Report - Filled
            self.send_execution_report(
                sessionID,
                cl_ord_id,
                symbol,
                side,
                order_qty,
                price,
                fix.OrdStatus_FILLED,
                fix.ExecType_TRADE
            )

        except fix.FieldNotFound as e:
            logger.error(f"Missing field in message: {e}")
            self.send_reject(sessionID, message, str(e))

    def send_execution_report(self, sessionID, cl_ord_id, symbol, side, order_qty, price, ord_status, exec_type):
        """Send an Execution Report message."""
        try:
            message = fix44.ExecutionReport()
            header = message.getHeader()
            header.setField(fix.MsgType(fix.MsgType_ExecutionReport))
            header.setField(fix.SendingTime(datetime.utcnow().strftime('%Y%m%d-%H:%M:%S')))
            
            message.setField(fix.OrderID(cl_ord_id))  # Simplified: using ClOrdID as OrderID
            message.setField(fix.ClOrdID(cl_ord_id))
            message.setField(fix.ExecID(f"{cl_ord_id}-{int(time.time())}"))
            message.setField(fix.OrdStatus(ord_status))
            message.setField(fix.ExecType(exec_type))
            message.setField(fix.Symbol(symbol))
            message.setField(fix.Side(side))
            message.setField(fix.OrderQty(order_qty))
            message.setField(fix.CumQty(order_qty if ord_status == fix.OrdStatus_FILLED else 0))
            message.setField(fix.AvgPx(price if price else 0))
            message.setField(fix.LeavesQty(0 if ord_status == fix.OrdStatus_FILLED else order_qty))
            message.setField(fix.TransactTime(datetime.utcnow().strftime('%Y%m%d-%H:%M:%S')))
            if price:
                message.setField(fix.Price(price))

            fix.Session.sendToTarget(message, sessionID)
            logger.info(f"Sent ExecutionReport: ClOrdID={cl_ord_id}, Status={ord_status}")

        except Exception as e:
            logger.error(f"Error sending execution report: {e}")

    def send_reject(self, sessionID, message, reason):
        """Send a reject message for invalid orders."""
        try:
            reject = fix44.BusinessMessageReject()
            reject.getHeader().setField(fix.MsgType(fix.MsgType_BusinessMessageReject))
            reject.setField(fix.RefMsgType(message.getHeader().getField(fix.MsgType())))
            reject.setField(fix.BusinessRejectReason(fix.BusinessRejectReason_OTHER))
            reject.setField(fix.Text(reason))
            fix.Session.sendToTarget(reject, sessionID)
            logger.info(f"Sent BusinessMessageReject: {reason}")
        except Exception as e:
            logger.error(f"Error sending reject: {e}")

def main():
    try:
        # Create directories for logs and store
        os.makedirs("./logs", exist_ok=True)
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./messages", exist_ok=True)

        # Load FIX configuration
        settings = fix.SessionSettings("cfg/broker.cfg")
        application = BrokerApplication()
        store = fix.FileStoreFactory(settings)
        log = fix.FileLogFactory(settings)
        acceptor = fix.SocketAcceptor(application, store, settings, log)

        # Start the acceptor
        acceptor.start()
        logger.info("Broker engine started. Press Ctrl+C to stop.")

        # Keep the application running
        while True:
            time.sleep(1)

    except (fix.ConfigError, fix.RuntimeError) as e:
        logger.error(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("Shutting down broker engine...")
        acceptor.stop()

if __name__ == '__main__':
    main()
