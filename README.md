# PBFT / CI: Proof-of-Concept

## Usage

> **NOTE**: A working internet connection is required since the pbft nodes have to pull the specified project

Start the pbft network and the client with example configuration:

```bash
    # start the client using example configuration
    ./scripts/startClient.sh
```

```bash
    # start the network using example configuration
    ./startNetwork.sh
```

Trigger a call by posting a request. This process imitates a webhook.
If the example configuration is used, TARGET_BRANCH may be

- master
- feature

If the specified branch does not exist, the network will still work (returning an err code). Assuming the client listens on port 8080:

```bash
curl --header "Content-Type: application/json" --request POST --data '{"branch":"TARGET_BRANCH"}' http://localhost:8080/webHook
```

Stop the network: Client has to be shut down manually.

```bash
    # stop the network
    ./stoptNetwork.sh
```

Inspect the logs in ./log

## Customization

If you want to customize the configuration, the help option might be insightful

```bash
    # change directory to root of the project

    # get more information about client
    python ./client/index.py -h
    # get more information about node
    python ./node/index.py -h
```

The pbft network needs needs 3 f + 1 nodes in order to work properly!
The prototype was tested using 4 nodes (assuming at max one node is faulty)

## Dependencies

- python 3.9.1
- aiohttp 3.7.3
- pycryptodome 3.9.9
- docker (Tested on windows Docker: version 20.10.2, build 2291f61)

You can check your dependencies in a shell:

```bash
    python --version # should print 3.9.1
    docker --version
```

> **NOTE**: On windows, virtualization has to be enabled for docker to work.

The modules can be installed with

```bash
    pip install -r requirements.txt
```

Test if it did work:

```bash
    python -c "import aiohttp; print(aiohttp.__version__)" # should print 3.7.3
    python -c "import Crypto; print(Crypto.__version__)" # should print 3.9.9
```

> **NOTE**: You might want to consider using [virtual environments](https://docs.python.org/3/tutorial/venv.html) if you have already installed the above modules with a different version.

## Literature

You might want to read the following papers to gain more insight on the pbft algortihm

- [The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf) (introduction to bft)
- [Practical Byzantine Fault Tolerance](http://www.pmg.lcs.mit.edu/papers/osdi99.pdf) (about the pbft algorithm)
