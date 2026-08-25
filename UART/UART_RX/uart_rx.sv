`timescale 1ns/1ps

module uart_rx #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200
) (
    input logic clk,
    input logic reset,
    input logic rx,

    output logic [7:0] data_out,
    output logic data_valid
);

typedef enum logic[1:0] {
    IDLE, 
    START,
    DATA,
    STOP
} state_t;

state_t state;
localparam int CLK_PER_BIT = CLK_FREQ/BAUD_RATE;
localparam int BIT_REQUIRED = $clog2(CLK_PER_BIT);
logic [BIT_REQUIRED-1:0] counter; 
logic [7:0]data_reg;
logic [BIT_REQUIRED-1:0]bit_index; 
logic [BIT_REQUIRED-1:0] half_bit = (CLK_PER_BIT/2);
logic possible_start;
logic [3:0] data_index;

always_ff @(posedge clk) begin
    bit_index <= (bit_index == CLK_PER_BIT) ? '0 : bit_index+1;
    if(reset) begin
        state <= IDLE;
        data_valid <= 0;
        data_out <= '0;
        bit_index <= '0;
        counter <= '0;
        possible_start <=0;
    end
    else if(state == IDLE) begin
        if((bit_index == half_bit) && possible_start) begin
            if(rx == 0) begin
                state <= START;
                bit_index <=0;
                possible_start <=0;
                data_index <= '0;
            end
            else begin
                bit_index <=
                possible_start <=0;
            end
        end

        if(rx == 0 && ~possible_start) begin 
            bit_index <= 0;
            possible_start <= 1; 
        end
        data_valid <= 0;
    end

    if(state == START) begin
        if(bit_index == CLK_PER_BIT) begin
            data_reg[data_index] <= rx;
            data_index <= data_index + 1'b1;
            if(data_index >7) begin
                state <= STOP;
                data_index <=0;
            end
        end
    end
    if(state == STOP && (bit_index == CLK_PER_BIT)) begin
        if(rx ==1) begin
            data_out <= data_reg;
            data_valid <= 1;
            state <= IDLE;
        end
        else begin
            data_valid <= 0;
            state <= IDLE;
        end
    end



end
endmodule