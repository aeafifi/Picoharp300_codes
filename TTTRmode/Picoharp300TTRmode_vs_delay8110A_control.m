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

% % Prepare list of delays to be scanned over, one time only\n",
   
offset =00 % ns\n",
step = 5 % ns\n",
pause_s = 10 % s\n",
time_span = 20 % ns\n",
num_point = ceil(time_span/step);
t = zeros(3,num_point+1)
%t(1,:) = cat(2,[0,0,0,0,0,0], linspace(step,time_span,num_point),[0,0,0,0,0,0])
t(1,:) = linspace(offset,time_span,num_point+1);
t(1,:) = t(1,:)+offset;
fprintf('Estimated time is %d sec, or % d min',(length(t(1,:))-1)*pause_s, (length(t(1,:))-1)*pause_s/60)

%  mkdir data_dcrbin3dm_1mdelaytwosdswithoutfilters
% cd data_dcrbin3dm_1mdelaytwosdswithoutfilters\


% Demo for access to PicoHarp 300 Hardware via PHLIB.DLL v 3.0.
% The program performs a TTTR measurement based on hardcoded settings.
% The resulting data stream is stored in a binary output file.
%
% Michael Wahl, December 2013
start_time = tic
folder_name=strcat('PH300_T2mode_bin',num2str(Binning),'Acqtime',num2str(Tacq/1000),'s',num2str(date));
mkdir(folder_name)
cd(folder_name)
for ii=1:1:(length(t(1,:)))
    %t(2,ii) = time.time()-start_time
    fprintf(obj,strcat(":PULS:DEL1 ",num2str(t(1,ii)),"NS"));
   

    
% Constants from Phdefin.h

REQLIBVER =  '3.0';     % this is the version this program expects
MAXDEVNUM =      8;
TTREADMAX = 131072;     % 128K event records 
HISTCHAN  =  65536;	    % number of histogram channels
RANGES	  =      8;
MODE_HIST =      0;
MODE_T2	  =      2;
MODE_T3	  =      3;

FLAG_OVERFLOW = hex2dec('0040');
FLAG_FIFOFULL = hex2dec('0003');

ZCMIN		  =          0;		% mV
ZCMAX		  =         20;		% mV
DISCRMIN	  =          0;	    % mV
DISCRMAX	  =        800;	    % mV

SYNCOFFSMIN	  =     -99999;		% ps
SYNCOFFSMAX	  =      99999;		% ps

OFFSETMIN	  =          0;		% ps
OFFSETMAX	  = 1000000000;	    % ps

ACQTMIN		  =          1;		% ms
ACQTMAX		  =  360000000;	    % ms  (100*60*60*1000ms = 100h)

% Errorcodes from errorcodes.h

PH_ERROR_DEVICE_OPEN_FAIL		 = -1;

% Settings for the measurement
 
Mode         = MODE_T2; % you can change this, observe appropriate SyncDivider
Offset       = 0;       % you can change this
CFDZeroX0    = 10;      % you can change this
CFDLevel0    = 100;     % you can change this
CFDZeroX1    = 10;      % you can change this
CFDLevel1    = 100;     % you can change this
SyncDiv      = 1;       %  you can change this, must be appropriate for chosen measurement mode!
SyncOffset   = 0;       %  you can change this
Binning      = 1;       %  you can change this, will apply in T3 mode only
Tacq         = 10000;    % you can change this      
    
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

fid = fopen(strcat('tttrmode',num2str(t(1,ii)),'ns.out'),'wb');
if (fid<0)
    fprintf('Cannot open output file\n');
    return;
end;

 fprintf('Measurement Mode : T%ld\n',Mode);
 fprintf('Binning          : %ld\n',Binning);
 fprintf('Offset           : %ld\n',Offset);
 fprintf('AcquisitionTime  : %ld\n',Tacq);
 fprintf('SyncDivider      : %ld\n',SyncDiv);
 fprintf('SyncOffset       : %ld\n',SyncOffset); 
 fprintf('CFDZeroCross0    : %ld\n',CFDZeroX0);
 fprintf('CFDLevel0        : %ld\n',CFDLevel0);
 fprintf('CFDZeroCross1    : %ld\n',CFDZeroX1);
 fprintf('CFDLevel1        : %ld\n',CFDLevel1);


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

[ret] = calllib('PHlib', 'PH_Initialize', dev(1), Mode);
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
    return
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

%Note: after Init or SetSyncDiv you must allow 100 ms for valid new count rate readings
pause(0.2);
Countrate0 = 0;
CountratePtr = libpointer('int32Ptr', Countrate0);
[ret, Countrate0] = calllib('PHlib', 'PH_GetCountRate', dev(1),0,CountratePtr);
Countrate1 = 0;
CountratePtr = libpointer('int32Ptr', Countrate1);
[ret, Countrate1] = calllib('PHlib', 'PH_GetCountRate', dev(1),1,CountratePtr);

fprintf('\nResolution=%1dps Countrate0=%1d/s Countrate1=%1d/s', Resolution, Countrate0, Countrate1);

buffer  = uint32(zeros(1,TTREADMAX));
bufferptr = libpointer('uint32Ptr', buffer);
nactual = int32(0);
nactualptr = libpointer('int32Ptr', nactual);

% from here you can repeat the measurement (with the same settings)

Progress = 0;
fprintf('\nProgress:%9d',Progress);
       
ret = calllib('PHlib', 'PH_StartMeas', dev(1),Tacq); 
if (ret<0)
    fprintf('\nPH_StartMeas error %ld. Aborted.\n', ret);
    closedev;
    return;
end
       
while(1)  
    
    flags = int32(0);
    flagsPtr = libpointer('int32Ptr', flags);
    [ret,flags] = calllib('PHlib', 'PH_GetFlags', dev(1), flagsPtr);
    if (flags<0)
        fprintf('\nPH_GetFlags error %ld. Aborted.\n', ret);
        break;
    end;
    FiFoWasFull=bitand(uint32(flags),FLAG_FIFOFULL);
   
    if (FiFoWasFull) 
        fprintf('\nFiFo Overrun!\n'); 
        break;
    end;
		
	[ret, buffer, nactual] = calllib('PHlib','PH_ReadFiFo', dev(1), bufferptr, TTREADMAX, nactualptr);
    %Note that PH_ReadFiFo may return less than requested  
	if (ret<0)  
        fprintf('\nPH_ReadFiFo error %d\n',ret); 
        break;
    end;  

    if(nactual) 
        cnt = fwrite(fid, buffer(1:nactual),'uint32');
        if(cnt ~= nactual)
            fprintf('\nfile write error\n');
            break;
        end;          
		Progress = Progress + nactual;
		fprintf('\b\b\b\b\b\b\b\b\b%9d',Progress);
    else
        ctcdone = int32(0);
        ctcdonePtr = libpointer('int32Ptr', ctcdone);
        [ret, ctcdone] = calllib('PHlib', 'PH_CTCStatus', dev(1), ctcdonePtr); 
        if (ctcdone) 
            fprintf('\nDone\n'); 
            break;
        end
    end
    %PH_GetCountRate can be called here if needed
    
    %[ret, buffer, nactual] = calllib('PHlib','PH_GetCountRate', dev(1), bufferptr, TTREADMAX, nactualptr);
    
end %while


ret = calllib('PHlib', 'PH_StopMeas', dev(1)); 
if (ret<0)
    fprintf('\nPH_StopMeas error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
        
closedev;
    
fprintf('\nData is in tttrmode.out\n');

if(fid>0) 
    fclose(fid);
end;

end 
cd ..

fclose(obj);

