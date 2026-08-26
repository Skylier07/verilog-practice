module uart_loopback #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200
)(
    input logic clk,
    input logic reset,
    input logic [7:0] tx_data,
    input logic tx_start,
    output logic tx_busy,

    output logic [7:0] rx_data,
    output logic rx_valid
);
    logic serial_wire;

    uart_rx rx(
        .clk(clk),
        .reset(reset),
        .rx(serial_wire),
        .data_out(rx_data),
        .data_valid(rx_valid)
    );

    uart_tx_top #(
    .CLK_FREQ(50000000),
    .BAUD_RATE(115200)
) tx(
        .clk(clk),
        .reset(reset),
        .start(tx_start),
        .data_in(tx_data),
        .tx(serial_wire),
        .busy(tx_busy)
    );



endmodule

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
                bit_index <=0;
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

`timescale 1ns/1ps

module uart_tx_top #(
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