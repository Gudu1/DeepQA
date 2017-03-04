#coding:utf8
import requests
import json
import simplejson
import langid


def translate_zh2en_with_google_cloud_platform(text):
    if text is None:
        raise "text is required."
    data = {"text":text, "action": "en"}
    url = 'http://app.snaplingo.com:8085/translation/translate'
    headers = {"Content-Type": "application/json"}
    if langid.classify(text)[0] == 'zh':
        # call get service with headers and params
        response = requests.post(url,data = json.dumps(data), headers=headers)
        print "code:"+ str(response.status_code) 
        print '*'*20
        print "headers:"+ str(response.headers)
        print '*'*20
        re = simplejson.loads(response.text)
        res = re["text"].encode("utf8")
        return res
    else:
        return text

def main(msg):
    return translate_zh2en_with_google_cloud_platform(msg)

if __name__ == '__main__':
    msg = "我 喜欢 她"
    print main(msg)