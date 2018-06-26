#ifndef ATMECHELLE_H
#define ATMECHELLE_H

#include <windows.h>

#if defined (_BUILDMICRODLL)
#define DLL_DEF __declspec(dllexport) WINAPI
#else
#define DLL_DEF __declspec(dllimport) WINAPI
#endif

#define MECHELLE_ERROR_CODES	20001
#define MECHELLE_SUCCESS	20002
#define MECHELLE_NOTINITIALIZED	20003
#define MECHELLE_DLLNOTFOUND    21000
#define MECHELLE_ATMCD32DLLNOTFOUND 21001
#define MECHELLE_TEMPERATUREERROR 21002
#define MECHELLE_NOTEMPERATUREDIFFERENCE 21003


//structures that the interface needs to know about
typedef struct {
	float	wavelength;
	int		intensity;
	int		order;
	float	lineWidth;
	float	lineHeight;
	int		error;
	float	initialX;
	float	initialY;
	float	measuredX;
	float	measuredY;
	float	calculatedX;
	float	calculatedY;
	float	residualX;
	float	residualY;

} CalibrationData;
typedef struct {
	int order;
	float intensity;
	float wavelength;
} SpectralData;

#ifdef __cplusplus
extern "C" {
#endif

unsigned int DLL_DEF MechelleInit(int width,int height,char * directory,int *MaxArraySize);

unsigned int DLL_DEF MechelleShutdown(void);

unsigned int DLL_DEF MechelleCalibrate(const char* wclFileName,int *searchArea,
                                int * imagePtr,CalibrationData * calibrationResults,
                                int * found_lines);

unsigned int DLL_DEF MechelleSaveCalibration(float *newTemperature);

unsigned int DLL_DEF MechelleGenerateSpectrum(int * imagePtr, SpectralData *Spectrum,
                                  int *SpectrumLength,double * calibCoefs);

unsigned int DLL_DEF MechelleSpectrumMaxArraySize(int *maxarraysize);

unsigned int DLL_DEF MechelleImageTemperatureAdjust(int *Image,float *currentTemp, int *pPixelAdjustX,int *pPixelAdjustY);

unsigned int DLL_DEF MechelleGetSavedCalibrationTemperature(float *calTemp);

unsigned int DLL_DEF MechelleGetInternalTemperature(float *calTemp);
unsigned int DLL_DEF MechelleBackupCalibration(void);
unsigned int DLL_DEF MechelleRestoreCalibration(void);


#ifdef __cplusplus
}
#endif

#endif