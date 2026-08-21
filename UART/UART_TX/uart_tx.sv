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
always_ff @(posedge clk) begin
    if(reset) begin
        state <= IDLE;
        busy <=0;
        tx<=1;
    end
    else if(start && state==IDLE) begin
        busy <= 1;
        stored_data <= data_in;
        tx<=0;
        state <= START;
        bit_index<=0;

    end
    else if (state == START) begin
        busy <= 1;
        state <= DATA
    else if(state==DATA) begin
        busy <= 1;
        tx <= stored_data[bit_index];
        bit_index++;
        if(bit_index>=3'd7)
            state <= STOP;
    end
    else if(state==STOP) begin
        tx <=1;
        busy<=0;
        state <= IDLE;
    end



end
endmodule