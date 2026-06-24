import zlib
import base64

with open("/Users/Developer/Desktop/Infinix/Infinix/helpers/_inline.py", "r") as f:
    content = f.read()

encoded_part = content.split("exec(zlib.decompress(base64.b64decode(")[1].split("))")[0]
encoded_part = eval(encoded_part)
decoded = zlib.decompress(base64.b64decode(encoded_part)).decode("utf-8")
print(decoded)
