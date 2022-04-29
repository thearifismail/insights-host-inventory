import base64
import json
import sys

"""
  This script is used to generate a base64-encoded apiKey using the same json input for a
  desired identity.  There have been occasions when a considerable amount of time was spent
  to determine why the hosts in DB were not accessible using REST API.  The reason turned
  out was using a different apikey for accessing hosts than the one used for creating hosts.

  To generate an apiKey, run:
  "python create_api_key.py basic"

  To see what `auth_type` options are available, run:
  "python create_api_key"
"""
VALID_AUTH_TYPES = ["basic", "cert", "classic"]

# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cn": "1b36b20f-7fa0-4454-a6d2-008294e06378", "cert_type": "system"},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }

# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }

# with_blank_account_number
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "",
#         "type": "User",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiIiwgInR5cGUiOiAiVXNlciIsICJhdXRoX3R5cGUiOiAiYmFzaWMtYXV0aCIsICJ1c2VyIjogeyJlbWFpbCI6ICJ0dXNlckByZWRoYXQuY29tIiwgImZpcnN0X25hbWUiOiAidGVzdCJ9fX0='

# with invalid_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "invalid",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogImludmFsaWQiLCAiYXV0aF90eXBlIjogImJhc2ljLWF1dGgiLCAidXNlciI6IHsiZW1haWwiOiAidHVzZXJAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1lIjogInRlc3QifX19'

# with_blank_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIiIsICJhdXRoX3R5cGUiOiAiYmFzaWMtYXV0aCIsICJ1c2VyIjogeyJlbWFpbCI6ICJ0dXNlckByZWRoYXQuY29tIiwgImZpcnN0X25hbWUiOiAidGVzdCJ9fX0='

# without_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJhdXRoX3R5cGUiOiAiYmFzaWMtYXV0aCIsICJ1c2VyIjogeyJlbWFpbCI6ICJ0dXNlckByZWRoYXQuY29tIiwgImZpcnN0X25hbWUiOiAidGVzdCJ9fX0='

# with_invalid_auth_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "auth_type": "invalid",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAiYXV0aF90eXBlIjogImludmFsaWQiLCAidXNlciI6IHsiZW1haWwiOiAidHVzZXJAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1lIjogInRlc3QifX19'
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAiYXV0aF90eXBlIjogImludmFsaWQiLCAidXNlciI6IHsiZW1haWwiOiAidHVzZXJAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1lIjogInRlc3QifX19'

# with_blank_auth_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "auth_type": "",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAiYXV0aF90eXBlIjogIiIsICJ1c2VyIjogeyJlbWFpbCI6ICJ0dXNlckByZWRoYXQuY29tIiwgImZpcnN0X25hbWUiOiAidGVzdCJ9fX0='
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAiYXV0aF90eXBlIjogIiIsICJ1c2VyIjogeyJlbWFpbCI6ICJ0dXNlckByZWRoYXQuY29tIiwgImZpcnN0X25hbWUiOiAidGVzdCJ9fX0='

# without_auth_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAidXNlciI6IHsiZW1haWwiOiAidHVzZXJAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1lIjogInRlc3QifX19'

# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlVzZXIiLCAiYXV0aF90eXBlIjogImJhc2ljLWF1dGgiLCAidXNlciI6IHsiZW1haWwiOiAidHVzZXJAcmVkaGF0LmNvbSIsICJmaXJzdF9uYW1lIjogInRlc3QifX19'

# # with_blank_cn
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cn": "", "cert_type": "system"},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY24iOiAiIiwgImNlcnRfdHlwZSI6ICJzeXN0ZW0ifSwgImludGVybmFsIjogeyJvcmdfaWQiOiAiMzM0MDg1MSIsICJhdXRoX3RpbWUiOiA2MzAwfX19'
# without_cn
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cert_type": "system"},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY2VydF90eXBlIjogInN5c3RlbSJ9LCAiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIzMzQwODUxIiwgImF1dGhfdGltZSI6IDYzMDB9fX0='

# with_invalid_cert_type
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cn": "1b36b20f-7fa0-4454-a6d2-008294e06378", "cert_type": "invalid"},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY24iOiAiMWIzNmIyMGYtN2ZhMC00NDU0LWE2ZDItMDA4Mjk0ZTA2Mzc4IiwgImNlcnRfdHlwZSI6ICJpbnZhbGlkIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjMzNDA4NTEiLCAiYXV0aF90aW1lIjogNjMwMH19fQ=='
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY24iOiAiMWIzNmIyMGYtN2ZhMC00NDU0LWE2ZDItMDA4Mjk0ZTA2Mzc4IiwgImNlcnRfdHlwZSI6ICJpbnZhbGlkIn0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjMzNDA4NTEiLCAiYXV0aF90aW1lIjogNjMwMH19fQ=='

# with_blank_cert_type
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cn": "1b36b20f-7fa0-4454-a6d2-008294e06378", "cert_type": ""},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY24iOiAiMWIzNmIyMGYtN2ZhMC00NDU0LWE2ZDItMDA4Mjk0ZTA2Mzc4IiwgImNlcnRfdHlwZSI6ICIifSwgImludGVybmFsIjogeyJvcmdfaWQiOiAiMzM0MDg1MSIsICJhdXRoX3RpbWUiOiA2MzAwfX19'

# without_cert_type
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {"cn": "1b36b20f-7fa0-4454-a6d2-008294e06378"},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHsiY24iOiAiMWIzNmIyMGYtN2ZhMC00NDU0LWE2ZDItMDA4Mjk0ZTA2Mzc4In0sICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjMzNDA4NTEiLCAiYXV0aF90aW1lIjogNjMwMH19fQ=='

# with_blank_system
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "system": {},
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgInN5c3RlbSI6IHt9LCAiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIzMzQwODUxIiwgImF1dGhfdGltZSI6IDYzMDB9fX0='


# # without_system
# SYSTEM_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "System",
#         "auth_type": "cert-auth",
#         "internal": {"org_id": "3340851", "auth_time": 6300},
#     }
# }
# b'eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAidGVzdCIsICJ0eXBlIjogIlN5c3RlbSIsICJhdXRoX3R5cGUiOiAiY2VydC1hdXRoIiwgImludGVybmFsIjogeyJvcmdfaWQiOiAiMzM0MDg1MSIsICJhdXRoX3RpbWUiOiA2MzAwfX19'

# with_invalid_auth_type
# USER_IDENTITY = {
#     "identity": {
#         "account_number": "test",
#         "type": "User",
#         "auth_type": "basic-auth",
#         "user": {"email": "tuser@redhat.com", "first_name": "test"},
#     }
# }

USER_IDENTITY = {
    "identity": {
        "account_number": "test",
        "type": "User",
        "auth_type": "basic-auth",
        "user": {"email": "tuser@redhat.com", "first_name": "test"},
    }
}

# Good System identity
SYSTEM_IDENTITY = {
    "identity": {
        "account_number": "test",
        "type": "System",
        "auth_type": "cert-auth",
        "system": {"cn": "1b36b20f-7fa0-4454-a6d2-008294e06378", "cert_type": "system"},
        "internal": {"org_id": "3340851", "auth_time": 6300},
    }
}

INSIGHTS_CLASSIC_IDENTITY = {
    "identity": {
        "account_number": "test",
        "auth_type": "classic-proxy",
        "internal": {"auth_time": 6300, "org_id": "3340851"},
        "system": {},
        "type": "System",
    }
}


def main(argv):
    if len(argv) < 2:
        print("Provide a valid authentication type")
        print("A valid command is python create_api_key.py basic, cert, or classic")
        exit(1)

    auth_type = argv[1]
    if auth_type not in VALID_AUTH_TYPES:
        print("Provide a valid authentication type")
        print('A valid command is "python create_api_key.py basic, cert, or classic"')
        exit(2)

    if auth_type == "basic":
        data = USER_IDENTITY
    elif auth_type == "cert":
        data = SYSTEM_IDENTITY
    else:  # auth type is classic
        data = INSIGHTS_CLASSIC_IDENTITY

    # turns json dict into s string
    data_dict = json.dumps(data)

    # base64.b64encode() needs bytes-like object NOT a string.
    apiKey = base64.b64encode(data_dict.encode("utf-8"))

    print(f"\nFor auth_type: {auth_type}: the encoded apiKey is:\n")
    print(f"{apiKey}\n")
    print(json.dumps(data, indent=2))


# end of the main

if __name__ == "__main__":
    main(sys.argv)
    print("\nDone!!!\n")
