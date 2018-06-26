unit atmechelle;

interface

const
    MECHELLE_ERROR_CODES =	20001;
    MECHELLE_SUCCESS =	20002;
    MECHELLE_NOTINITIALIZED =	20003;
    MECHELLE_DLLNOTFOUND = 21000;
    MECHELLE_ATMCD32DLLNOTFOUND = 21001;
    MECHELLE_TEMPERATUREERROR = 21002;
    MECHELLE_NOTEMPERATUREDIFFERENCE = 21003;

    function  MechelleInit(width: Integer;height: Integer;directory: PChar;var MaxArraySize: Integer): integer; stdcall;
    function  MechelleShutdown: integer; stdcall;
    function  MechelleCalibrate(wclFileName: PChar;var searchArea: Integer;var imagePtr: Integer; calibrationResults: Pointer;var found_lines: Integer): integer; stdcall;
    function MechelleSaveCalibration(var newTemperature: Single): integer; stdcall;
    function MechelleGenerateSpectrum(var imagePtr: Integer; Spectrum: Pointer;var SpectrumLength: Integer ;var calibCoefs: Double ): integer; stdcall;
    function MechelleSpectrumMaxArraySize(var maxarraysize: Integer): integer; stdcall;
    function MechelleImageTemperatureAdjust(var Image: Integer;var currentTemp: Single; var pPixelAdjustX: Integer; var pPixelAdjustY: Integer): integer; stdcall;
    function MechelleGetSavedCalibrationTemperature(var calTemp: Single): integer; stdcall;
    function MechelleGetInternalTemperature(var calTemp: Single): integer; stdcall;
    function MechelleBackupCalibration: integer; stdcall;
    function MechelleRestoreCalibration: integer; stdcall;
        
implementation

    function MechelleInit; external 'atmechelle.dll' name 'MechelleInit';
    function MechelleShutdown; external 'atmechelle.dll' name 'MechelleShutdown';
    function MechelleCalibrate; external 'atmechelle.dll' name 'MechelleCalibrate';
    function MechelleSaveCalibration; external 'atmechelle.dll' name 'MechelleSaveCalibration';
    function MechelleGenerateSpectrum; external 'atmechelle.dll' name 'MechelleGenerateSpectrum';
    function MechelleSpectrumMaxArraySize; external 'atmechelle.dll' name 'MechelleSpectrumMaxArraySize';
    function MechelleImageTemperatureAdjust; external 'atmechelle.dll' name 'MechelleImageTemperatureAdjust';
    function MechelleGetSavedCalibrationTemperature; external 'atmechelle.dll' name 'MechelleGetSavedCalibrationTemperature';
    function MechelleGetInternalTemperature; external 'atmechelle.dll' name 'MechelleGetInternalTemperature';
    function MechelleBackupCalibrationexternal 'atmechelle.dll' name 'MechelleBackupCalibrationexternal' 
    function MechelleRestoreCalibrationexternal 'atmechelle.dll' name 'MechelleRestoreCalibrationexternal' 

end.


