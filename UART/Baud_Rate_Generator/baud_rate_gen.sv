module baud_gen #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200
)(
    input logic clk,
    input logic reset,
    output logic tick
);


localparam int CLK_PER_BIT = CLK_FREQ/BAUD_RATE;
localparam int BIT_REQUIRED = $clog2(CLK_PER_BIT);
logic [BIT_REQUIRED-1:0] counter;

always @(posedge clk) begin
    if(reset) begin
        counter <= '0;
        tick <= '0;
    end
    else if(counter == CLK_PER_BIT) begin
        counter <= '0;
        tick <= 1'b1; 
    end
    else begin
        tick <= '0; 
        counter <= counter + 1'b1;
    end
    

end
endmodule