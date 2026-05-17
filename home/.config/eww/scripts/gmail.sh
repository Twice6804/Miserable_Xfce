#!/usr/bin/env python3

import imaplib
import os
obj = imaplib.IMAP4_SSL('imap.gmail.com',993)
user = os.environ.get('MISERABLE_GMAIL_USER')
password = os.environ.get('MISERABLE_GMAIL_APP_PASSWORD')
if not user or not password:
    print('!')
    raise SystemExit(0)
obj.login(user, password)
obj.select()

cnt = len(obj.search(None, 'UnSeen')[1][0].split())
if(cnt>9):
	print("+")
else:
	print(cnt)