import base64

adsense_code = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3058622880826183"></script>'
encoded = base64.b64encode(adsense_code.encode('utf-8')).decode('utf-8')
print(encoded)
