PROTOCOLS = ['modbus',
             'siemens',
             'iec104',
             'profinet',
             'tcp',
             'mms',
             'goose',
             'udp',
             'icmp',
             'ip',
             'arp',
             'cip',
             'dnp3',
             'hartip',
             'omron_fins',
             'ethernet/ip']


class JobStatus:
    CREATED = 0
    SELECTED_CASE = 1
    TO_FUZZ = 2
    FUZZING = 3
    FUZZ_COMPLETE = 4
    ERROR = 5
    VULN = 6


class JobType:
    FUZZ = 1
    SCAN = 2
