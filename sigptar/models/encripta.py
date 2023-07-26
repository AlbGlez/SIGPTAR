
from werkzeug.security import check_password_hash,generate_password_hash
import sys

if __name__=='__main__':
    args = sys.argv[1:]
    for str in args:
        hstr=generate_password_hash(str)
        print(hstr," [",(len(hstr)),"]")
        
