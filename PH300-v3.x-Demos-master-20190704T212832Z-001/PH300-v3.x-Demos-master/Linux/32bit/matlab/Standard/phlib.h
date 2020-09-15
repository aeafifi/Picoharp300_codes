/* Functions exported by the PicoHarp programming library PHLib */

/* Ver. 3.0.0.3 October 2015 */

#ifndef _WIN32
#define _stdcall
#endif

extern int _stdcall PH_GetLibraryVersion(char* version);
extern int _stdcall PH_GetErrorString(char* errstring, int errcode);

extern int _stdcall PH_OpenDevice(int devidx, char* serial);
extern int _stdcall PH_CloseDevice(int devidx);
extern int _stdcall PH_Initialize(int devidx, int mode);

//all functions below can only be used after PH_Initialize

extern int _stdcall PH_GetHardwareInfo(int devidx, char* model, char* partno, char* version); //new in v 3.0
extern int _stdcall PH_GetSerialNumber(int devidx, char* serial);
extern int _stdcall PH_GetFeatures(int devidx, int* features);                                //new in v 3.0
extern int _stdcall PH_GetBaseResolution(int devidx, double* resolution, int* binsteps);      //changed in v 3.0
extern int _stdcall PH_GetHardwareDebugInfo(int devidx, char *debuginfo);                     //new in v 3.0

extern int _stdcall PH_Calibrate(int devidx);
extern int _stdcall PH_SetInputCFD(int devidx, int channel, int level, int zc);               //changed in v 3.0
extern int _stdcall PH_SetSyncDiv(int devidx, int div);
extern int _stdcall PH_SetSyncOffset(int devidx, int syncoffset);                             //new in v 3.0

extern int _stdcall PH_SetStopOverflow(int devidx, int stop_ovfl, int stopcount);	
extern int _stdcall PH_SetBinning(int devidx, int binning);
extern int _stdcall PH_SetOffset(int devidx, int offset);                                     //changed in v 3.0
extern int _stdcall PH_SetMultistopEnable(int devidx, int enable);                            //new in v 3.0

extern int _stdcall PH_ClearHistMem(int devidx, int block);
extern int _stdcall PH_StartMeas(int devidx, int tacq);
extern int _stdcall PH_StopMeas(int devidx);
extern int _stdcall PH_CTCStatus(int devidx, int* ctcstatus);                                 //changed in v 3.0

extern int _stdcall PH_GetHistogram(int devidx, unsigned int* chcount, int block);            //changed in v 3.0
extern int _stdcall PH_GetResolution(int devidx, double* resolution);                         //changed in v 3.0
extern int _stdcall PH_GetCountRate(int devidx, int channel, int* rate);                      //changed in v 3.0
extern int _stdcall PH_GetFlags(int devidx, int* flags);                                      //changed in v 3.0
extern int _stdcall PH_GetElapsedMeasTime(int devidx, double* elapsed);                       //changed in v 3.0

extern int _stdcall PH_GetWarnings(int devidx, int* warnings);                                //changed in v 3.0
extern int _stdcall PH_GetWarningsText(int devidx, char* text, int warnings);  

//for the Time Tagging modes
extern int _stdcall PH_SetMarkerEnable(int devidx, int en0, int en1, int en2, int en3);       //new in v 3.0
extern int _stdcall PH_SetMarkerEdges(int devidx, int me0, int me1, int me2, int me3);        //changed in v 3.0
extern int _stdcall PH_SetMarkerHoldoffTime(int devidx, int holdofftime);                     //new in v 3.0
extern int _stdcall PH_ReadFiFo(int devidx, unsigned int* buffer, int count, int* nactual);   //changed in v 3.0

//for Routing
extern int _stdcall PH_GetRouterVersion(int devidx, char* model, char* version);  
extern int _stdcall PH_GetRoutingChannels(int devidx, int* rtchannels);                 //changed in v 3.0
extern int _stdcall PH_EnableRouting(int devidx, int enable);
extern int _stdcall PH_SetRoutingChannelOffset(int devidx, int channel, int offset);    //new in v 3.0
extern int _stdcall PH_SetPHR800Input(int devidx, int channel, int level, int edge);  
extern int _stdcall PH_SetPHR800CFD(int devidx, int channel, int level, int zc); 

 
