import struct
import numpy as np

def float_to_hex(f):
  return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def make_u48(words):
  return words[0] + (words[1] << 16) + (words[2] << 32) 

def sub_ts(words):
  return make_u48(words[3:]) - make_u48(words[0:3])

def calculate_cycles(timestamp_buf):
  hex_t0 = int(float_to_hex(timestamp_buf[0]), base=16)
  hex_t1 = int(float_to_hex(timestamp_buf[1]), base=16)
  hex_t2 = int(float_to_hex(timestamp_buf[2]), base=16)

  tsc_tensor_d2h = np.zeros(6).astype(np.uint16)
  tsc_tensor_d2h[0] = hex_t0 & 0x0000ffff
  tsc_tensor_d2h[1] = (hex_t0 >> 16) & 0x0000ffff
  tsc_tensor_d2h[2] = hex_t1 & 0x0000ffff
  tsc_tensor_d2h[3] = (hex_t1 >> 16) & 0x0000ffff
  tsc_tensor_d2h[4] = hex_t2 & 0x0000ffff
  tsc_tensor_d2h[5] = (hex_t2 >> 16) & 0x0000ffff

  return sub_ts(tsc_tensor_d2h)
