import requests
import json

img_url='https://c2cpicdw.qpic.cn/offpic_new/2508488843//801a5255-07dc-4e6e-9f1d-ef1c55f3e525/0?vuin=1564652357&amp'
url=f'https://saucenao.com/search.php?output_type=2&testmode=1&numres=16&url={img_url}'
result=requests.get(url)
content=json.loads(result.content)
print(content.get('header').get('long_remaining'))
