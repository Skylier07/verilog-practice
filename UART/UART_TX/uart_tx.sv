`timescale 1ns/1ps

module uart_top #(
    parameter CLK_FREQ = 100,
    parameter BAUD_RATE = 10
)(
    input logic clk,
    input logic reset,
    input logic start,
    input logic [7:0]data_in,
    output logic tx,
    output logic busy
);

logic baud_tick;
baud_gen #(
    .CLK_FREQ(CLK_FREQ),
    .BAUD_RATE(BAUD_RATE)
) baud(
    .clk(clk),
    .reset(reset),
    .tick(baud_tick)
);

uart_tx tx_instance(
    .clk(clk),
    .reset(reset),
    .baud_tick(baud_tick),
    .start(start),
    .data_in(data_in),
    .tx(tx),
    .busy(busy)
);

endmodule

module baud_gen #(
    parameter CLK_FREQ = 100,
    parameter BAUD_RATE = 10
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
    else if(counter == (CLK_PER_BIT-1)) begin
        counter <= '0;
        tick <= 1'b1; 
    end
    else begin
        tick <= '0; 
        counter <= counter + 1'b1;
    end
    

end
endmodule

module uart_tx(
    input logic clk,
    input logic reset,
    input logic baud_tick,
    input logic start,
    input logic [7:0] data_in,
    output logic tx,
    output logic busy

);

typedef enum logic[1:0] {
    IDLE, 
    START,
    DATA,
    STOP
} state_t;
logic [7:0]stored_data;
state_t state;
logic [2:0]bit_index;
logic tick; 
logic gonna_start;

always_ff @(posedge clk) begin
    if(reset) begin
        state <= IDLE;
        busy <=0;
        tx<=1;
    end
    if((~start) && state == IDLE) begin
        if(baud_tick) begin
            busy <= 0;
            tx <= 1;
        end
    end
    
    if(start && state==IDLE) begin
        gonna_start = 1;
        bit_index <= 0;


    end
    else if (state == START) begin
        if(baud_tick) begin
            tx<=0;

            busy <= 1;
            state <= DATA;
            tx <= stored_data[bit_index];
            bit_index<=bit_index + 1'b1;
        end

    end
    else if(state==DATA) begin
        if(baud_tick) begin
            busy <= 1;
            tx <= stored_data[bit_index];
            bit_index<=bit_index+1'b1;
            if(bit_index>=3'd7)
                state <= STOP;
        end
    end
    else if(state==STOP) begin
        if(baud_tick) begin
            tx <=1;
            busy<=1;
            state <= IDLE;
        end
    end

    if(baud_tick && gonna_start) begin
        busy <= 1;
        stored_data <= data_in;
        tx<=0;
        state <= START;
        bit_index<=0;
        gonna_start <= 0;
    end
// end
end
endmodule