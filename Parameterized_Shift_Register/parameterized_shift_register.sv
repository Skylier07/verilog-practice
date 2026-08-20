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
            q <= (WIDTH-1)'b0;
        end
        else if(load)
            q <= parallel_in;
        else if(enable) begin
            // q <= q>>1'b1;
            // q[WIDTH-1] <= serial_in;
            q <= {serial_in, q[WIDTH-1:1]}
        end
    end

endmodule

