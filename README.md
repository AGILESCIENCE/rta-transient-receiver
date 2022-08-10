# rta-transient-receiver

rta-transient-receiver is a COMET plugin for handling VoEvents notices in the context of the AFIS project (AHEAD2020) and AGILE mission.  The plugin writes the notices in a MySQL database and performs several processes for detecting a possible correlation among instruments. Then it sends an email alert to the team for further analysis.

The current list of the supported instruments is:

- AGILE_MCAL
- CHIME
- FERMI_GBM
- FERMI_LAT
- ICECUBE
- INTEGRAL
- KONUS/WIND
- LIGO
- MAXI
- SWIFT

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

