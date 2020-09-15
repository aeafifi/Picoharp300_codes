%%%%% Script for 8110A pulse generator control in MATLB
%%%%  Abdelrahman Afifi
%%%% 27 May 2019
instrfindall
delete(instrfindall)
clc;
clear all;
obj=gpib('ni',0,28);
obj.InputBufferSize = 1000;
obj.timeout=1000;
%connect the object to the oscilloscope
fopen(obj)

fprintf(obj,':OUTP1 ON') % Output1 ON\n",
pause(1)
fprintf(obj,':OUTP2 ON') % Output1 ON\n",

fprintf(obj,':OUTP1:IMP 50OHM') % Output Impedance\n",
fprintf(obj,':OUTP1:IMP:EXT 50OHM') % Output Impedance\n",
pause(1)

fprintf(obj,':OUTP1:POL NORM') % Invert Output (negative polarity)\n",
fprintf(obj,':PULS:TRAN1 1.9NS')
fprintf(obj,':ARM:SOUR INT1') % Internal Trigger\n",
%fprintf(':ARM:SOUR EXT1') % External Trigger\n",
pause(1)

% %fprintf(':ARM:LEV -0.5V') % Trigger Level\n",
fprintf(obj,':PULS:DEL1 0NS') % Pulse Delay\n",
fprintf(obj,':PULS:WIDT1 10NS') % Pulse Width\n",
fprintf(obj,':PULS:WIDT2 10NS') % Pulse Width\n",

fprintf(obj,':PULS:PER 100NS') % Pulse period\n",
% fprintf(':HOLD VOLT') % Voltage Hold\n",
% 
% fprintf(':VOLT1 500MV') % Voltage Amplitude \n",
% %fprintf(':VOLT1:LIM 3V') % Voltage limit\n",
% %fprintf(':HOLD CURR') % Current High\n",
% %fprintf(':CURR1 20MA') % Current High\n",
% 
fprintf(obj,':VOLT1:HIGH 250MV') % Voltage Low"
fprintf(obj,':VOLT1:LOW 0V') % Voltage Low"

fprintf(obj,':VOLT2:HIGH 250MV') % Voltage Low"
fprintf(obj,':VOLT2:LOW 0V') % Voltage Low"
% % Prepare list of delays to be scanned over, go and fro\n",
% 
% %offset = 0 % ns\n",
% %step = 5 % ns\n",
% %time_span = 20 % ns\n",
% %num_point = int(time_span/step)
% %t = np.zeros((2,num_point*4+12))
% %t[0] = np.concatenate(([0,0,0,0,0,0],
% %                      np.linspace(0.5,time_span,num_point),
% %                      np.linspace(time_span-step,0,num_point),
% %                      np.linspace(0.5,time_span,num_point),
% %                      np.linspace(time_span-step,0,num_point),
% %                      [0,0,0,0,0,0]))
% %t[0] = t[0]+offset
% %print('Estimated time is %d sec, or %d min' 
% %      % (len(t[0])-1,(len(t[0])-1)/60))
% % Prepare list of delays to be scanned over, one time only\n",
%   
offset =00 % ns\n",
step = 5 % ns\n",
pause_s = 1 % s\n",
time_span = 20 % ns\n",
num_point = round(time_span/step);
t = zeros(3,num_point+12)
t(1,:) = cat(2,[0,0,0,0,0,0], linspace(step,time_span,num_point),[0,0,0,0,0,0])
t(1,:) = t(1,:)+offset;
fprintf('Estimated time is %d sec, or % d min',(length(t(1,:))-1)*pause_s, (length(t(1,:))-1)*pause_s/60)
    
%     
% % Send the list of delays to pulse generator to start the scan\n",
% 
%a=strcat(":PULS:DEL1 ",num2str(t(1,ii)),"NS")
start_time = tic
for ii=1:1:(length(t(1,:)))
    %t(2,ii) = time.time()-start_time
    fprintf(obj,strcat(":PULS:DEL1 ",num2str(t(1,ii)),"NS"));
    %t(1,ii) = time.time()-start_time
    pause(pause_s)
end
%t[1][-1] = time.time()-start_time
fclose(obj);
%fprintf('Actual elapsed time is %d sec',t(1,end))
hbar = 1.05*10^(-34) % J.s\n",
% ev = 1.5*10**(-19) %J\n",
% ph_qd = 0.751*ev % 1.6 micron"
%     
% p = 0.005*10**(-9) % W\n",
% pulse_freq = 2.5 % MHz\n",
% ph_rate = p/(ph_qd)/(10**6) % MHz\n",
% ph_per_pulse = ph_rate/pulse_freq % Hz\n",
% ph_per_pulse
% fprintf(':OUTP2 ON')