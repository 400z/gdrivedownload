import pygame
import time
import os
import subprocess
import threading
import RPi.GPIO as GPIO
import datetime



# Initialize Pygame
pygame.init()

#setup
def image_setup():
	global folder_path, file_prefix, files, screen_width, screen_height, screen, directory, count, images
	#checks continuous png files
	### 
	folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "church dashboard pictures")
	file_prefix = "1"
	files = os.listdir(folder_path)
	# sort files in ascending order based on numerical values in the file names
	files.sort(key=lambda f: int(os.path.splitext(f)[0]))
	# check if file_prefix exists in the folder
	if any([f.startswith(file_prefix) for f in files]):
		i = next(i for i, f in enumerate(files) if f.startswith(file_prefix))
		# find longest continuous sequence
		count = 1
		for j in range(i+1, len(files)):
			if files[j].startswith(str(int(file_prefix)+count) + ".png"):
				count += 1
			else:
				break
		if count > 1:
			print("There are {} continuous png files".format(count))
		else:
			print("There is only one png file")
	else:
		print("{}.png does not exist in {}".format(file_prefix, folder_path))
		pygame.quit()
	print (count)
	###

	# Define the dimensions of the screen
	screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
	screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

	#open the church dashboard picture folder
	directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "church dashboard pictures")
	# Load the images
	images = []
	for i in range(1, count+1):
		image_path = os.path.join(directory, f"{i}.png")
		image = pygame.image.load(image_path).convert()
		images.append(image)

#run setup
image_setup()


###constant variables

#hide mouse cursor
pygame.mouse.set_visible(False)
#password
font = pygame.font.SysFont(None, 32)
password = "123"
max_password_length = 8
# Set the window title
pygame.display.set_caption("Slideshow")
# Define some variables for timing
slide_duration = 15  # seconds
black_screen_duration = 5  # seconds
current_slide = 0
last_slide_change_time = time.time()
#setup gpio
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)



def get_network_status_code():
	# Define the IP address to ping (in this case, Google's DNS server)
	ip_address = "8.8.8.8"

	# Run the ping command and capture the output
	ping_output = subprocess.run(['ping', '-c', '1', ip_address], stdout=subprocess.PIPE)
	
	global network_status_code
	network_status_code = ping_output.returncode

def network_led1():
	global running
	running = True
	while running:
		get_network_status_code()
		if network_status_code == 0:
			print ("there is network connection")
			GPIO.output(14, GPIO.HIGH)
			time.sleep(10)
			GPIO.output(14, GPIO.LOW)
			time.sleep(0.1)
		else:
			GPIO.output(14, GPIO.LOW)
			time.sleep(10)

def run_download():
	subprocess.run(["python", "download.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
	
def run_emptyfolder():
	subprocess.run(["python", "emptyfolder.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
	
def downloading_screen():
	default_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rdefault/d1.png")
	image_d1 = pygame.image.load(default_image_path)
	# get the image width and height
	image_d1_width = image_d1.get_width()
	image_d1_height = image_d1.get_height()
	# scale the image to fit the width of the display
	scale_factor_d1 = screen.get_width() / image_d1_width
	scaled_image_width_d1 = int(image_d1_width * scale_factor_d1)
	scaled_image_height_d1 = int(image_d1_height * scale_factor_d1)
	scaled_image_d1 = pygame.transform.smoothscale(image_d1, (scaled_image_width_d1, scaled_image_height_d1))
	# calculate the gaps on the top and bottom
	gap = (screen.get_height() - scaled_image_height_d1) // 2
	# display the image for 5 seconds
	screen.fill((0, 0, 0))
	screen.blit(scaled_image_d1, (0, gap))
	pygame.display.update()
	
def download_message():
	# Set up font for message
	font = pygame.font.SysFont(None, 72)
	screen.fill((0, 200, 100))
	text_surface = font.render("Download finished", True, (255, 255, 255))
	text_x = (screen.get_width() - text_surface.get_width()) // 2
	text_y = (screen.get_height() - text_surface.get_height()) // 2
	screen.blit(text_surface, (text_x, text_y))
	pygame.display.flip()

def download_error_message():
	# Set up font for message
	font = pygame.font.SysFont(None, 72)
	screen.fill((170, 0, 0))
	text_surface = font.render("Download unsuccessful :(", True, (255, 255, 255))
	text_x = (screen.get_width() - text_surface.get_width()) // 2
	text_y = (screen.get_height() - text_surface.get_height()) // 2
	screen.blit(text_surface, (text_x, text_y))
	pygame.display.flip()

def check_1png():
	# Get the absolute path of the folder containing the Python script
	folder_path = os.path.dirname(os.path.abspath(__file__))
	global exists
	# Check if the file "1.png" exists in the "new" folder
	if os.path.exists(os.path.join(folder_path, "church dashboard pictures", "1.png")):
		print("The file exists!")
		exists = 1
	else:
		print("The file does not exist.")
		exists = 0
def download_sequence():
	screen.fill((0, 50, 200))
	pygame.display.flip()
	pygame.time.delay(1000)
	screen.fill((0, 255, 255))
	pygame.display.flip()
	pygame.time.delay(1000)
                
	#check for internet
	get_network_status_code()
	if network_status_code != 0:
		print("there no network connection")
		screen.fill((255, 0, 0))
		pygame.display.update()
		pygame.time.delay(2000)
	else:
		print("there is network connection")
		screen.fill((0, 255, 0))
		pygame.display.update()
		pygame.time.delay(2000)
                
		#run download
		downloading_screen()
		run_emptyfolder()
		time.sleep(1)
		run_download()
		time.sleep(1)
                    
		# download success
		check_1png()
		if exists == 0 :
			print("download unsuccessful")
			download_error_message()
			time.sleep(5)
			pygame.quit()
		else:
                        print("download success")
                        download_message()
                        time.sleep(2)
                        
			#run setup again
                        image_setup()	


#start Led thread
t = threading.Thread(target=network_led1)
t.start()	
#calibrating last_download_time
last_download_time = datetime.datetime.now() - datetime.timedelta(weeks = 1)

# Main game loop

running = True
while running:
    # Handle events
    
    #auto 
    now = datetime.datetime.now()
    hours_difference = (now - last_download_time).total_seconds()/3600
    if now.weekday() == 4 and now.hour == 19 and hours_difference > 24 :
        last_download_time = datetime.datetime.now()
        screen.fill((50, 50, 200))
        pygame.display.flip()
        pygame.time.delay(1000)
        download_sequence()
        #print(hours_difference," ",last_download_time)
        #print (" run download script")

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_6:
                # Quit the program
                running = False

            elif event.key == pygame.K_5:
                input_password = ""
                start_time = pygame.time.get_ticks()
                while True:
                    event = pygame.event.poll()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if input_password == password:
                                running = False
                                break
                            else:
                                input_password = ""
                        elif event.key == pygame.K_BACKSPACE:
                            input_password = input_password[:-1]
                        elif event.unicode.isalnum() and len(input_password) < max_password_length:
                            input_password += event.unicode
                        password_surface = font.render("Enter password:", True, (255, 255, 255))
                        password_input_surface = font.render("*" * len(input_password), True, (255, 255, 255))
                        screen.fill((0, 0, 0))
                        screen.blit(password_surface, password_surface.get_rect(center=screen.get_rect().center))
                        screen.blit(password_input_surface, password_input_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50)))
                        pygame.display.flip()
                    elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
                        break
                    current_time = pygame.time.get_ticks()
                    if (current_time - start_time) > 15000: # time limit reached
                        break
                if input_password != password: # password not entered in time
                    continue
            elif event.type == pygame.QUIT: #or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break
            
            elif event.key == pygame.K_7:
                os.system("sudo shutdown -h now")
            
            elif event.key == pygame.K_8:
                os.system("sudo reboot -h now")
			
            elif event.key == pygame.K_9:
                download_sequence()




    # Calculate the time since the last slide change
    time_since_last_slide_change = time.time() - last_slide_change_time

    # Check if it's time to change to the next slide
    if time_since_last_slide_change > slide_duration:
        current_slide += 1
        if current_slide >= len(images):
            current_slide = 0
        last_slide_change_time = time.time()

    # Draw the current slide
    image = images[current_slide]
    image_width, image_height = image.get_size()
    aspect_ratio = image_width / image_height
    scaled_width = int(screen_height * aspect_ratio)
    scaled_height = screen_height
    scaled_image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))
    screen.fill((0, 0, 0))
    screen.blit(scaled_image, ((screen_width - scaled_width) // 2, 0))

    # Update the display
    pygame.display.flip()

pygame.quit()
GPIO.output(14, GPIO.LOW)
t.join()
GPIO.cleanup()	

