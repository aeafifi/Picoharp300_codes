% % %clear all
% % fil=['C:\Users\Bigcheese\Desktop\CANADAUBC\picoharp\t2toknow_000x.txt'];%strcat(num2str(kk))
% % A= importdata(fil);
% 
% 
% fid = fopen('C:\Users\Bigcheese\Desktop\CANADAUBC\picoharp\t2toknow_000x.txt');
% 
% c = textscan(fid, ...            
%                 'v1=%f %*s \n%7u %08x %14.0f %2u', ...
%                 'Delimiter', ' ', ...
%                 'CollectOutput', true);
%   
% fclose(fid);
% 
% %fprintf(fpout,'\n%7u %08x %14.0f %2u ',i,T2Record,T2time,chan);

 %%%% use read_pt2rqt   to read data
fil=['C:\Users\Bigcheese\Desktop\CANADAUBC\picoharp\t2toknow_000.out'];
A= importdata(fil);
B=diff(A.data(:,2:4));
C=B(B(:,1)==1,3);
% figure (1);plot(diff(A.data(:,4)))
% figure (2);plot(diff(A.data(A.data(:,2)==0,4)))
% figure (3);plot(C)
% figure (4);hist(C,(min(C):1e-9:max(C)));

figure (6)
subplot(2,2,1)
plot(diff(A.data(:,4)),'MarkerSize',0.5,'Marker','.')
xlabel('Data Point','FontSize',14);
ylabel('Time [s] ','FontSize',14);

subplot(2,2,2)
plot(diff(A.data(A.data(:,2)==0,4)),'MarkerSize',0.5,'Marker','.')
xlabel('Data Point [Sync]','FontSize',14);
ylabel('Time [s]','FontSize',14);

subplot(2,2,3)
plot(C,'MarkerSize',0.5,'Marker','.')
xlabel('Data Point [Stop]','FontSize',14);
ylabel('Time [s]','FontSize',14);

subplot(2,2,4)
hist(C,(min(C):5e-9:max(C)))
xlabel('Time [s]','FontSize',14);
ylabel('Counts','FontSize',14);