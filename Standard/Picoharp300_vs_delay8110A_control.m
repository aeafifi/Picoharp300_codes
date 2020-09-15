%% Script for Control the Picoharp300 with the delay generator for Coincidence Measurements
%% Abdelrahman Afifi UBC 
%% 28 May 2019
% instrfindall
% delete(instrfindall)
clc;
clear all;

%%%%% Script for 8110A pulse generator control in MATLB
%%%%  Abdelrahman Afifi
%%%% 27 May 2019

obj=gpib('ni',0,28);
obj.InputBufferSize = 1000;
obj.timeout=1000;
%connect the object to the oscilloscope
fopen(obj)

fprintf(obj,':OUTP1 OFF') % Output1 ON\n",
pause(1)
fprintf(obj,':OUTP2 OFF') % Output1 ON\n",

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

fprintf(obj,':PULS:PER 1000NS') % Pulse period\n",
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
step = 20 % ns\n",
pause_s = 30 % s\n",
time_span = 400 % ns\n",
num_point = ceil(time_span/step);
t = zeros(3,num_point+1)
%t(1,:) = cat(2,[0,0,0,0,0,0], linspace(step,time_span,num_point),[0,0,0,0,0,0])
t(1,:) = linspace(offset,time_span,num_point+1);
t(1,:) = t(1,:)+offset;
fprintf('Estimated time is %d sec, or % d min',(length(t(1,:))-1)*pause_s, (length(t(1,:))-1)*pause_s/60)
%fold_name='data_dcrbin0dm_1mdelaytwosdswithoutfilters1'


% Constants from Phdefin.h

REQLIBVER   =  '3.0';     % this is the version this program expects
MAXDEVNUM   =      8;
HISTCHAN    =  65536;	    % number of histogram channels
MAXBINSTEPS =      8;
MODE_HIST   =      0;
MODE_T2	    =      2;
MODE_T3	    =      3;

FLAG_OVERFLOW = hex2dec('0040');

ZCMIN		  =          0;		% mV
ZCMAX		  =         20;		% mV
DISCRMIN	  =          0;	    % mV
DISCRMAX	  =        800;	    % mV

SYNCOFFSMIN	  =     -99999;		% ps
SYNCOFFSMAX	  =      99999;		% ps

OFFSETMIN	  =          0;		% ps
OFFSETMAX	  = 1000000000;	    % ps

ACQTMIN		  =          1;		% ms
ACQTMAX		  =  360000000;	    % ms  (10*60*60*1000ms = 100h)

% Errorcodes from errorcodes.h

PH_ERROR_DEVICE_OPEN_FAIL		 = -1;

% Settings for the measurement
 
Offset       = 0;       %  you can change this
CFDZeroX0    = 10;      %  you can change this
CFDLevel0    = 150;     %  you can change this
CFDZeroX1    = 10;      %  you can change this
CFDLevel1    = 150;     %  you can change this
SyncDiv      = 1;       %  you can change this
SyncOffset   = 0;       %  you can change this
Binning      = 7;       %  you can change this 0-->4ps, 1--> 8ps, ...,7--> 512ps.
Tacq         = pause_s*1000;    %  you can change this    ms.  
    
fprintf('\nPicoHarp 300 PHLib.DLL Demo Application             PicoQuant 2013\n');

if (~libisloaded('PHlib'))    
    %Attention: The header file name given below is case sensitive and must
    %be spelled exactly the same as the actual name on disk except the file 
    %extension. 
    %Wrong case will apparently do the load successfully but you will not
    %be able to access the library!
    %The alias is used to provide a fixed spelling for any further access via
    %calllib() etc, which is also case sensitive.
    loadlibrary('phlib64.dll', 'phlib.h', 'alias', 'PHlib');
else
    fprintf('Note: PHlib was already loaded\n');
end;

if (libisloaded('PHlib'))
    fprintf('PHlib opened successfully\n');
    %libfunctionsview('PHlib'); %use this to test for proper loading
else
    fprintf('Could not open PHlib\n');
    return;
end;
    
LibVersion    = '????'; %enough length!
LibVersionPtr = libpointer('cstring', LibVersion);

[ret, LibVersion] = calllib('PHlib', 'PH_GetLibraryVersion', LibVersionPtr);
if (ret<0)
    fprintf('Error in GetLibVersion. Aborted.\n');
    err = PH_GETLIBVERSION_ERROR;
else
	fprintf('PHLib version is %s\n', LibVersion);
end;

if ~strcmp(LibVersion,REQLIBVER)
    fprintf('This program requires PHLib version %s\n', REQLIBVER);
    return;
end;

% fid = fopen('Picoharp300_vsdelay_v1_28May2019.out','w');
% if (fid<0)
%     fprintf('Cannot open output file\n');
%     return;
% end;
% 
%  fprintf(fid,'Binning          : %ld\n',Binning);
%  fprintf(fid,'Offset           : %ld\n',Offset);
%  fprintf(fid,'AcquisitionTime  : %ld\n',Tacq);
%  fprintf(fid,'SyncDivider      : %ld\n',SyncDiv);
%  fprintf(fid,'SyncOffset       : %ld\n',SyncOffset); 
%  fprintf(fid,'CFDZeroCross0    : %ld\n',CFDZeroX0);
%  fprintf(fid,'CFDLevel0        : %ld\n',CFDLevel0);
%  fprintf(fid,'CFDZeroCross1    : %ld\n',CFDZeroX1);
%  fprintf(fid,'CFDLevel1        : %ld\n',CFDLevel1);


fprintf('\nSearching for PicoHarp devices...');

dev = [];
found = 0;
Serial     = '12345678'; %enough length!
SerialPtr  = libpointer('cstring', Serial);
ErrorStr   = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'; %enough length!
ErrorPtr   = libpointer('cstring', ErrorStr);

for i=0:MAXDEVNUM-1
    [ret, Serial] = calllib('PHlib', 'PH_OpenDevice', i, SerialPtr);
    if (ret==0)       % Grab any PicoHarp we successfully opened
        fprintf('\n  %1d        S/N %s', i, Serial);
        found = found+1;            
        dev(found)=i; %keep index to devices we may want to use
    else
        if(ret==PH_ERROR_DEVICE_OPEN_FAIL)
            fprintf('\n  %1d        no device', i);
        else 
            [ret, ErrorStr] = calllib('PHlib', 'PH_GetErrorString', ErrorPtr, ret);
            fprintf('\n  %1d        %s', i,ErrorStr);
        end;
	end;
end;
    
% in this demo we will use the first PicoHarp device we found, i.e. dev(1)
% you could also check for a specific serial number, so that you always know 
% which physical device you are talking to.

if (found<1)
	fprintf('\nNo device available. Aborted.\n');
	return; 
end;

fprintf('\nUsing device #%1d',dev(1));
fprintf('\nInitializing the device...');

[ret] = calllib('PHlib', 'PH_Initialize', dev(1), MODE_HIST); 
if(ret<0)
	fprintf('\nPH init error %d. Aborted.\n',retcode);
    closedev;
	return;
end; 

%this is only for information
Model      = '1234567890123456'; %enough length!
Partnum    = '12345678'; %enough length!
Version    = '12345678'; %enough length!
ModelPtr   = libpointer('cstring', Model);
PartnumPtr = libpointer('cstring', Partnum);
VersionPtr = libpointer('cstring', Version);

[ret, Model, Partnum, Version] = calllib('PHlib', 'PH_GetHardwareInfo', dev(1), ModelPtr, PartnumPtr, VersionPtr);
if (ret<0)
    fprintf('\nPH_GetHardwareInfo error %1d. Aborted.\n',ret);
    closedev;
	return;
else
	fprintf('\nFound Model %s Part number %s Version: %s', Model, Partnum, Version);             
end;
        
fprintf('\nCalibrating ...');
[ret] = calllib('PHlib', 'PH_Calibrate', dev(1));
if (ret<0)
    fprintf('\nPH_Calibrate error %1d. Aborted.\n',ret);
    closedev;
    return;
end;
   
[ret] = calllib('PHlib', 'PH_SetSyncDiv', dev(1), SyncDiv);
if (ret<0)
    fprintf('\nPH_SetSyncDiv error %1d. Aborted.\n',ret);
    closedev;
    return;
end;

[ret] = calllib('PHlib', 'PH_SetSyncOffset', dev(1), SyncOffset);
if (ret<0)
    fprintf('\nPH_SetSyncOffset error %1d. Aborted.\n',ret);
    closedev;
    return;
end;

[ret] = calllib('PHlib', 'PH_SetInputCFD', dev(1), 0, CFDLevel0, CFDZeroX0);
if (ret<0)
    fprintf('\nPH_SetInputCFD error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

[ret] = calllib('PHlib', 'PH_SetInputCFD', dev(1), 1, CFDLevel1, CFDZeroX1);
if (ret<0)
    fprintf('\nPH_SetInputCFD error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

[ret] = calllib('PHlib', 'PH_SetBinning', dev(1), Binning);
if (ret<0)
    fprintf('\nPH_SetBinning error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

[Offset] = calllib('PHlib', 'PH_SetOffset', dev(1), Offset);
if (Offset<0)
    fprintf('\nPH_SetOffset error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

ret = calllib('PHlib', 'PH_SetStopOverflow', dev(1), 1, 65535);
if (ret<0)
    fprintf('\nPH_SetStopOverflow error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

Resolution = 0;
ResolutionPtr = libpointer('doublePtr', Resolution);
[ret, Resolution] = calllib('PHlib', 'PH_GetResolution', dev(1), ResolutionPtr);
if (Resolution<0)
    fprintf('\nPH_GetResolution error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

% Note: after Init or SetSyncDiv you must allow 100 ms for valid new count rate readings
pause(0.2);
Countrate0 = 0;
CountratePtr = libpointer('int32Ptr', Countrate0);
[ret, Countrate0] = calllib('PHlib', 'PH_GetCountRate', dev(1),0,CountratePtr);
Countrate1 = 0;
CountratePtr = libpointer('int32Ptr', Countrate1);
[ret, Countrate1] = calllib('PHlib', 'PH_GetCountRate', dev(1),1,CountratePtr);

fprintf('\nResolution=%1dps Countrate0=%1d/s Countrate1=%1d/s', Resolution, Countrate0, Countrate1);

%%% folder name 
folder_name=strcat('PH300_','ASE_source_off','1mdelaytwospdswithoutfilters30s',num2str(date));
mkdir(folder_name)  %PH300_dcrbin0_1mdelaytwospdswithoutfilters1
cd(folder_name)	%PH300_dcrbin0_1mdelaytwospdswithoutfilters1


%%% Add waitbar 
f = waitbar(0,'1','Name','PicoHarp300 Histogram Data Acquisition ...',...
    'CreateCancelBtn','setappdata(gcbf,''canceling'',1)');

setappdata(f,'canceling',0);


% % Send the list of delays to pulse generator to start the scan\n",
% 
%a=strcat(":PULS:DEL1 ",num2str(t(1,ii)),"NS")
start_time = tic
for ii=1:1:(length(t(1,:)))
   
    
    if getappdata(f,'canceling')
        break
    end
    
    % Update waitbar and message
    waitbar(ii/length(t(1,:)),f,sprintf(' Percentage Done %3.2f ',100*ii/length(t(1,:))))
    
    %t(2,ii) = time.time()-start_time
    fprintf(obj,strcat(":PULS:DEL1 ",num2str(t(1,ii)),"NS"));
    %t(1,ii) = time.time()-start_time

%fprintf('Actual elapsed time is %d sec',t(1,end))
% hbar = 1.05*10^(-34) % J.s\n",
% ev = 1.5*10**(-19) %J\n",
% ph_qd = 0.751*ev % 1.6 micron"
%     
% p = 0.005*10**(-9) % W\n",
% pulse_freq = 2.5 % MHz\n",
% ph_rate = p/(ph_qd)/(10**6) % MHz\n",
% ph_per_pulse = ph_rate/pulse_freq % Hz\n",
% ph_per_pulse
% fprintf(':OUTP2 ON')

fid = fopen(strcat('PH300Hist_delay',num2str(t(1,ii)),'_IntT',num2str(pause_s),'_binning',num2str(2^(Binning+2)),'ps_',num2str(date),'.txt'),'w');
if (fid<0)
    fprintf('Cannot open output file\n');
    return;
end;

 fprintf(fid,'Binning          : %ld\n',Binning);
 fprintf(fid,'Offset           : %ld\n',Offset);
 fprintf(fid,'AcquisitionTime  : %ld\n',Tacq);
 fprintf(fid,'SyncDivider      : %ld\n',SyncDiv);
 fprintf(fid,'SyncOffset       : %ld\n',SyncOffset); 
 fprintf(fid,'CFDZeroCross0    : %ld\n',CFDZeroX0);
 fprintf(fid,'CFDLevel0        : %ld\n',CFDLevel0);
 fprintf(fid,'CFDZeroCross1    : %ld\n',CFDZeroX1);
 fprintf(fid,'CFDLevel1        : %ld\n',CFDLevel1);


%%% Control Picoharp300 alone 
% Demo for access to PicoHarp 300 Hardware via PHLIB.DLL v 3.0.
% The program performs a measurement based on hardcoded settings.
% The resulting histogram (65536 channels) is stored in an ASCII output file.
%
% Michael Wahl, December 2013



% From here you can repeat the measurement (with the same settings)

ret = calllib('PHlib', 'PH_ClearHistMem', dev(1),0);    % always use Block 0 if not Routing
if (ret<0)
    fprintf('\nPH_ClearHistMem error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
        
ret = calllib('PHlib', 'PH_StartMeas', dev(1),Tacq); 
if (ret<0)
    fprintf('\nPH_StartMeas error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
         
fprintf('\nMeasuring for %1d milliseconds...',Tacq);
        
ctcdone = int32(0);
ctcdonePtr = libpointer('int32Ptr', ctcdone);
while (ctcdone==0)
    [ret, ctcdone] = calllib('PHlib', 'PH_CTCStatus', dev(1), ctcdonePtr);
end;    
         
ret = calllib('PHlib', 'PH_StopMeas', dev(1)); 
if (ret<0)
    fprintf('\nPH_StopMeas error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
        
countsbuffer  = uint32(zeros(1,HISTCHAN));
bufferptr = libpointer('uint32Ptr', countsbuffer);
[ret,countsbuffer] = calllib('PHlib', 'PH_GetHistogram', dev(1), bufferptr, 0); 
if (ret<0)
    fprintf('\nPH_GetHistogram error %ld. Aborted.\n', ret);
    closedev;
    return;
end;

flags = int32(0);
flagsPtr = libpointer('int32Ptr', flags);
[ret,flags] = calllib('PHlib', 'PH_GetFlags', dev(1), flagsPtr);
if (flags<0)
    fprintf('\nPH_GetFlags error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
        
if(bitand(uint32(flags),FLAG_OVERFLOW)) 
    fprintf('  Overflow.');
end;     

Integralcount(ii) = sum(countsbuffer);        
fprintf('\nTotalCount=%1d', Integralcount(ii));

for (i=1:HISTCHAN)
    fprintf(fid,'\n%5d', countsbuffer(i));
end    

fprintf('\nData is in dlldemo.out ');


    
if(fid>0) 
    fclose(fid);
end;

    %pause(pause_s)
end
%% Closing the objects
delete(f)

fclose(obj);
cd ..
closedev;


%%plotting the results total counts vs delay
plot(t(1,:),Integralcount,'r-o','linewidth',2)
xlabel('Delay in ns')
ylabel('Total counts ')
legend(strcat('Int time',num2str(pause_s),' with bins', num2str(2^(Binning+2)),'ps'))


% Ase_power_dBm=-2.7
% laser_wl_nm=1550;
% Atten1_dB=60;
% Atten2_dB=40;
% 
% % laser_power_mW=4;
% % laser_wl_nm=1550;
% % Atten1_dB=60;
% % Atten2_dB=40;
% % filter_wl=1550;
%  save data_for_PH300_sweep_ASEonpausetime30s.mat