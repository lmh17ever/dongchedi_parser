"""Constants for project"""


RESPONSE_TIMEOUT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

SPECIAL_REPLACEMENTS = {
        '图示': '',
        '马力': ' л.с.',
        '版本': 'Версия'
    }
SPECIAL_CHARS_TO_NUMBERS = {
                    '\ue53d': '1',
                    '\ue3f0': '2',
                    '\ue422': '3',
                    '\ue42c': '4',
                    '\ue49c': '5',
                    '\ue42b': '6',
                    '\ue4fe': '7',
                    '\ue548': '8',
                    '\ue4c8': '9',
                    '\ue453': '0',
                    '\ue45f': '', # 万
                    '\ue531': '', # 公
                    '\ue4fc': '' # 里
                }
