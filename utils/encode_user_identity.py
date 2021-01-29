import base64
import json

"""
  Script to generate base64-encoded json and avoid forgetting or not
  thinking about new-line character, which is add by default when using
  "echo "asdfadsaf | base64".  The output to use is the generated in
  b'<generted_string>'.
"""

data = {
    "identity": {
        "account_number": "test",
        "type": "User",
        "auth_type": "basic-auth",
        "user": {"email": "tuser@redhat.com", "first_name": "test"},
    }
}

# turns json dict into s string
data_dict = json.dumps(data)

# base64.b64encode() needs bytes-like object NOT a string.
apiKey = base64.b64encode(data_dict.encode("utf-8"))

print("")
print("The encoded apiKey is:")
print(f"{apiKey}")
print("")
print("")
print("Done!!!")
