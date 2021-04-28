# iperf3tocsv

 - set iperf3 server to ouput in json (`-J`)
 - parse the json for each test
 - sum usage per IP
 - output a log line
 
usage:

    iperf3 -s -J | iperf3tocsv.py

or 

    iperf3tocsv.py /path/to/jsonfile.json

usage:

    iperf3tocsv.py [--help] [-h] [-d] [-v] [jsonfile]

    positional arguments:
      jsonfile       Specify json file to parse (default: STDIN)

    optional arguments:
      --help         Show this help message and exit
      -h, --headers  Include column headers
      -d, --debug    Debug messages
      -v, --verbose  Verbose messsages
