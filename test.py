HEADER      = b'\x02\x01\x00AOSMAP\x00\x01\x02'
END_OF_META = b'\x00METADATAEND\x00'
with open("./fake_header", mode='wb') as fake_map:
    fake_map.write(HEADER)
    fake_map.write(b'hello ima fake metadata')
    fake_map.write(END_OF_META)

