#!/usr/bin/python2.7
# -*- encoding=utf-8 -*-

from base import *

class CandCrawler(SinglePageCrawler):

    _url_list_base = 'http://info.nec.go.kr/electioninfo/electionInfo_report.xhtml'\
            '?electionId=0000000000'\
            '&requestURI=%2Felectioninfo%2F0000000000%2Fcp%2Fcpri03.jsp'\
            '&electionType=4&electionCode=3&cityCode=0&sggCityCode=-1'\
            '&townCode=-1&sggTownCode=0&dateCode=0'

    format_suffix = '&statementId=%s&oldElectionType=%d&electionName=%s'

    args = {
            1: ('CPRI03_%2300', 0, '19950627'),
            2: ('CPRI03_%2300', 0, '19980604'),
            3: ('CPRI03_%2300', 0, '20020613'),
            4: ('CPRI03_%231', 1, '20060531'),
            5: ('CPRI03_%231', 1, '20100602')
            }

    attrs = ['district', 'candno', 'party', 'name', 'sex', 'birth', 'job',
            'education', 'experience']

    @property
    def url_list(self):
        url = self._url_list_base + self.format_suffix % self.args[self.nth]
        return url

    def __init__(self, nth):
        self.nth = nth

Crawler = CandCrawler
