
import java.awt.TextField;
import java.util.Vector;

import ij.*;
import ij.io.*;
import ij.gui.*;
import ij.plugin.PlugIn;
import com.andor.ATSIF.IO.*;
import com.andor.ATSIF.consts.*;

public class Read_SIF implements PlugIn {

  public void run(String arg) {
    String str_FileName = "";
  	String str_Directory = "";
		
    OpenDialog OpenDlg = new OpenDialog("Open SIF ...", arg);
    str_FileName = OpenDlg.getFileName();
    str_Directory = OpenDlg.getDirectory();
		
    if (str_FileName == null) {
      return;
    }
		
    int noImages[] = new int[1];
    noImages[0] = 0;
    ImagePlus MyImage[] = DisplaySIF(str_Directory, str_FileName, noImages);
    if (noImages[0] > 0) {
      for(int i = 0; i < noImages[0]; ++i) {
        if(MyImage[i] != null) {
          MyImage[i].show();	
			  }
      }
    }
    else {
      IJ.showMessage("Open SPE...", "Failed.");
		}
	}
	
  public static ImagePlus[] DisplaySIF(String str_Directory, String str_FileName, int noImages[]) {
    ImagePlus displayImage[] = new ImagePlus[10];
    int noSources = 0;
    ATSIFIO sio = new ATSIFIO();
		
    if (sio.SetFileAccessMode(ATSIF_ReadMode.ATSIF_ReadAll) == ATSIF_Status.ATSIF_SUCCESS) {		
      String imageFile = str_Directory + str_FileName;
      int rc = sio.ReadFromFile(imageFile);
      if(rc == ATSIF_Status.ATSIF_SUCCESS) {		
        //Check which signals are present and then add to the imagePlus array
        //Check which signals are present and then add to the imagePlus array
		    for(int i = ATSIF_DataSource.ATSIF_Signal; i < (ATSIF_DataSource.ATSIF_Source); ++i) {
          int present[] = new int[1];
          present[0] = 0;
          if(sio.IsDataSourcePresent(i, present) == ATSIF_Status.ATSIF_SUCCESS) {
            if(present[0] > 0) {
              ImagePlus image = populateImage(i, sio);
              if(image != null){
                displayImage[noSources++] = image;
              }
            }
          }
        }
		    sio.CloseFile();
      }
      else if (rc == ATSIF_Status.ATSIF_SIF_FORMAT_ERROR) {
        String msg = "Could not open SIF.\n";
        MessageDialog msgDlg = new MessageDialog(null,"File Access Error!","Could not open Sif.\nAre using the latest ATSIFIO library?\n");
      }
    }
    noImages[0] = noSources;
    return displayImage;
  }
	
  public static ImagePlus populateImage(int datasource, ATSIFIO sio) {
    ImagePlus image = null;
    String str_dataSource = "";
    switch(datasource){
      case(ATSIF_DataSource.ATSIF_Signal):
        str_dataSource = "Signal ";
        break;
      case(ATSIF_DataSource.ATSIF_Reference):
        str_dataSource = "Reference ";
        break;
      case(ATSIF_DataSource.ATSIF_Background):
        str_dataSource = "Background ";
        break;
      case(ATSIF_DataSource.ATSIF_Live):
        str_dataSource = "Live";
        break;
      case(ATSIF_DataSource.ATSIF_Source):
        str_dataSource = "Source ";
        break;
      default:
        str_dataSource = "Unknown ";
        break;
    }
    int frameSize[] = new int[1];
    frameSize[0] = 0;
    if (sio.GetFrameSize(datasource, frameSize)== ATSIF_Status.ATSIF_SUCCESS) {
      int subImages[] = new int[1];
      subImages[0] = 0;
      if(sio.GetNumberSubImages(datasource, subImages) == ATSIF_Status.ATSIF_SUCCESS){
        int left[] = new int[subImages[0]];
        int right[] = new int[subImages[0]];
        int bottom[] = new int[subImages[0]];
        int top[] = new int[subImages[0]];
        int vBin[] = new int[subImages[0]];
        int hBin[] = new int[subImages[0]];
				
        int temp_left[] = new int[1];
        temp_left[0] = (0);
        int temp_right[] = new int[1]; 
        temp_right[0] = (0);
        int temp_bottom[] =new int[1]; 
        temp_bottom[0] = (0);
        int temp_top[] = new int[1];
        temp_top[0] = (0) ;
        int temp_hBin[] = new int[1];
        temp_hBin[0] = (0);
        int temp_vBin[] = new int[1];
        temp_vBin[0] = (0);
        
        for(int i = 0; i < subImages[0]; ++i ) {
          sio.GetSubImageInfo(datasource, i, temp_left, temp_bottom, temp_right, temp_top, temp_hBin, temp_vBin);
          left[i] = temp_left[0];	
          right[i] = temp_right[0];
          bottom[i] = temp_bottom[0];
          top[i] = temp_top[0];
          vBin[i] = temp_vBin[0];
          hBin[i] = temp_hBin[0];
        }
        int width = 1 + right[0] - left[0];
        String propertyValue[] = new String[1];
        propertyValue[0] = "";
        sio.GetPropertyValue(datasource,"DetectorFormatZ", propertyValue);
        int height = Integer.parseInt(propertyValue[0].toString());
        
        if(height == 1) {
          height = width;
        }
        ImageStack kSeries = new ImageStack(width, height);
        int noFrames[] = new int[1];
        noFrames[0] = 0;	
        if ( sio.GetNumberFrames(datasource, noFrames) == ATSIF_Status.ATSIF_SUCCESS) {
          boolean validRange = false;
          int firstFrame = 1;
          int lastFrame = noFrames[0];
          int count = 0;
          while(!validRange) {  
            long maxMem = IJ.maxMemory();
            long currMem = IJ.currentMemory();
            String str_title = "Choose " + str_dataSource + " Subset";
            GenericDialog gd = new GenericDialog(str_title);
            long maxNoFrames = noFrames[0];
            if(count > 0) {
              gd.addMessage("INVALID RANGE");
            }
            if(maxMem > 0) {
              if((noFrames[0]*frameSize[0]*4) > (maxMem-currMem)) {
                maxNoFrames = (maxMem - currMem)/(frameSize[0]*4);
                String msg = "Enough Memory to open " + maxNoFrames + " images.";
                gd.addMessage(msg);
              }	  
            }
            String str_fieldTxt = "First Frame (min " + firstFrame + "):";
            gd.addStringField(str_fieldTxt,""+1);
            str_fieldTxt = " Last Frame (max " + noFrames[0] + "):";
            gd.addStringField(str_fieldTxt, ""+noFrames[0]);
            if(noFrames[0] == 1) {
              validRange = true;
              break;
            }
            gd.showDialog();
            if(gd.wasCanceled()) {
              break;
            }
            Vector fields;
            fields = gd.getStringFields();
            firstFrame = Integer.parseInt(((TextField)fields.elementAt(0)).getText());
            lastFrame = Integer.parseInt(((TextField)fields.elementAt(1)).getText());

            if((firstFrame > 0) 
                && (firstFrame <= lastFrame)
                && (lastFrame <= noFrames[0])
                && ((lastFrame - firstFrame  + 1) <= maxNoFrames)) {
              validRange = true;	  
            }
            ++count;
          }
          if(validRange){ 
            for(int i = firstFrame - 1; i < lastFrame; i++) {
              int detectorSize = width * height;
              float detectorBuffer[] = new float[detectorSize];
              int noPixels = frameSize[0];
              float imageBuffer[] = new float[noPixels];
              if(sio.GetFrame(datasource, i, imageBuffer, noPixels) == ATSIF_Status.ATSIF_SUCCESS) {
                int bufferPos = 0;
                for(int j = 0; j < subImages[0]; ++j){
                  int p = bottom[j] - 1;
                  while(p< top[j]){
                    for(int k = 0; k < vBin[j]; ++k){
                      if(k != 0){
                        bufferPos -= (width / hBin[j]);
                      }
                      for(int l = 0; l < width;) {
                        for(int m = 0; m < hBin[j];++m) {
                          int detectorPos = (width * p) + l++;
                          detectorBuffer[detectorPos] = imageBuffer[bufferPos];
                        }	
                        bufferPos++;
                      }
                      ++p;
                    }
                  }
                }
              }
              kSeries.addSlice(str_dataSource + i, detectorBuffer);
              IJ.showProgress(i, lastFrame);
            }
            propertyValue[0] = "";
            sio.GetPropertyValue(datasource,"ReadPatternFullName", propertyValue);
            String imageName = str_dataSource + " - " + propertyValue[0];
            if ( noFrames[0] > 1 ) {
              imageName += " Series";	
            }
            image = new ImagePlus(imageName, kSeries);
          }
			  }
      }
    }
    return image;
  }
	
  public static void main(String[] args)  {
    Read_SIF rs = new Read_SIF();
    rs.run("");
  }
}
