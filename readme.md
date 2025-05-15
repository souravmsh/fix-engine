# Simple FIX Protocol-Based Trading System

## Overview
This project implements a lightweight trading system using the **FIX 4.4 protocol**. It consists of two core components:
- **Broker Engine** (`broker_engine.py`): A FIX acceptor that processes client orders, maintains an in-memory order book, and sends execution reports.
- **Client Engine** (`client_engine.py`): A FIX initiator that sends new order requests to the broker and logs responses.

The system uses the **QuickFIX Python library** for FIX message handling. Configuration files (`broker.cfg` and `client.cfg`) define session settings for communication.

## Features
- Supports **FIX 4.4** messages: `NewOrderSingle` (D), `ExecutionReport` (8), and `BusinessMessageReject` (j).
- In-memory order book for tracking orders.
- Logging of session events and messages to files and console.
- Simple client that sends a sample order and processes execution reports.
- Configurable via `broker.cfg` and `client.cfg`.

## Prerequisites
- **Python**: 3.6 or higher
- **QuickFIX Python Library**: Install via `pip install quickfix`
- **FIX 4.4 Data Dictionary**: `FIX44.xml` (place in `./data/`)
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: ~100 MB for Python, QuickFIX, virtual environment, and project files

## Project Structure
```
project_root/
├── broker_engine.py    # Broker engine script (FIX acceptor)
├── client_engine.py    # Client engine script (FIX initiator)
├── cfg/
│   ├── broker.cfg      # Broker configuration
│   ├── client.cfg      # Client configuration
├── data/
│   ├── FIX44.xml       # FIX 4.4 data dictionary
├── logs/               # Log files (created at runtime)
├── messages/           # Message store (created at runtime)
├── fix_venv/           # Virtual environment
├── README.md           # This file
```

## Installation

### Step-by-Step Guide
1. **Install Python**:
   - Download Python 3.6+ from [python.org](https://www.python.org/downloads/).
   - Verify:
     ```bash
     python3 --version
     pip3 --version
     ```

2. **Create Virtual Environment**:
   - Navigate to the project root.
   - Create and activate:
     ```bash
     python3 -m venv fix_venv
     ```
     - **Linux/macOS**:
       ```bash
       source fix_venv/bin/activate
       ```
     - **Windows**:
       ```bash
       fix_venv\Scripts\activate
       ```

3. **Install QuickFIX**:
   - In the virtual environment:
     ```bash
     pip3 install quickfix
     ```
   - Verify:
     ```bash
     python3 -c "import quickfix"
     ```

4. **Download FIX 4.4 Data Dictionary**:
   - Obtain `FIX44.xml` from [FIX Protocol](https://www.fixtrading.org/) or QuickFIX repositories.
   - Place in `./data/`.

5. **Set Up Project**:
   - Ensure `broker_engine.py`, `client_engine.py`, `broker.cfg`, and `client.cfg` are in place.
   - Create `logs/` and `messages/` directories:
     ```bash
     mkdir logs messages
     ```

6. **Verify Configuration**:
   - Check `broker.cfg` and `client.cfg`:
     - `SenderCompID`/`TargetCompID`: `BROKER` and `CLIENT`
     - `SocketAcceptPort` (broker) and `SocketConnectPort` (client): `5001`
     - `DataDictionary`: `./data/FIX44.xml`

## Usage

### Running the Broker
1. Activate virtual environment:
   ```bash
   source fix_venv/bin/activate  # Linux/macOS
   fix_venv\Scripts\activate     # Windows
   ```
2. Start broker:
   ```bash
   python3 broker_engine.py
   ```
   - Listens on port `5001`, logs to `./logs/`.
3. Stop: Press `Ctrl+C`.

### Running the Client
1. Ensure broker is running.
2. Activate virtual environment (in a new terminal).
3. Start client:
   ```bash
   python3 client_engine.py
   ```
   - Connects to `127.0.0.1:5001`, sends a sample order:
     - `ClOrdID`: `ORDER_1`
     - `Symbol`: `COMPANY_SYMBOL`
     - `Side`: `BUY`
     - `OrdType`: `LIMIT`
     - `Price`: `150.00`
     - `OrderQty`: `100`
     - `TimeInForce`: `DAY`
   - Stops after 10 seconds.

### Customizing Orders
- Edit `sendNewOrder` in `client_engine.py`:
  ```python
  order.setField(fix.Symbol("GOOGL"))
  order.setField(fix.Price(200.00))
  ```
- Save and rerun client.

### Viewing Logs
- Check `./logs/` for `quickfix.event.log` and `quickfix.message.log`.
- Logs include session events, sent/received messages, and errors.

## Example Interaction
1. Start broker:
   ```bash
   python3 broker_engine.py
   ```
   - Output: `Broker engine started. Press Ctrl+C to stop.`
2. Start client:
   ```bash
   python3 client_engine.py
   ```
   - **Client Logs**:
     ```
     2025-05-15 10:41:00 INFO Session created
     2025-05-15 10:41:01 INFO Logon
     2025-05-15 10:41:01 INFO Sent NewOrderSingle
     2025-05-15 10:41:01 INFO Received ExecutionReport: OrdStatus=New
     2025-05-15 10:41:02 INFO Received ExecutionReport: OrdStatus=Filled
     ```
   - **Broker Logs**:
     ```
     2025-05-15 10:41:00 INFO Session created
     2025-05-15 10:41:01 INFO Logon
     2025-05-15 10:41:01 INFO New order: ClOrdID=ORDER_1, Symbol=COMPANY_SYMBOL
     2025-05-15 10:41:01 INFO Sent ExecutionReport: Status=New
     2025-05-15 10:41:02 INFO Sent ExecutionReport: Status=Filled
     ```

## Configuration Details
- **broker.cfg**:
  - `ConnectionType`: `acceptor`
  - `SocketAcceptPort`: `5001`
  - `SenderCompID`: `BROKER`
  - `TargetCompID`: `CLIENT`
  - `FileLogPath`: `./logs`
  - `FileStorePath`: `./messages`
  - `DataDictionary`: `./data/FIX44.xml`
  - `HeartBtInt`: `30` seconds
- **client.cfg**:
  - `ConnectionType`: `initiator`
  - `SocketConnectHost`: `127.0.0.1`
  - `SocketConnectPort`: `5001`
  - `SenderCompID`: `CLIENT`
  - `TargetCompID`: `BROKER`
  - `FileLogPath`: `./logs`
  - `FileStorePath`: `./messages`
  - `DataDictionary`: `./data/FIX44.xml`
  - `HeartBtInt`: `30` seconds

## Limitations
- **Broker**: In-memory order book, simulated execution, supports only `NewOrderSingle`.
- **Client**: Hardcoded order, 10-second runtime, minimal message processing.
- **General**: Single client session, no security, static configuration.

## Future Enhancements
- Support additional FIX messages (e.g., `OrderCancelRequest`).
- Persistent order book (database).
- Real matching engine.
- Interactive client interface.
- Multi-client support.
- SSL/TLS security.
- Unit tests.

## Troubleshooting
- **Broker Fails to Start**:
  - Check port `5001` (`netstat -an | grep 5001` or `netstat -an | findstr 5001`).
  - Verify `FIX44.xml` in `./data/`.
  - Ensure `logs/` and `messages/` are writable.
- **Client Connection Issues**:
  - Confirm broker is running.
  - Match `SocketConnectHost`/`Port` in `client.cfg`.
  - Check firewall for port `5001`.
- **Missing Fields**: Validate `NewOrderSingle` fields and `FIX44.xml`.
- **Logs**: Review `./logs/` for errors.

## License
For educational use only. Not licensed for commercial purposes. Comply with QuickFIX library’s license terms.