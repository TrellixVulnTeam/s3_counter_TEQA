#!/usr/bin/python
from os.path import splitext, join
from os import environ, system
import sys 
import time
from boto3 import client
import pandas as pd
from collections import Counter
from datetime import datetime


bucket_input = input('버켓명을 입력하세요(종료를 원하시면 q를 입력): ')

bucket=str(bucket_input).strip()

endpoint_url = 'http://kr.object.ncloudstorage.com'

if bucket == 'q' or bucket=='Q':
    exit()
else:
    root_input = input('파일을 카운트할 폴더명을 입력하세요(종료를 원하시면 q를 입력): ')
    root=str(root_input).strip()
    if root == 'q' or root == 'Q':
        exit()
    else:
        



        print("카운트를 시작합니다......")
        start_time = time.time()

        now=datetime.now()
        date=now.strftime('%Y-%m-%d')

        #endpoint_url=str(sys.argv[1])
        #bucket = str(sys.argv[2])
        #root = str(sys.argv[3])

        sub_prefixes=list()
        folder_name=list()
        count=0
        file_count= list()
        file_names= list()
        file_ext=list()
        cnt = Counter()


        ### setting up client object ###
        client = client(service_name='s3', endpoint_url =endpoint_url)


        ### setting up paginator and response ### 
        paginator = client.get_paginator('list_objects')
        response = client.list_objects(Bucket=bucket, Prefix=root, Delimiter='/')


        ### genearting all subfolders of prefix given by user ###
        for s in response.get('CommonPrefixes'):
            sub_prefixes.append(s.get('Prefix'))

        if len(sub_prefixes)!=0:
            for i in range(len(sub_prefixes)):
                pages= paginator.paginate(Bucket=bucket, Prefix=sub_prefixes[i])
                for page in pages:
                    for obj in page['Contents']:
                        if obj['Key'][-1:] !='/':
                            count+=1
                            file_names.append(obj['Key'])

                for f in file_names:
                    name, ext  = splitext(f)
                    cnt[ext]+=1
            
                folder_name.append(sub_prefixes[i][len(root):])
                file_count.append(count)
                count=0
                file_ext.append(str(cnt)[7:])
                cnt.clear()
                file_names=list()



        df= pd.DataFrame()
        df.insert(0, "Folder_Name", folder_name)
        df.insert(1, "File_Count", file_count)
        df.insert(2, "Count by extension", file_ext)

        file_dest = desktop = join(environ['USERPROFILE'], 'Desktop')
        df.to_csv(join(file_dest,'{}_output_{}.csv'.format(root[:root.find('/')],date)), index=False, encoding="utf-8-sig") 


        print("작업완료. 바탕화면에 [{}_output_{}.csv] 파일이 생성되었습니다.".format(root[:root.find('/')],date))
        system('pause')

        #print('Execution took {} seconds'.format(round(time.time()-start_time,2)))

        #system('pause')
