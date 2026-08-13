module alu(
        input [7:0]a,
        input [7:0]b,
        input [2:0]op,
        output logic [7:0]result,
        output logic zero,
        output logic negative,
        output logic carry,
        output logic overflow
    );

    always_comb begin
        result = 8'b0;
        carry = '0;
        case(op)
            3'b000: {carry, result} = a + b;
            3'b001: result = a - b;
            3'b010: result = a & b;
            3'b011: result = a | b;
            3'b100: result = a ^ b;
            3'b101: result = a<<1;
            3'b110: result = a>>1;
            3'b111: result = (a < b) ? 1 : 0;
        endcase

        if(result == 8'b0)
            zero = 1;
        else
            zero = 0;
    
        
        negative = result[7];
        case op
            3'b000: overflow = (~(a[7]^b[7])&(a[7]^result[7]));
            3'b001: overflow = ((a[7]^b[7])&(a[7]^result[7]));
            default: overflow =0;
        endcase
        



    end

endmodule