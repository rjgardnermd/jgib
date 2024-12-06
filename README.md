# jgib: Common code for jg's Interactive Brokers services

For learning how to create your own python package, this article is great:
https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56


## Notes to self:
### To update this package:
- update the code
- update release version in setup.py (two spots)
- run the following script with commitMsg and version as params
    ./runToUpdate.sh "commitMsg" "2.0.6"
- then upgrade the package to test the new version: 
    pip install jgib --upgrade







### To test the server and client:
- python -m jgib.websocket.services.websocketServer
- python -m jgib.websocket.services.websocketClient --id 1
