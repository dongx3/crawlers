#!/usr/bin/python2.7
# -*- encoding=utf-8 -*-

from argparse import ArgumentParser
import codecs
import gevent
from gevent import monkey
import json
from types import UnicodeType

from crawlers import Crawler

def print_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, encoding="UTF-8", indent=2)

def print_csv(filename, data):

    def transform(txt):
        if isinstance(txt, int):
            txt = str(txt)
        if isinstance(txt, list):
            txt = '||'.join(txt)
        txt = txt.replace(',', '|')
        if isinstance(txt, UnicodeType):
            txt = txt.encode('utf8')
        return txt

    attrs = ['assembly_no', 'district', 'cand_no', 'party', 'name_kr',
             'name_cn', 'sex', 'birthyear', 'birthmonth', 'birthday',
             'address', 'job', 'education', 'experience', 'recommend_priority',
             'votenum', 'voterate', 'elected']

    with open(filename, 'w') as f:
        f.write(codecs.BOM_UTF8)
        f.write(','.join(attrs))
        f.write('\n')
        for cand in data:
            values = (cand[attr] if attr in cand else '' for attr in attrs)
            values = (transform(value) for value in values)
            f.write(','.join(values))
            f.write('\n')

def crawl(target, _type, nth, printer, filename):
    crawler = Crawler(target, _type, nth)
    cand_list = crawler.crawl()
    printer(filename, cand_list)

def create_parser():
    parser = ArgumentParser()
    parser.add_argument('target', choices=['assembly', 'mayor', 'president'])
    parser.add_argument('type', choices=['candidates', 'elected'])
    parser.add_argument('start', type=float)
    parser.add_argument('end', type=float, nargs='?', default=None)
    parser.add_argument('-t', dest='test', action='store_true')
    return parser

def main(args):
    printer = print_csv if args.test else print_json
    filetype = 'csv' if args.test else 'json'

    if args.end:
        jobs = []
        for n in xrange(args.start, args.end+1):
            filename = '%s-%s-%d.%s' % (args.target, args.type, n, filetype)
            job = gevent.spawn(crawl, target=args.target, _type=args.type, nth=n,\
                    filename=filename, printer=printer)
            jobs.append(job)
        gevent.joinall(jobs)
    else:
        n = args.start
        filename = '%s-%s-%.01f.%s' % (args.target, args.type, n, filetype)
        crawl(target=args.target, _type=args.type, nth=n,\
                    filename=filename, printer=printer)

if __name__ == '__main__':
    monkey.patch_all()
    parser = create_parser()
    args = parser.parse_args()
    main(args)
