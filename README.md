# jgib: Common Code for Interactive Brokers Services

`jgib` is a Python package used to share reusable code between various services in the **ibServices** repository. This package simplifies managing shared functionality for Interactive Brokers (IB) services and includes utilities for working with WebSocket servers, clients, and models.

For an excellent guide on creating and publishing your own Python package, refer to this article:  
[How to Upload Your Python Package to PyPI](https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56)

---

## Notes to Self

### To Update This Package
1. Update the code.
2. Update the release version in `setup.py` (in two places).
3. Run the following script with the commit message and version as parameters:
   ./runToUpdate.sh "commit message" "2.0.6"
4. Upgrade the package to test the new version:
   pip install jgib --upgrade

---

### To Test the WebSocket Models (using pytest)
```bash
python -m pytest tests/
```
---

### To Test the WebSocket Server and Client (NOT using pytest)
```bash
python -m tests.test_websocket
```
---

### To Manually Test the Server and Client
Run the following three scripts simultaneously in separate terminal windows:

1. Start the WebSocket server:
    ```bash
   python -m jgib.websocket.services.websocketServer
   ```

2. Start Client 1:
    ```bash
   python -m jgib.websocket.services.websocketClient --id 1
    ```
3. Start Client 2:
    ```bash
   python -m jgib.websocket.services.websocketClient --id 2
    ```
You should see the clients sending messages to one another through the server.
