`timescale 1ns/1ps

module shift_register #(
    parameter WIDTH = 16
    )(
    input logic clk,
    input logic reset,
    input logic enable,
    input logic load,
    input logic serial_in,
    input logic [WIDTH-1:0] parallel_in,
    output logic [WIDTH-1:0] q
);

    always @(posedge clk) begin
        if(reset) begin
            q <= '0;
        end
        else if(load)
            q <= parallel_in;
        else if(enable) begin
            // q <= q>>1'b1;
            // q[WIDTH-1] <= serial_in;
            if(WIDTH>1) 
                q <= {serial_in, q[WIDTH-1:1]};
            else
                q <= serial_in;
        end
    end

endmodule

