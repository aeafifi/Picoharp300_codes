
% Demo for access to PicoHarp 300 Hardware via PHLIB v 3.0.
% The program performs a routed measurement based on hardcoded settings.
% (see 'you can change this' below). The resulting histograms (4 x 
% 65536 channels) are stored as a 4-column table in an ASCII output file.
% This requires a PHR 40x or PHR 800 router for PicoHarp 300. When using
% a PHR 800 you must also suitably set its inputs and CFDs (if installed).
%
% Michael Wahl, December 2013


% Constants from Phdefin.h

REQLIBVER =  '3.0';     % this is the version this program expects
MAXDEVNUM =      8;
HISTCHAN  =  65536;	    % number of histogram channels
RANGES	  =      8;
MODE_HIST =      0;
MODE_T2	  =      2;
MODE_T3	  =      3;

FLAG_OVERFLOW = hex2dec('0040');

ZCMIN		  =          0;		% mV
ZCMAX		  =         20;		% mV
DISCRMIN	  =          0;	    % mV
DISCRMAX	  =        800;	    % mV

SYNCOFFSMIN	  =     -99999;		% ps
SYNCOFFSMAX   =      99999;		% ps

RTCHANOFFSMIN =      -8000;		% ps
RTCHANOFFSMAX =       8000;		% ps

OFFSETMIN	  =          0;		% ps
OFFSETMAX	  = 1000000000;	    % ps

ACQTMIN		  =          1;		% ms
ACQTMAX		  =  360000000;	    % ms  (100*60*60*1000ms = 100h)

% Errorcodes from errorcodes.h

PH_ERROR_DEVICE_OPEN_FAIL		 = -1;

% Settings for the measurement 

Offset         = 0;       % you can change this
CFDZeroX0      = 10;      % you can change this
CFDLevel0      = 100;     % you can change this
CFDZeroX1      = 10;      % you can change this
CFDLevel1      = 100;     % you can change this
SyncDiv        = 8;       % you can change this
SyncOffset     = 0;       % you can change this
Binning        = 0;       % you can change this
Tacq           = 1000;    % you can change this      
PHR800Level    = -200;    % you can change this but watch for deadlock!
PHR800Edge     = 0;       % you can change this but watch for deadlock!
PHR800CFDLevel = 100;     % you can change this
PHR800CFDZeroX = 10;      % you can change this
RtChanOffset   = 0;       % you can change this
    

fprintf('\nPicoHarp 300 PHLib  Demo Application             PicoQuant 2013\n');

if (~libisloaded('PHlib'))    
    %Attention: The header file name given below is case sensitive and must
    %be spelled exactly the same as the actual name on disk except the file 
    %extension. 
    %Wrong case will apparently do the load successfully but you will not
    %be able to access the library!
    %The alias is used to provide a fixed spelling for any further access via
    %calllib() etc, which is also case sensitive.
    loadlibrary('/usr/local/lib64/ph300/phlib.so', 'phlib.h', 'alias', 'PHlib');
else
    fprintf('Note: PHlib was already loaded\n');
end;

if (libisloaded('PHlib'))
    fprintf('PHlib opened successfully\n');
    %libfunctionsview('PHlib'); %use this to test for proper loading
else
    fprintf('Could not open PHlib.\n');
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

fid = fopen('routing.out','w');
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
    
% In this demo we will use the first PicoHarp device we found, i.e. dev(1)
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

% This is only for information
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

% The following is specific for routing

ret = calllib('PHlib', 'PH_EnableRouting', dev(1), 1); 
if(ret<0)
    fprintf('\nPH_EnableRouting error %ld. No router!? Aborted.\n', ret);
    closedev;
    return;
end;

RtChannels = 0
RtChanPtr = libpointer('int32Ptr', RtChannels);
[ret,RtChannels] = calllib('PHlib', 'PH_GetRoutingChannels', dev(1), RtChanPtr);
if(ret<0)
    fprintf('\nPH_GetRoutingChannels error %ld. Aborted.\n', ret);
    closedev;
    return;
end;
if(RtChannels~=4)
    fprintf('\nInappropriate number of routing channels. Aborted.\n');
    return;
end;

[ret, Model, Version] = calllib('PHlib', 'PH_GetRouterVersion', dev(1), ModelPtr, VersionPtr);
if (ret<0)
    fprintf('\nPH_GetRouterVersion error %1d. Aborted.\n',ret);
    closedev;
	return;
else
	fprintf('\nFound Router Model %s Version %s', Model, Version);             
end;

if (strcmp(Model,'PHR 800'))
    fprintf('\nInitializing PHR 800...');
    for i=0:3 
        ret = calllib('PHlib', 'PH_SetPHR800Input', dev(1), i, PHR800Level, PHR800Edge);
        if (ret<0) % Full set of channels may not be installed, so be liberal here
            fprintf('\nPH_SetPHR800Input (ch%1d) failed. Maybe not installed.\n',ret);
        end;
    end;

    for i=0:3 		
		ret = calllib('PHlib', 'PH_SetPHR800CFD', dev(1), i, PHR800CFDLevel, PHR800CFDZeroX);
		if (ret<0) 	% CFDs may not be installed, so be liberal here 
			fprintf('\nPH_SetPHR800CFD (ch%1d) failed. Maybe not installed.\n',i);
        end;
    end;
end;

for i=0:3 		
	ret = calllib('PHlib', 'PH_SetRoutingChannelOffset', dev(1), i, RtChanOffset);
	if (ret<0) 	% CFDs may not be installed, so be liberal here 
        fprintf('\nPH_SetRoutingChannelOffset error %ld. Aborted.\n', ret);
        closedev;
        return;
    end;
end;

% From here you can repeat the measurement (with the same settings)

for (i=0:3) % must clear 4 Blocks for 4-channel Routing
    ret = calllib('PHlib', 'PH_ClearHistMem', dev(1),i);  
    if (ret<0)
        fprintf('\nPH_ClearHistMem error %ld. Aborted.\n', ret);
        closedev;
        return;
    end;
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
    
counts=[]; % this will be our matrix of counts
for (i=0:3) % must fetch 4 Blocks for 4-channel Routing
    countsbuffer  = uint32(zeros(1,HISTCHAN));
    bufferptr = libpointer('uint32Ptr', countsbuffer);
    [ret,countsbuffer] = calllib('PHlib', 'PH_GetHistogram', dev(1), bufferptr, i); 
    if (ret<0)
        fprintf('\nPH_GetHistogram error %ld. Aborted.\n', ret);
        closedev;
        return;
    end;
    Integralcount = sum(countsbuffer);        
    fprintf('\nIn ch%1d TotalCount = %1d',i+1, Integralcount);    
    counts = [counts,countsbuffer'];
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
 
for (i=1:HISTCHAN)
    fprintf(fid,'\n%5d %5d %5d %5d', counts(i,1), counts(i,2), counts(i,3), counts(i,4));
end;    

fprintf('\nData is in routing.out\n');

closedev;
    
if(fid>=0) 
    fclose(fid);
end;

