#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import time

from redis_queue import RedisQueue
from settings import DIR, QUEUE_NAMES, SESSION
import facebook
import twitter


INTERVAL_MIN = 5
INTERVAL_SEC = INTERVAL_MIN * 60


def refine_bill_content(bill):
    # bill_id
    bill_id = bill['bill_id']

    # title
    title = bill['title']
    title = truncate(title, 30)
    title_josa = ullul(title.strip('.')[-1])

    # proposer
    proposer = bill['status_dict']['접수']['의안접수정보'][0]['제안자']
    while isinstance(proposer, list):
        proposer = proposer[0]
    proposer = truncate(proposer, 30)
    proposer_josa = yiga(proposer.strip('.')[-1])

    return {
        'proposer': proposer
        'proposer_josa': proposer_josa
        'title': title
        'title_josa': title_josa
        'bill_id': bill_id
    }


def post_bills_facebook(new_bills):
    if new_bills:
        post_sentences = []
        post_sentences += u'오늘 발의된 %d개의 새 의안 목록입니다.\n' % (len(new_bills))
        for bill_id in new_bills:
            bill = get_bill(bill_id)
            bill_contents = refine_bill_content(bill)
            post_sentences += u'%(title)s (%(proposer)s)'
        post = "\n".join(post_sentences)
        facebook.post(post)


def post_bills_twitter(new_bills):
    if new_bills:
        cnt = len(new_bills)
        twitter.post('지금부터 %d분간 %d분 간격으로 %d개의 새 의안을 트윗할 예정입니다.' % (INTERVAL_MIN * cnt, INTERVAL_MIN, cnt))
    for bill_id in new_bills:
        time.sleep(INTERVAL_SEC)
        bill = get_bill(bill_id)
        post_bill_twitter(bill)
        print '%s posted' % bill['bill_id']


def post_bill_twitter(bill):
    status = u'%(proposer)s%(proposer_josa)s "%(title)s"%(title_josa)s 새로 발의하였습니다. http://pokr.kr/bill/%(bill_id)s' % refine_bill_content(bill)
    twitter.post(status)


def truncate(text, max_len):
    if len(text) > max_len:
        text = text[:max_len] + '...'
    return text


def yiga(char):
    if (ord(char) - 44032) % 28:
        return u'이'
    else:
        return u'가'


def ullul(char):
    if (ord(char) - 44032) % 28:
        return u'을'
    else:
        return u'를'


def get_bill(bill_id):
    with open('%s/%d/%s.json' % (DIR['data'], SESSION, bill_id), 'r') as f:
        bill = json.load(f)
    return bill


def usage():
    print 'number of argument is not 1'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    command = sys.argv[1]
    if command == 'twitter':
        queue = RedisQueue('post_bills_twitter')
        bills = list(queue)
        post_bills_twitter(bills)
    elif command == 'facebook':
        queue = RedisQueue('post_bills_facebook'):
        bills = list(queue)
        post_bills_facebook(bills)
    else:
        raise Exception('Unknown target')
