def model_alu(a, b, op):
    overflow =0
    carry =0
    zero =0
    negative =0


    if op==0b000:
        result = a + b & 0xFF
        if((a+b)>=0b100000000):
            carry = 1
        else:
            carry =0
        if((not ((a >> 7) & 1^(b >> 7) & 1)) & ((a >> 7) & 1^(result >> 7) & 1)):
            overflow =1
        else:
            overflow =0
    elif op == 0b001:
        result = a-b & 0xFF
        if(((a >> 7) & 1^(b >> 7) & 1)& (not ((a >> 7) & 1^(result >> 7) & 1))):
            overflow =1
        else:
            overflow =0
    elif op ==0b010:
        result = a & b
    elif op == 0b011:
        result = a | b
    elif op == 0b100: 
        result = a^b
    elif op == 0b101:
        result = (a << 1) & 0xFF
    elif op == 0b110:
        result = (a >> 1) & 0xFF
    elif op == 0b111:
        result = 1 if a < b else 0
    result_sign = (result >> 7) & 1

    if result == 0:
        zero =1

    if (result >> 7) & 1 == 1:
        negative =1


    return result, zero, negative, carry, overflow