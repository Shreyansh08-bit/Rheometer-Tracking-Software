import customtkinter
from PIL import Image, ImageTk
import cv2

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

cap = cv2.VideoCapture(0)

class TimeIn(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        
        self.title("Time In")
        
        # =================== Center Form =================== #
        window_height = 800
        window_width = 1000

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/3) - (window_height/3))
        
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
         
        
        # =================== Mainframe =================== #
        self.mainFrame = customtkinter.CTkFrame(master=self)
        self.mainFrame.pack(pady=15, padx=15, fill="both", expand=True)

        
        # =================== set row and column =================== #
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # =================== Camera Streaming =================== #
        self.cameraFrame = customtkinter.CTkFrame(master=self.mainFrame, width=950 )
        self.cameraFrame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        
        self.camera = customtkinter.CTkLabel(self.cameraFrame)
        self.camera.grid()


        # self.camera.configure(image=)
    
    # code for video streaming
    def streaming(self):
        ret, img = cap.read()
        cv2image= cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        ImgTks = ImageTk.PhotoImage(image=img)
        self.camera.imgtk = ImgTks
        self.camera.configure(image=ImgTks)
        self.after(20, self.streaming)


if __name__ == "__main__":
    app = TimeIn()
    app.streaming()
    app.mainloop()
    
