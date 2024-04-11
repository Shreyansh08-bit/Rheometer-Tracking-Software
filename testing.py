from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_ushort
from math import pi, sin, cos
from time import sleep

import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import ttk, Tk 
from SpinBox import FloatSpinbox
import os
import PIL
import numpy as np

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status, ULRange
from mcculw.device_info import DaqDeviceInfo
 
try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device
    
import datetime
import cv2
from tkinter import filedialog
import threading

from PIL import Image,ImageTk,ImageEnhance
import time
angleOld=0
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
opacity=0

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# Create some random colors
color = np.random.randint(0, 255, (100, 3))

coordinates = []
OrigFrame_Flag=True
DiffFrame_Flag=False 
Fading_Flag=True
DAqCOnfigured_Flag=False
MotionFrame_Flag=False 
GrayFrame_Flag=False
selected_camera_index=0

recording_Flag=False
Executing_Flag=False
Camera_Flag=True
Playing_Flag=True
BackGroundSubtractorMOG2_Flag=False
Pause_Flag=False
VideoUpload_Flag=False
current_frame=0
ReplayErrorFlag=False
AutomaticallySaving_Flag=False
CustomSaving_FLag=True
Start_StopUploadRecording_Flag=False
out1=None
out2=None
MOG2Flag=True
out3=None
k=0
out4=None
cap = cv2.VideoCapture(selected_camera_index)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Rheometer Control")
        self.geometry(f"{1250}x{580}")
        self.resizable(False, False)
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        
        validate_func = self.register(self.validate_input) 
        
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Control Pannel", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Camera",command=self.CameraSelect)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame,text="Upload A Video File" ,command=self.UploadVideoselect)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        
        
        

        
        
        #Appearance and scale function
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 10))
        
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main VideoFilePath and Uploadbutton
        self.VideoFilePath = customtkinter.CTkEntry(master=self, placeholder_text="Uploaded video file path",width=500)
        self.VideoFilePath.place(relx=0.40, rely=0.05, anchor="n")

        self.UploadButton = customtkinter.CTkButton(master=self, text="Upload Video",fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.UploadVideoExecution)
        self.UploadButton.place(relx=0.70, rely=0.05, anchor="n")
        
        
        
        #Create a play pause Restart button for Uploaded Video
        self.PlayPause = customtkinter.CTkButton(master=self, text="Play/Pause",fg_color="transparent", border_width=1, width=100,text_color=("gray10", "#DCE4EE"),command=self.PlayPauseEvent)
        self.PlayPause.place(relx=0.31, rely=0.13, anchor="n")
        self.Replay = customtkinter.CTkButton(master=self, text="Replay",fg_color="transparent", border_width=1,width=70, text_color=("gray10", "#DCE4EE"), command=self.ReplayUploadFile)
        self.Replay.place(relx=0.21, rely=0.13, anchor="n")
        
        #start and stop recording option
        self.StartRec = customtkinter.CTkButton(master=self, text="Start Recording",fg_color="transparent", border_width=1, width=120,text_color=("gray10", "#DCE4EE"),command=self.StartRecording)
        self.StartRec.place(relx=0.43, rely=0.13, anchor="n")
        self.StopRec = customtkinter.CTkButton(master=self, text="Stop Recording",fg_color="transparent", border_width=1,width=120, text_color=("gray10", "#DCE4EE"),command=self.StopRecording)
        self.StopRec.place(relx=0.56, rely=0.13, anchor="n")
        
        #Upload Start_Stop recording button
        self.Start_Stop = customtkinter.CTkButton(master=self, text="Start/Stop Upload Rec",fg_color="transparent", border_width=1,width=120, text_color=("gray10", "#DCE4EE"),command=self.Start_StopUploadRecording)
        self.Start_Stop.place(relx=0.69, rely=0.13, anchor="n")
        

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.place(relx=0.87, rely=0.05, anchor="n")
        
        #Making Amplitude and Frequency Entry
        self.Amplitude = customtkinter.CTkLabel(master=self, text="Amplitude:", anchor="w")
        self.Amplitude.place(relx=0.81, rely=0.45, anchor="n")
        self.AmplitudeEntry  = customtkinter.CTkEntry(master=self, placeholder_text="Enter the Amplitude",width=120,validate="key", validatecommand=(validate_func, '%S'))
        self.AmplitudeEntry.place(relx=0.89, rely=0.45, anchor="n")
        self.AmplitudeEntry.insert(0, float(10))
        self.ApliUnit = customtkinter.CTkOptionMenu(master=self, values=["V", "mV", "MicroV"], width=50)
        self.ApliUnit.place(relx=0.97, rely=0.45, anchor="n")
        
        self.Frequency = customtkinter.CTkLabel(master=self, text="Frequency:", anchor="w")
        self.Frequency.place(relx=0.81, rely=0.52, anchor="n")
        self.FrequencyEntry  = customtkinter.CTkEntry(master=self, placeholder_text="Enter the Frequency",width=120,validate="key", validatecommand=(validate_func, '%S'))
        self.FrequencyEntry.place(relx=0.89, rely=0.52, anchor="n")
        self.FrequencyEntry.insert(0, float(1))
        self.FrequencyUnit = customtkinter.CTkOptionMenu(master=self, values=["Hz", "KHz", "MHz"], width=50)
        self.FrequencyUnit.place(relx=0.97, rely=0.52, anchor="n")
        
        #Start and Stop Calculations Button
        self.StartCalc = customtkinter.CTkButton(master=self, text="Initiate Calculations",fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.executeDaq)
        self.StartCalc.place(relx=0.88, rely=0.60, anchor="n")
        self.StopCalc = customtkinter.CTkButton(master=self, text="Stop Calculations",fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.StopExecutingDaq)
        self.StopCalc.place(relx=0.88, rely=0.67, anchor="n")
        
        
        #Configuring DAq and Releasing Daq
        self.ConfigDaq = customtkinter.CTkButton(master=self, text="ConfigureDAQ",fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.ConfigureDaqDevice)
        self.ConfigDaq.place(relx=0.67, rely=0.25, anchor="n")
        self.ReleaseDaq = customtkinter.CTkButton(master=self, text="ReleaseDAQ",fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),command=self.ReleaseDaq)
        self.ReleaseDaq.place(relx=0.67, rely=0.32, anchor="n")
        
        
        #Changing Between Image to show on the screen
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.place(relx=0.67, rely=0.42, anchor="n")
        self.radiobutton_frame.configure(width=200, height=300)
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Image Frame")
        self.label_radio_group.place(relx=0.5, rely=0.1, anchor="center")
        self.Original_Frame = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0,text="Original Frame",command=self.OrigFrameDisplay)
        self.Original_Frame.place(relx=0.45, rely=0.2, anchor="center")
        self.Motion_Frame = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1,text="Motion Frame",command=self.MotionFrameDisplay)
        self.Motion_Frame.place(relx=0.435, rely=0.35, anchor="center")
        self.Difference_Frame = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2,text="Difference Frame",command=self.DiffFrameDisplay)
        self.Difference_Frame.place(relx=0.48, rely=0.5, anchor="center")
        self.Grayscale_Frame = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=3,text="GrayScale Frame",command=self.GrayFrameDisplay)
        self.Grayscale_Frame.place(relx=0.48, rely=0.65, anchor="center")
        self.BackGroundSubtractorMOG2_Frame = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=4,text=" Background Subtractor Frame",command=self.BackGroundSubtractorMOG2Display)
        self.BackGroundSubtractorMOG2_Frame.place(relx=0.48, rely=0.8, anchor="center")
        
        

        switch = customtkinter.CTkSwitch(self.sidebar_frame, text=f"Save Automatically",command=self.FileSaving_Flag)
        switch.place(relx=0.5, rely=0.5, anchor="center")
        
        switchMOG_KNN = customtkinter.CTkSwitch(self, text=f"MOG2/KNN",command=self.MOG2KNNswitch)
        switchMOG_KNN.place(relx=0.66, rely=0.95, anchor="center")
        
        #Setting the defualt values for widgets
        
        self.PlayPause.configure(state="disabled")
        self.Replay.configure(state="disabled")    
        self.StartRec.configure(state="enabled")  
        self.StopRec.configure(state="disabled")      
        self.StopCalc.configure(state="disabled")  
        self.UploadButton.configure(state="disabled")  
        self.Start_Stop.configure(state="disabled") 
        self.StartCalc.configure(state="disabled")
        self.ReleaseDaq.configure(state="disabled")
        self.ConfigDaq.configure(state="enabled")
        
        
        self.cameraFrame = customtkinter.CTkFrame(master=self, width=950 )
        self.cameraFrame.place(relx=0.37, rely=0.57, anchor="center")
        
        self.camera = customtkinter.CTkLabel(self.cameraFrame,text="")
        self.camera.grid() 
        
        self.recording_icon_label = customtkinter.CTkLabel(self,text="")
        self.recording_icon_label.place(relx=0.18, rely=0.9, anchor="n")
        
        #Creating a Camera Change Combobox
        selected_camera_index=0
        self.CameraIndex_label = customtkinter.CTkLabel(self.sidebar_frame, text="Camera Index:", anchor="w")
        self.CameraIndex_label.place(relx=0.50, rely=0.34, anchor="n")
        self.spinbox_1 = FloatSpinbox(self.sidebar_frame, width=150, step_size=1)
        self.spinbox_1.place(relx=0.50, rely=0.39, anchor="n")
        self.spinbox_1.set(0)
        
        
    def streaming(self):
        global current_frame, VideoUpload_Flag,ReplayErrorFlag, out1, status, out2, out3, out4, frame1,frame2, Executing_Flag, Fading_Flag,opacity, angleOld, memhandle
        frame_count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if MOG2Flag:
            backSub = cv2.createBackgroundSubtractorMOG2()
        else:
            backSub = cv2.createBackgroundSubtractorKNN()  
                         
        try:
            if Camera_Flag:
                self.change_camera()
                
            if cap:
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps >0:
                    delaytime = int(1000 / fps)  # Convert to milliseconds
                else:
                    delaytime=10
            else: 
                delaytime=10

            
            if Playing_Flag:
                if VideoUpload_Flag:
                    if frame_count != 0:
                        mapped_value = float(current_frame - 0) / (frame_count - 0) * (1 - 0) + 0
                    else:
                        mapped_value = 0.0  # Set a default value if frame_count is zero
                    self.progressbar_3.set(mapped_value) 
                    current_frame += 1
                    self.progressbar_3.update()
                    if current_frame==frame_count:
                        VideoUpload_Flag=False
                        ReplayErrorFlag=True
                        
                k=0
                if k<=1:
                    ret,frame1 = cap.read()
                    ret,frame2=cap.read()
                    
                    k=k+1
                else:
                    ret,frame2=cap.read()
                
                if ret:
                    
                    
                    
                    
                    diff=cv2.absdiff(frame1,frame2)
                    grayDisplay=cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
                    gray=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
                    
                    
                    
                    #WE ARE CONVERTING IT HERE TO FIND out1 THE CONTOURS AS IT IS 
                    #EASIER TO FIND out1 THE COUNTOURS IN GRAYSCALE MODE
                    blur=cv2.GaussianBlur(gray,(5,5),0)
                    
                    _,thresh=cv2.threshold(blur,20,255,cv2.THRESH_BINARY)
                    
                    DILATED=cv2.dilate(thresh,None,iterations=1)
                    
                    contours,_ =cv2.findContours(DILATED,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                    # cv2.drawContours(frame1,contours,-1,(0,255,0),2)
                    
                    for contour in contours:
                        if cv2.contourArea(contour)<1500:
                            continue
                        else:
                            if len(contour)>=5:
                                
                                ellipse=cv2.fitEllipse(contour)
                                center, axes, angle = ellipse
                                #AngleChange=angleOld-angle
                                #print(AngleChange)
                                #angleOld=angle
                                cv2.ellipse(frame1,ellipse, (255,0,0),1,cv2.LINE_AA)
                        # (x,y,w,h)=cv2.boundingRect(contour)
                    
                        # if cv2.contourArea(contour)<1100:
                        #     continue
                        # cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,255,0),2)
                        # cv2.putText(frame1, "Status: {}".format('Movement'),(10,20),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                    
                    fgMask = backSub.apply(gray)
                    # print(fgMask)
                    # cv2.imshow("frame2",frame1
                    #            )
                    # cv2.imshow("frame",fgMask)
                    
                    if recording_Flag : 
                        out1.write(frame1)
                        out2.write(diff)
                        out3.write(frame2)
                        out4.write(grayDisplay)
                        
                        recordingImage=cv2.imread('Recordingpng.png')
                        ResizedRecFrame=cv2.resize(recordingImage,(51,21))
                        Recimage = cv2.cvtColor(ResizedRecFrame, cv2.COLOR_BGR2RGB)
                        Recimg = Image.fromarray(Recimage)
                        
                        
                        enhancer = ImageEnhance.Brightness(Recimg)
                        if Fading_Flag:
                            
                            OpacImg = enhancer.enhance(opacity)
                            opacity=opacity+0.1
                            if opacity>=1:
                                Fading_Flag=False
                        else:
                            OpacImg = enhancer.enhance(opacity)
                            opacity=opacity-0.1
                            if opacity<=0:
                                Fading_Flag=True
                                
                        RecImgTks = ImageTk.PhotoImage(image=OpacImg)
                        self.recording_icon_label.imgtk = RecImgTks
                        self.recording_icon_label.configure(image=RecImgTks)
                    else:
                        self.recording_icon_label.imgtk = None
                        self.recording_icon_label.configure(image=None)
                    
                    
                    if OrigFrame_Flag==True and DiffFrame_Flag==False and MotionFrame_Flag==False and GrayFrame_Flag==False and BackGroundSubtractorMOG2_Flag==False:
                        DisplayFrame=frame2
                    elif OrigFrame_Flag==False and DiffFrame_Flag==True and MotionFrame_Flag==False and GrayFrame_Flag==False and BackGroundSubtractorMOG2_Flag==False:
                        DisplayFrame=diff
                    elif OrigFrame_Flag==False and DiffFrame_Flag==False and MotionFrame_Flag==True and GrayFrame_Flag==False and BackGroundSubtractorMOG2_Flag==False:
                        DisplayFrame=frame1
                    elif OrigFrame_Flag==False and DiffFrame_Flag==False and MotionFrame_Flag==False and GrayFrame_Flag==True and BackGroundSubtractorMOG2_Flag==False:
                        DisplayFrame=grayDisplay
                    elif OrigFrame_Flag==False and DiffFrame_Flag==False and MotionFrame_Flag==False and GrayFrame_Flag==False and BackGroundSubtractorMOG2_Flag==True:
                        DisplayFrame=fgMask
                    
    
                    
                    desired_width = 640
                    desired_height = 480
                    
                    resized_frame = cv2.resize(DisplayFrame, (desired_width, desired_height))
                    # Convert the resized frame to RGB color space
                    cv2image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    
                    img = Image.fromarray(cv2image)
                    ImgTks = ImageTk.PhotoImage(image=img)
                    self.camera.imgtk = ImgTks
                    self.camera.configure(image=ImgTks)
                    frame1=frame2
        finally:
           
            if DAqCOnfigured_Flag:
                
                status, _, _ = ul.get_status(board_num, FunctionType.AOFUNCTION)
                print(status, Executing_Flag)
                if Executing_Flag and status==Status.IDLE:
                    print('capturing123456')
                    self.run_example()
            # print('DAqCOnfigured_Flag is ', DAqCOnfigured_Flag)
            # print("Executing Flag is ", Executing_Flag)
            
            self.after(delaytime, self.streaming)
    
    def change_camera(self):
        global selected_camera_index, cap
        selected_camera_index_new = int(self.spinbox_1.get())
        if selected_camera_index_new == selected_camera_index:
            return 
        
        selected_camera_index = selected_camera_index_new
        
        if cap is not None:
            cap.release()
            cap = cv2.VideoCapture(selected_camera_index)
        
        if not cap.isOpened():
            tkinter.messagebox.showwarning(title="Camera Index out Of Range", message="Program couldn't find the camera. Kindly check the connections or restart the program.")
    
    def FileSaving_Flag(self):
        global AutomaticallySaving_Flag, CustomSaving_FLag
        AutomaticallySaving_Flag=not AutomaticallySaving_Flag
        CustomSaving_FLag=not CustomSaving_FLag
        
        
        
    def ReplayUploadFile(self):
        global cap, file_path,current_frame,VideoUpload_Flag
        current_frame=0
        cap.release()
        cap = cv2.VideoCapture(file_path)
        if ReplayErrorFlag:
            VideoUpload_Flag=True
            
    
        
    def PlayPauseEvent(self):
        global Playing_Flag, Pause_Flag, VideoUpload_Flag
        Playing_Flag=not Playing_Flag
        Pause_Flag=not Pause_Flag
        VideoUpload_Flag=not VideoUpload_Flag
            
        
    #To ignore characters and only numbers are allowed
    def validate_input(self,char):
        if char.isalpha():  # checks if the character (char) is alphabetic using the isalpha() method
            return False  # Reject alphabetic characters
        return True # Accept non-alphabetic characters

    

    def UploadVideoExecution(self):
        global cap,selected_camera_index,file_path,current_frame,Playing_Flag,Pause_Flag, Camera_Flag
        UploadVideoFilePath=str(self.VideoFilePath.get())
        
        if not UploadVideoFilePath:
            cap.release()  # Release the video capture
            file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.avi;*.mp4;*.mkv")])
            if file_path:
                cap = cv2.VideoCapture(file_path)
                Playing_Flag=False
                Pause_Flag=True
                VideoUpload_Flag=True
                current_frame=0
                Camera_Flag=False
                print("Selected File:", file_path)
                self.Start_Stop.configure(state="enabled")
            else:
                tkinter.messagebox.showwarning(title="No File was Selected", message="Please select an Appropriate file")
                cap = cv2.VideoCapture(selected_camera_index)
                return
        else:
            file_path=UploadVideoFilePath
            if os.path.exists(file_path):
                # File exists, proceed with capturing the video
                cap = cv2.VideoCapture(file_path)
                Playing_Flag = False
                Pause_Flag = True
                VideoUpload_Flag = True
                current_frame=0
                Camera_Flag = False
                print("Selected File:", file_path)
                self.Start_Stop.configure(state="enabled")
            else:
                tkinter.messagebox.showwarning(title="File Not Present", message="Please Provide an Appropriate File name or upload the file. Please Remove quotation mark/double quotation marks if present")
                cap = cv2.VideoCapture(selected_camera_index)
                return
        
    def MOG2KNNswitch(self):
        global MOG2Flag
        MOG2Flag=not MOG2Flag 
            
    def BackGroundSubtraction(self):
        
        if MOG2Flag:
            backSub = cv2.createBackgroundSubtractorMOG2()
        else:
            backSub = cv2.createBackgroundSubtractorKNN()   
        fgMask = backSub.apply(frame2)
        return fgMask 

    def OrigFrameDisplay(self):
        global OrigFrame_Flag, DiffFrame_Flag, MotionFrame_Flag, GrayFrame_Flag, BackGroundSubtractorMOG2_Flag
        OrigFrame_Flag=True
        DiffFrame_Flag=False
        MotionFrame_Flag=False
        GrayFrame_Flag=False  
        
        BackGroundSubtractorMOG2_Flag=False
    def DiffFrameDisplay(self):
        global OrigFrame_Flag, DiffFrame_Flag, MotionFrame_Flag, GrayFrame_Flag, BackGroundSubtractorMOG2_Flag
        OrigFrame_Flag=False
        DiffFrame_Flag=True
        MotionFrame_Flag=False
        GrayFrame_Flag=False
       
        BackGroundSubtractorMOG2_Flag=False
    def MotionFrameDisplay(self):
        global OrigFrame_Flag, DiffFrame_Flag, MotionFrame_Flag, GrayFrame_Flag, BackGroundSubtractorMOG2_Flag
        OrigFrame_Flag=False
        DiffFrame_Flag=False
        MotionFrame_Flag=True
        GrayFrame_Flag=False
        
        BackGroundSubtractorMOG2_Flag=False
    def GrayFrameDisplay(self):
        global OrigFrame_Flag, DiffFrame_Flag, MotionFrame_Flag, GrayFrame_Flag, BackGroundSubtractorMOG2_Flag
        OrigFrame_Flag=False
        DiffFrame_Flag=False
        MotionFrame_Flag=False
        GrayFrame_Flag=True
        
        BackGroundSubtractorMOG2_Flag=False
    def BackGroundSubtractorMOG2Display(self):
        global OrigFrame_Flag, DiffFrame_Flag, MotionFrame_Flag, GrayFrame_Flag, BackGroundSubtractorMOG2_Flag
        BackGroundSubtractorMOG2_Flag=True
        
        OrigFrame_Flag=False
        DiffFrame_Flag=False
        MotionFrame_Flag=False
        GrayFrame_Flag=False
        
    
        
    
    
    def UploadVideoselect(self):
        global Camera_Flag,VideoUpload_Flag
        self.StartRec.configure(state="disabled")
        self.StopRec.configure(state="disabled")
        self.UploadButton.configure(state="enabled")
        self.StartCalc.configure(state="enabled")
        self.StopCalc.configure(state="disabled")
        self.PlayPause.configure(state="enabled")
        self.Replay.configure(state="enabled")
        self.Start_Stop.configure(state="disabled")
        #Upload Video progress Bar
        
        self.progressbar_3 = customtkinter.CTkProgressBar(self, orientation="Horizontal",width=500)
        self.progressbar_3.place(relx=0.37, rely=0.96, anchor="center")
        
        
        
            
        Camera_Flag=False
        VideoUpload_Flag=True
        
        
    def CameraSelect(self):
        global cap, selected_camera_index
        self.StartRec.configure(state="enabled")
        
        self.StopRec.configure(state="disabled")
        self.UploadButton.configure(state="disabled")
        self.StartCalc.configure(state="enabled")
        self.StopCalc.configure(state="disabled")
        self.PlayPause.configure(state="disabled")
        self.Replay.configure(state="disabled")
        self.UploadButton.configure(state="disabled")
        self.Start_Stop.configure(state="disabled")
        if cap.isOpened():
            cap.release()
            cap=cv2.VideoCapture(selected_camera_index)
            Playing_Flag=True
            Pause_Flag=False
            VideoUpload_Flag=False
            Camera_Flag=True
        
        
    def StartRecording(self):
        global recording_Flag, frame1, out1, out2, out3, out4
        
        self.StartRec.configure(state="disabled")
        self.StopRec.configure(state="enabled")
        self.UploadButton.configure(state="disabled")
        self.PlayPause.configure(state="disabled")
        self.Replay.configure(state="disabled")
        self.Start_Stop.configure(state="disabled")
        if AutomaticallySaving_Flag:
            self.saveFile()
        elif CustomSaving_FLag:
            out1,out2,out3,out4=self.customSaveFIle()
            if out1 and out2 and out3 and out4 is None:
                return
        recording_Flag=True
            
            
    def customSaveFIle(self):
        global out1,out2,out3,out4, file_name, fps, recording_Flag,frame1
        dialog = customtkinter.CTkInputDialog(text="Enter the file name:", title="Save File Name")
        file_name = dialog.get_input()
        
        if file_name:
            # Use the file name to save the file
            save_directory = filedialog.askdirectory()
            if save_directory:
                amplitude = float(self.AmplitudeEntry.get())
                frequency=float(self.FrequencyEntry.get())
                
                freqUnit=self.FrequencyUnit.get()
                ampliUnit= self.ApliUnit.get()
                folder_name = f"Rheometer_{amplitude}{ampliUnit}_{frequency}{freqUnit}"
                folder_path = os.path.join(save_directory, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Create file paths using the entered file name
                
                
                
                frame_size = (640, 480)
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                
                original_file_name=f"{file_name}_Original.avi"
                original_file_path = os.path.join(folder_path,original_file_name )
                motion_file_name=f"{file_name}_Motion.avi"
                motion_file_path = os.path.join(folder_path,motion_file_name )
                diff_file_name=f"{file_name}_Diff.avi"
                diff_file_path = os.path.join(folder_path,diff_file_name )
                gray_file_name=f"{file_name}_Gray.avi"
                gray_file_path = os.path.join(folder_path,gray_file_name )
                
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                height, width,_ = frame1.shape
                frame1_size=(width,height)
                print(frame1_size)
                fps = cap.get(cv2.CAP_PROP_FPS)

                # Create the VideoWriter object
                out1 = cv2.VideoWriter(motion_file_path, fourcc, fps, frame1_size)
                out2 = cv2.VideoWriter(diff_file_path, fourcc, fps, frame1_size)
                out3 = cv2.VideoWriter(original_file_path, fourcc, fps, frame1_size)
                out4 = cv2.VideoWriter(gray_file_path, fourcc, fps, frame1_size,isColor=False)

                
                print(out1,out2,out3,out4)
                return out1,out2,out3,out4
        else: 
            tkinter.messagebox.showwarning(title="Invalid File Name", message="Please Provide an Appropriate File name")
            recording_Flag=False
            
            self.StartRec.configure(state="enabled")
        
            self.StopRec.configure(state="disabled")
            self.UploadButton.configure(state="disabled")
            
            self.PlayPause.configure(state="disabled")
            self.Replay.configure(state="disabled")
            return
            
        
        
    def StopRecording(self):
        global recording_Flag, out1, out2, out3, out4 
        recording_Flag=False  
        self.StartRec.configure(state="enabled")
        
        self.StopRec.configure(state="disabled")
        self.UploadButton.configure(state="disabled")
        self.Start_Stop.configure(state="disabled")
        self.PlayPause.configure(state="disabled")
        self.Replay.configure(state="disabled")
        out1.release()
        out2.release()
        out3.release()
        out4.release()
        out1 = None
        out2 = None
        out3 = None
        out4 = None
              
    def Start_StopUploadRecording(self):
        global recording_Flag, out1, out2, out3, out4, Start_StopUploadRecording_Flag
        Start_StopUploadRecording_Flag= not  Start_StopUploadRecording_Flag
        if  Start_StopUploadRecording_Flag:
            if AutomaticallySaving_Flag:
                self.saveFile()
            elif CustomSaving_FLag:
                out1,out2,out3,out4=self.customSaveFIle()
                if out1 and out2 and out3 and out4 is None:
                    return
            recording_Flag=True 
        else:
            recording_Flag=False  
            self.StartRec.configure(state="disabled")
            
            self.StopRec.configure(state="disabled")
            self.UploadButton.configure(state="enabled")
            
            self.PlayPause.configure(state="enabled")
            self.Replay.configure(state="enabled")
            out1.release()
            out2.release()
            out3.release()
            out4.release()
            out1 = None
            out2 = None
            out3 = None
            out4 = None

    def Amplitude_evreertertent(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())
        
    def Amplitude_event(self):
        amplitude = float(self.AmplitudeEntry.get())
        
        ampliUnit=self.ApliUnit.get()
        if ampliUnit=="V":
            amplitude=amplitude
        elif ampliUnit=="mV":
            amplitude =amplitude/1000
        elif ampliUnit=="MicroV":
            amplitude=amplitude/1000000
        return amplitude
        
    def Frequency_Event(self):
        frequency=float(self.FrequencyEntry.get())
        
        FreqUnit=self.FrequencyUnit.get()
        if FreqUnit=="Hz":
            frequency=frequency
        elif FreqUnit=="KHz":
            frequency =frequency*1000
        elif FreqUnit=="MHz":
            frequency=frequency*1000000
        return frequency
        
        
        
    def SavingVideoFilePath(self):
        global fps

        # extracting current time and date
        current_datetime = datetime.datetime.now()
        date_folder = current_datetime.strftime("%Y-%m-%d")  # Format the date as "YYYY-MM-DD"
        time_stamp = current_datetime.strftime("%H-%M-%S")  # Format the time as "HH-MM-SS"

        # Create the date-specific folder if it doesn't exist
        folder_path = os.path.join(os.getcwd(), date_folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        additional_folder_path = os.path.join(folder_path, time_stamp)
        if not os.path.exists(additional_folder_path):
            os.makedirs(additional_folder_path)
        amplitude = float(self.AmplitudeEntry.get())
        frequency=float(self.FrequencyEntry.get())
        
        freqUnit=self.FrequencyUnit.get()
        ampliUnit= self.ApliUnit.get()
        # Generate a unique test file name
        original_file_name=f"Orig_{amplitude}{ampliUnit}_{frequency}{freqUnit}_{time_stamp}.avi"
        original_file_path=os.path.join(additional_folder_path, original_file_name)
        test_file_name = f"test_{amplitude}{ampliUnit}_{frequency}{freqUnit}_{time_stamp}.avi"
        test_file_path = os.path.join(additional_folder_path, test_file_name)
        diff_file_name=f"diff_{amplitude}{ampliUnit}_{frequency}{freqUnit}.avi"
        diff_file_path= os.path.join(additional_folder_path, diff_file_name)
        gray_file_name=f"gray_{amplitude}{ampliUnit}_{frequency}{freqUnit}_{time_stamp}.avi"
        gray_file_path=os.path.join(additional_folder_path, original_file_name)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_size = (640, 480)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Create the VideoWriter object
        out1 = cv2.VideoWriter(test_file_path, fourcc, fps, frame_size)
        out2 = cv2.VideoWriter(diff_file_path, fourcc, fps, frame_size)
        out3 = cv2.VideoWriter(original_file_path, fourcc, fps, frame_size)
        out4 = cv2.VideoWriter(gray_file_path, fourcc, fps, frame_size,isColor=False)

        

        return out1,out2,out3,out4

        


    def saveFile(self):
        global recording_Flag, out1, out2, out3, out4
        
        amplitude = float(self.AmplitudeEntry.get())
        frequency=float(self.FrequencyEntry.get())
        
        if not amplitude or not frequency:
            tkinter.messagebox.showwarning(title="Missing Values", message="Please select both frequency and amplitude values.")
            return
        
        out1, out2,out3,out4= self.SavingVideoFilePath()
        if out1 and out4 and out3 and out2 is None:
            return

        recording_Flag = True
        
        
        self.StartRec.configure(state="disabled")
        
        self.StopRec.configure(state="enabled")
        self.UploadButton.configure(state="disabled")
        self.AmplitudeEntry.configure(state="disabled")
        self.Apliunit.configure(state="disabled")
        self.FrequencyEntry.configure(state="disabled")
        self.FrequencyUnit.configure(state="disabled")
        self.PlayPause.configure(state="disabled")
        self.Replay.configure(state="disabled")
        

    
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
        
    
    def executeDaq(self):
        global Executing_Flag
        amplitude=self.Amplitude_event()
        frequency=self.Frequency_Event()
        Executing_Flag=True
        self.StopCalc.configure(state="enabled")
        self.StartCalc.configure(state="disabled")
        print(amplitude,frequency)
        
    def StopExecutingDaq(self):
        global Executing_Flag, DAqCOnfigured_Flag, memhandle, board_num
        Executing_Flag=False
        self.StartCalc.configure(state="enabled")
        self.StopCalc.configure(state="disabled")
        ul.stop_background(board_num, FunctionType.AOFUNCTION)
        if memhandle:
                # Free the buffer in a finally block to prevent a memory leak.
                ul.win_buf_free(memhandle)
                print('memhandle released')
        

        
    
        
    
    def ReleaseDaq(self):
        global memhandle,use_device_detection, board_num, Executing_Flag, DAqCOnfigured_Flag
        self.StopExecutingDaq()
        if memhandle:
            # Free the buffer in a finally block to prevent a memory leak.
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)
        DAqCOnfigured_Flag=False
        self.StartCalc.configure(state="disabled")
        self.ConfigDaq.configure(state="enabled")
        self.ReleaseDaq.configure(state="disabled")
        self.StopCalc.configure(state="disabled")
        Executing_Flag=False
            
            
    def ConfigureDaqDevice(self):
        global memhandle, board_num,dev_id_list,use_device_detection, Exception, ao_info,ao_range,low_chan,high_chan,num_chans, DAqCOnfigured_Flag
        # By default, the example detects and displays all available devices and
        # selects the first device listed. Use the dev_id_list variable to filter
        # detected devices by device ID (see UL documentation for device IDs).
        # If use_device_detection is set to False, the board_num variable needs to
        # match the desired board number configured with Instacal.
        use_device_detection = True
        dev_id_list = []
        board_num = 0
        memhandle = None

        try:
            if use_device_detection:
                config_first_detected_device(board_num, dev_id_list)

            daq_dev_info = DaqDeviceInfo(board_num)
            if not daq_dev_info.supports_analog_output:
                raise Exception('Error: The DAQ device does not support '
                                'analog output')

            print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
                  daq_dev_info.unique_id, ')\n', sep='')

            ao_info = daq_dev_info.get_ao_info()

            

            # Allocate a buffer for the scan
            self.StartCalc.configure(state="enabled")
            self.ConfigDaq.configure(state="disabled")
            self.ReleaseDaq.configure(state="enabled")
            self.StopCalc.configure(state="disabled")
            DAqCOnfigured_Flag=True
        except Exception as e:
            tkinter.messagebox.showwarning(title="DAQ Error", message=e)
            
            self.ReleaseDaq()

    def run_example(self):

        global num_chans,total_count,rate,points_per_channel,ctypes_array,board_num,memhandle, ao_range, Executing_Flag
        try:
            low_chan = 0
            high_chan = 1
            num_chans = 2
            
            ao_range = ULRange.BIP10VOLTS  #ao_info.supported_ranges[0]  #ULRange.BIP2VOLTS
            # print(ao_range)
            # print(ao_info.supported_ranges)
            #print(num_chans)
            input_freq=self.Frequency_Event()
            rate = int(input_freq)*100
            points_per_channel = 1000
            total_count = points_per_channel * num_chans

            memhandle = ul.win_buf_alloc(total_count)
            # Convert the memhandle to a ctypes array
            # Note: the ctypes array will no longer be valid after win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # before the memory is freed. The copy can be used at any time.
            ctypes_array = cast(memhandle, POINTER(c_ushort))

            # Check if the buffer was successfully allocated
            if not memhandle:
                raise Exception('Error: Failed to allocate memory') 


            frequencies = self.add_example_data(board_num, ctypes_array, ao_range,
                                            num_chans, rate, points_per_channel)

            for ch_num in range(low_chan, high_chan + 1):
                print('Channel', ch_num, 'Output Signal Frequency:',
                      frequencies[ch_num - low_chan])

            # Start the scan

            ul.a_out_scan(board_num, low_chan, high_chan, total_count, rate,
                          ao_range, memhandle, ScanOptions.BACKGROUND)
            
           # Wait for the scan to complete
            # print('Waiting for output scan to complete...', end='')
            
        except Exception as e:
            tkinter.messagebox.showwarning(title="DAQ Main Loop Error", message=e)
            
            App.ReleaseDaq()
        
                
            
        


    
        
        
    def add_example_data(self, board_num, data_array, ao_range, num_chans, rate,
                         points_per_channel):
        # Calculate frequencies that will work well with the size of the array
        frequencies = []
        
        for channel_num in range(num_chans):
            if channel_num<=0:
                 frequencies.append(
                   (channel_num + 1) / (points_per_channel / rate) * 10)
            else:
                frequencies.append(
                    (channel_num + 1) / (points_per_channel / rate) * 5)


        # Calculate an amplitude and y-offset for the signal
        # to fill the analog output range
        amplitude=self.Amplitude_event()
        
        
        #(ao_range.range_max - ao_range.range_min)/2    #
        y_offset = float(amplitude + ao_range.range_min)/2
        print(amplitude)
        #print(ao_range.range_max)
        #print(ao_range.range_min)
        #print(y_offset)



        # Fill the array with sine wave data at the calculated frequencies.
        # Note that since we are using the SCALEDATA option, the values
        # added to data_array are the actual voltage values that the device
        # will output
        data_index = 0

        for point_num in range(points_per_channel):

           for channel_num in range(num_chans):
               if channel_num==0:
                        freq = frequencies[channel_num]

                        value = amplitude * sin(2 * pi * freq * point_num / rate) + y_offset

                        raw_value = ul.from_eng_units(board_num, ao_range, value)

                        data_array[data_index] = raw_value

                        data_index += 1

               else:

                       freq = frequencies[channel_num]

                       value = amplitude * cos(2 * pi * freq * point_num / rate) + y_offset

                       raw_value = ul.from_eng_units(board_num, ao_range, value)

                       data_array[data_index] = raw_value

                       data_index += 1


        return frequencies

            
                
if __name__ == "__main__":
    app = App()
    
    app.streaming()
    
    
    app.mainloop()
    
   