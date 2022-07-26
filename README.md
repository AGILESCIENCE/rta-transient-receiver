# rta-transient-receiver

Plugin used to receive VoEvents from different instruments, it supports the GCN Network and chimenet. It is used for AGILE and AFIS project.

## Installation
The dependencies are listed in the file requirement.txt. It is recommended to install them into a venv enviromnent.

Step to install:

```
python3 -m venv /path/to/new/virtual/environment
```

```
pip install -r requirements.txt
pip install .
```

## Run transient-receiver
Comet commands can be found on the official documentation, a typical command is:

```
twistd -n comet -r --local-ivo=ivo://hotwired.org --local-ivo=ivo://it.agile/mcal  --remote=209.208.78.170:8096 --receive-port=28098 --save-event --save-event-directory=/data01/homes/afiss/repos/voevents --receive-event
```

