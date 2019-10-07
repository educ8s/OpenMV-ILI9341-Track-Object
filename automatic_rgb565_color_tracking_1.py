# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking using the OpenMV Cam.

import sensor, image, time
from machine import SPI
from OpenMV_TFT import TFT
print("Letting auto algorithms run. Don't put anything in front of the camera!")

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

spi = SPI(2, baudrate=54000000) #create an SPI bus1

screen = TFT(spi, TFT.ili9341)

#set window on screen to write to (x_start, Y_start, width, height)
#the window needs to be inside the resolution of the screen and must match the exact size of fb
screen.set_window(0,0,320,240)


# Capture the color thresholds for whatever was in the center of the image.
r = [(320//2)-(50//2), (240//2)-(50//2), 50, 50] # 50x50 center of QVGA.

print("Auto algorithms done. Hold the object you want to track in front of the camera in the box.")
print("MAKE SURE THE COLOR OF THE OBJECT YOU WANT TO TRACK IS FULLY ENCLOSED BY THE BOX!")
for i in range(60):
    img = sensor.snapshot()
    img.rotation_corr(z_rotation=90, zoom = 1.28 )
    img.draw_rectangle(r)
    screen.write_to_screen(img) #send the fb to the screen


print("Learning thresholds...")
threshold = [50, 50, 0, 0, 0, 0] # Middle L, A, B values.
for i in range(60):
    img = sensor.snapshot()
    img.rotation_corr(z_rotation=90, zoom = 1.28 )
    hist = img.get_histogram(roi=r)
    lo = hist.get_percentile(0.01) # Get the CDF of the histogram at the 1% range (ADJUST AS NECESSARY)!
    hi = hist.get_percentile(0.99) # Get the CDF of the histogram at the 99% range (ADJUST AS NECESSARY)!
    # Average in percentile values.
    threshold[0] = (threshold[0] + lo.l_value()) // 2
    threshold[1] = (threshold[1] + hi.l_value()) // 2
    threshold[2] = (threshold[2] + lo.a_value()) // 2
    threshold[3] = (threshold[3] + hi.a_value()) // 2
    threshold[4] = (threshold[4] + lo.b_value()) // 2
    threshold[5] = (threshold[5] + hi.b_value()) // 2
    for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        img.draw_rectangle(r)
        screen.write_to_screen(img) #send the fb to the screen

print("Thresholds learned...")
print("Tracking colors...")

while(True):
    clock.tick()
    fps =clock.fps()
    img = sensor.snapshot()
    img.rotation_corr(z_rotation=90, zoom = 1.28 )
    for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    img.draw_string(7,2, ("%2.1ffps" %(fps)), color=(255,255,255), scale=2, string_rotation = 0)
    screen.write_to_screen(img) #send the fb to the screen

    print(clock.fps())
