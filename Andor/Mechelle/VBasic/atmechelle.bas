Attribute VB_Name = "Module3"

Type CalibrationData
      wavelength As Single
      intensity As Long
      order As Long
      lineWidth As Single
      lineHeight As Single
      error As Long
      initialX As Single
      initialY As Single
      measuredX As Single
      measuredY As Single
      calculatedX As Single
      calculatedY As Single
      residualX As Single
      residualY As Single
End Type

Type SpectralData
        order As Long
        intensity As Single
        wavelength As Single
End Type

Global Const DRV_ERROR_CODES = 20001
Global Const MECHELLE_ERROR_CODES = 20001
Global Const MECHELLE_SUCCESS = 20002
Global Const MECHELLE_NOTINITIALIZED = 20003
Global Const MECHELLE_DLLNOTFOUND = 21000
Global Const MECHELLE_ATMCD32DLLNOTFOUND = 21001
Global Const MECHELLE_TEMPERATUREERROR = 21002
Global Const MECHELLE_NOTEMPERATUREDIFFERENCE = 21003

Declare Function MechelleInit Lib "atmechelle.dll" (ByVal width As Long, ByVal height As Long, ByVal directory As String, MaxArraySize As Long) As Long
Declare Function MechelleShutdown Lib "atmechelle.dll" () As Long
Declare Function MechelleCalibrate Lib "atmechelle.dll" (ByVal wclFileName As String, searchArea As Long, imagePtr As Long, calibrationResults As CalibrationData, found_lines As Long) As Long
Declare Function MechelleSaveCalibration Lib "atmechelle.dll" (newTemperature As Single) As Long
Declare Function MechelleGenerateSpectrum Lib "atmechelle.dll" (imagePtr As Long, Spectrum As SpectralData, SpectrumLength As Long, calibCoefs As Double) As Long
Declare Function MechelleSpectrumMaxArraySize Lib "atmechelle.dll" (MaxArraySize As Long) As Long
Declare Function MechelleImageTemperatureAdjust Lib "atmechelle.dll" (Image As Long, currentTemp As Single, pPixelAdjustX As Long, pPixelAdjustY As Long) As Long
Declare Function MechelleGetSavedCalibrationTemperature Lib "atmechelle.dll" (calTemp As Single) As Long
Declare Function MechelleGetInternalTemperature Lib "atmechelle.dll" (calTemp As Single) As Long
Declare Function MechelleBackupCalibration Lib "atmechelle.dll" () As Long
Declare Function MechelleRestoreCalibration Lib "atmechelle.dll" () As Long
