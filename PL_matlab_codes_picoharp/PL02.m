ds345 = visa('ni','GPIB0::19::0::INSTR');
fopen(ds345)

% t=zeros(76,3);
% t(:,1)=1:76;
% t(:,2)=[0,0,0,0,0,0,linspace(0.5,8,16),linspace(7.5,0,16),linspace(0.5,8,16),linspace(7.5,0,16),0,0,0,0,0,0];
% tic
% fprintf(pg,':OUTP2 ON')% on output 1
% 
% for m=1:75
%     delay=[':PULS:DEL2',blanks(1), num2str(t(m,2)),'NS'];
%     fprintf(pg,delay)
%     t(m,3)=toc;
%     pause(5)%.9863
% end
% t(end,3)=toc;
% fprintf(pg,':OUTP2 OFF')% on output 1
% fprintf(pg,':PULS:DEL2 0NS')


fprintf(ds345,'FREQ 100000')
fprintf(ds345,'AMPL 1.0VP')
fprintf(ds345,'PHSE 1.0')

fclose (ds345)
delete(ds345)
clear ds345

%fprintf(pg,':PULS:DEL2 1NS')
% toc
% toc(ticID)
% elapsedTime = toc
% elapsedTime = toc(ticID)