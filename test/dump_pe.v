module dump();
    initial begin
        $dumpfile ("pe.vcd");
        $dumpvars (0, pe);
        #1;
    end
endmodule