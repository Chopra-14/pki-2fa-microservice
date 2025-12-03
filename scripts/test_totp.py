import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.totp_utils import generate_totp_code, verify_totp_code

hex_seed = "2b3e97f9ebb8bbb8ee34717c727774bb85ea62e7468ce0fe994d0f5624ee0984"



code = generate_totp_code(hex_seed)
print("Generated OTP:", code)

is_valid = verify_totp_code(hex_seed, code)
print("Is valid:", is_valid)
