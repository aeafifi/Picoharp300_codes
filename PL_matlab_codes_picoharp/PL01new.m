% pg = visa('ni','GPIB0::10::0::INSTR');
% fopen(pg)

t=zeros(501,3);
t(:,1)=1:501;
t(:,2)=linspace(0,500,501);
tic
% fprintf(pg,':OUTP1 ON')% on output 1

for m=1:501
    delay=[':PULS:DEL1',blanks(1), num2str(t(m,2)),'NS'];
%     fprintf(pg,delay)
    t(m,3)=toc;
    pause(1)%.9863
end
t(end,3)=toc;
% fprintf(pg,':OUTP1 OFF')% on output 1
% fprintf(pg,':PULS:DEL1 0NS')

% fclose (pg)
% delete(pg)
% clear pg
t(:,4)=linspace(0,500,501);
t(:,5)=t(:,4)-t(:,3);