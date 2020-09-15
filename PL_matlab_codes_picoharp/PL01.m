pg = visa('ni','GPIB0::12::0::INSTR');
fopen(pg)

t=zeros(76,3);
t(:,1)=1:76;
t(:,2)=[0,0,0,0,0,0,linspace(0.5,8,16),linspace(7.5,0,16),linspace(0.5,8,16),linspace(7.5,0,16),0,0,0,0,0,0];
tic
fprintf(pg,':OUTP1 ON')% on output 1

for m=1:75
    delay=[':PULS:DEL1',blanks(1), num2str(t(m,2)),'NS'];
    fprintf(pg,delay)
    t(m,3)=toc;
    pause(1)%.9863
end
t(end,3)=toc;
fprintf(pg,':OUTP1 OFF')% on output 1
fprintf(pg,':PULS:DEL1 0NS')

fclose (pg)
delete(pg)
clear pg

%fprintf(pg,':PULS:DEL2 1NS')
% toc
% toc(ticID)
% elapsedTime = toc
% elapsedTime = toc(ticID)

% fprintf(pg,':SYST:KEY 21')% on output 1
% fprintf(pg,':SYST:KEY 22')% on output 1
% fprintf(pg,':OUTP1 ON')% on output 1
% fprintf(pg,':SYST:KEY 22')% on output 1