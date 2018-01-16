class HammingCodec:
    """
    Class for Hammong code writing and checking
    """

    def __init__(self, length):
        self.MSGLEN = length
        assert self.MSGLEN
        self.control_bits = []
        i = 1
        while i <= self.MSGLEN:
            self.control_bits.append(i)
            i <<= 1 
        self.dependencies = {i: [] for i in self.control_bits}
        for i in range(1, self.MSGLEN + 1):
            if i not in self.control_bits:
                for q in self.get_control_bits_for(i):
                    self.dependencies[q].append(i)
        
    def get_control_bits_for(self, i):
        """
        Returns list of bits bit i is checked by
        """
        bits = bin(i)[-1:1:-1]
        res = []
        for num, bit in enumerate(bits):
            if int(bit):
                res.append(1 << num)
        return res

    def get_code(self, origin):
        """
        Get the Hamming code for the data
        """
        assert origin < 1 <<  (self.MSGLEN - len(self.control_bits))
        origin = bin(origin)[2:]
        origin = '0' * (self.MSGLEN - len(origin) - len(self.control_bits))\
                + origin
        origin = [int(i) for i in origin] # list of origin bits
        origin = [0 for i in range(self.MSGLEN - len(origin) - \
                                   len(self.control_bits))] + origin
        code = [0 for i in range(self.MSGLEN)]
        q = 0
        for i in range(self.MSGLEN):
            if i + 1 not in self.control_bits:
                code[i] = origin[q]
                q += 1
        for i in self.dependencies:
            code[i - 1] = sum([code[q - 1] for q in self.dependencies[i]]) % 2
        return int(''.join(list(map(str, code))), 2)

    def get_data(self, code):
        """
        Get the correct (if errors amount is less than 2) data from code
        """
        code = bin(code)[2:]
        code = '0' * (self.MSGLEN - len(code)) + code
        data = ''.join([code[i] for i in range(self.MSGLEN)\
                        if i + 1 not in self.control_bits])
        right_code = bin(self.get_code(int(data, 2)))[2:]
        right_code = '0' * (self.MSGLEN - len(right_code)) + right_code
        code = list(code)
        errors = []
        for i in self.control_bits:
            if code[i - 1] != right_code[i - 1]:
                errors.append(i)

        if errors:
            wrong_bit = sum(errors)
            code[wrong_bit - 1] = '1' if code[wrong_bit - 1] == '0' else '0' 
        data = [code[i] for i in range(self.MSGLEN) \
                if i + 1 not in self.control_bits]

        return int(''.join(data), 2)
