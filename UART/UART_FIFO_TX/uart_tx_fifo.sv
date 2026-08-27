`timescale 1ns/1ps

module uart_tx_fifo #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200,
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input logic clk,
    input logic reset,
    input logic write_en,
    input logic [WIDTH-1:0] write_data,
    output logic full,
    output logic tx
);
    logic tx_start;
    logic [WIDTH-1:0]data_in_tx;
    logic tx_busy;
    logic fifo_read_en;
    logic [WIDTH-1:0] fifo_read_data;
    logic empty;

    fifo fifo_module(
        .clk(clk),
        .reset(reset),
        .write_en(write_en),
        .write_data(write_data),
        .read_en(fifo_read_en),
        .read_data(fifo_read_data),
        .full(full),
        .empty(empty) 
    );
    uart_tx_top tx_module(
        .clk(clk),
        .reset(reset),
        .start(tx_start),
        .data_in(data_in_tx),
        .tx(tx),
        .busy(tx_busy)
    );

    always_ff @(posedge clk) begin
        if(reset) begin
        end
        else begin
            if(~empty && ~tx_busy) begin
                fifo_read_en <= 1;
                data_in_tx <= fifo_read_data;
            end
            else
                fifo_read_en <=0;
        end
    end

endmodule


module uart_tx_top #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200
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

module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input logic clk,
    input logic reset,
    input logic write_en,
    input logic [WIDTH-1:0] write_data,
    input logic read_en,
    output logic [WIDTH-1:0] read_data,

    output logic full,
    output logic empty
);
    logic [$clog2(DEPTH)-1:0] write_ptr;
    logic [$clog2(DEPTH)-1:0] read_ptr;
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [$clog2(DEPTH):0] count;
    
    assign full = (count == DEPTH);
    assign empty = (count == 0);

    always_ff @(posedge clk) begin
        if(reset) begin
            read_ptr <=0;
            write_ptr <=0;
            count <= 0;
        end
        else begin
            if(write_en && !full) begin
                if(~read_en)
                    count<= count+1;
                mem[write_ptr] <= write_data;
                if(write_ptr>=(DEPTH)) begin
                    write_ptr <= 0;
                end
                else
                    write_ptr <= write_ptr+1'b1;
            end
            if(read_en && !empty) begin
                read_data <= mem[read_ptr];
                if(~write_en)
                    count<= count-1;
                if(read_ptr>=(DEPTH-1)) begin
                    read_ptr <= 0;
                end
                else
                    read_ptr <= read_ptr+1'b1;
            end
        end
    end

endmodule