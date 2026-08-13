module alu_test;
    logic [7:0]a;
    logic [7:0]b;
    logic [2:0] op;
    logic [7:0] result;
    logic zero;
    logic negative;
    logic carry;
    logic overflow;

    alu test_alu(
        .a(a),
        .b(b),
        .op(op),
        .result(result),
        .zero(zero),
        .negative(negative),
        .carry(carry),
        .overflow(overflow)
    );

    initial begin
        a = 8'd2;
        b = 8'd1;
        op = 3'b000;

        #1;
        
        if(result == 3)
            $display("Passed addition test");
        else
            $display("Failed addition test");

        if(negative ==1)
            $display("Failed negative test");
            
        a = 8'b10000000;
        b = 8'b10000000;
        op = 3'b000;

        #1;
        
        if(result == 0)
            $display("Passed addition test");
        else
            $display("Failed addition test");

        if(carry ==0)
            $display("Failed negative test");
            

        a = 8'b01000001;
        b = 8'b01000001;
        op = 3'b000;

        #1;
        
        if(result == 2)
            $display("Passed addition test");
        else
            $display("Failed addition test");

        if(overflow ==0)
            $display("Failed overflow test");
            


        a = 8'd1;
        b = 8'd2;
        op = 3'b001;

        #1;
                
        if(result == 1)
            $display("Passed subtraction test");
        else
            $display("Failed subtraction test");
        if(negative ==0)
            $display("Failed negative test");        


        
        a = 8'd1;
        b = 8'd1;
        op = 3'b001;

        #1;
                
        if(result == 0)
            $display("Passed subtraction test");
        else
            $display("Failed subtraction test");
        if(zero ==0)
            $display("Failed negative test");        


        a = 8'b00101101;
        b = 8'b00101100;
        op = 3'b010;

        #1;

        if(result==8'b11111110)
            $display("Passed AND test");
        else
            $display("Failed AND test");

        a = 8'b11001101;
        b = 8'b00101100;
        op = 3'b011;

        #1;
        
        if(result==8'b11101101)
            $display("Passed OR test");
        else
            $display("Failed OR test");

        a = 8'b11001101;
        b = 8'b00101100;
        op = 3'b100;

        #1;

        if(result==8'b11100001)
            $display("Passed XOR test");
        else
            $display("Failed XOR test");

        a = 8'b11001101;
        op = 3'b101;        

        #1;

        if(result==8'b10011011)
            $display("Passed left test");
        else
            $display("Failed left test");

        a =8'b10011011;
        op = 3'b101;   

        #1;

        if(result==8'b11001101)
            $display("Passed left test");
        else
            $display("Failed left test");

        
        a = 8'b00101101;
        b = 8'b00101100;
        op = 3'b100;

        #1;

        if(result==8'b00000000)
            $display("Passed comparison test");
        else
            $display("Failed comparison test");

        #1;
    end
endmodule