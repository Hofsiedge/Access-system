from HammingCode import HammingCodec

"""
1 byte, 11 bits for data and 5 for checking (Hamming code):
    1st bit is for command type (passing 0 or special command 1)
    Remaining ones contain command body

    0...:
        Just the user_id of a passer in 10 bits
    1...:
        10000000000 - the first command, is used for checking connection
        10101010101 - the end of the day command
"""
#TODO: logging to work w/o connection




HMCode = HammingCodec(16)

class BinaryProtocol:

    codes = {1024: 'test',
             1635: 'day_end'
            }

    @staticmethod
    def test_connection():
        return HMCode.get_code(1024)

    @staticmethod
    def end_of_the_day():
        return HMCode.get_code((1 << 10) + 1365)

    @staticmethod
    def passing(user_id):
        assert user_id < 1 << 10
        return HMCode.get_code(user_id)

    @staticmethod
    def decode(message):
        message = HMCode.get_data(message)
        if message // 1024:
            return BinaryProtocol.codes[message]
        else:
            return message % 1024
