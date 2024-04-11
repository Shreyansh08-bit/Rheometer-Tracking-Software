import customTkinter

# Create an instance of CustomTkinter
app = customTkinter()

# Define the recording icon image path
recording_icon_path = "recording_icon.png"

# Create a label widget to display the recording icon
recording_icon_label = app.create_label(image=recording_icon_path)
recording_icon_label.pack()

# Function to update the recording icon visibility
def update_recording_icon():
    if recording_flag:
        recording_icon_label.configure(state="normal")
    else:
        recording_icon_label.destroy()

# Call the update_recording_icon function periodically
app.after(100, update_recording_icon)

# Start the main loop of the CustomTkinter application
app.mainloop()
