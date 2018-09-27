import cv2
from PIL import Image
from PIL import ImageEnhance
import numpy as np
from time import sleep
import json
import os.path
import subprocess
from mss import mss
import keyboard

PROJECTOR_WIDTH, PROJECTOR_HEIGHT = 1024, 640
CAMERA_WIDTH, CAMERA_HEIGHT = 1280, 720
X_MARGIN, Y_MARGIN = 250, 100
NAVBAR_HEIGHT = 22
CURRENT_WINDOW = 0

WINDOW_NAME = 'output'
THRESHOLD = 230
cam = cv2.VideoCapture(0)
sct = mss()


def calibrate():

	calibration_points = []

	def click(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			# print(x,y)
			calibration_points.append((x, y))


	# print("Press any key to start the calibration process.")
	# cv2.waitKey()

	calibration_dots = [
		(X_MARGIN, Y_MARGIN),
		(PROJECTOR_WIDTH - X_MARGIN, Y_MARGIN),
		(PROJECTOR_WIDTH - X_MARGIN, PROJECTOR_HEIGHT - Y_MARGIN),
		(X_MARGIN, PROJECTOR_HEIGHT- Y_MARGIN)
	]

	if os.path.isfile("./calibration.json"):
		calibration_points = json.load(open("calibration.json"))
		return calibration_dots, calibration_points


	calibration_image = np.zeros((PROJECTOR_HEIGHT, PROJECTOR_WIDTH, 3), dtype=np.float32)

	for i, point in enumerate(calibration_dots):
		
		color = (255, 0, 0)
		if i == 0:
			color = (0, 255, 255)
		cv2.circle(calibration_image, point, 30, color, thickness=-1)

	cv2.imshow(WINDOW_NAME, calibration_image)
	
	cv2.namedWindow("calibration")
	cv2.moveWindow("calibration", 0, 0)
	cv2.setMouseCallback("calibration", click)

	cv2.waitKey()

	_, camera_image = cam.read()
	camera_image = adjust_picture(camera_image, contrast=1.5, brightness=0.75)
	cv2.imshow('calibration', camera_image)

	while True:
		if cv2.waitKey(1) == 27: break

	with open("calibration.json", "w") as calibration_file:
		calibration_file.write(json.dumps(calibration_points))

	cv2.destroyWindow('calibration')

	return calibration_dots, calibration_points

def find_cards(image):

	def sort_poly(poly):
		close_vert = poly[0]
		for vert in poly:
			if distance((CAMERA_WIDTH,CAMERA_HEIGHT), vert) < distance((CAMERA_WIDTH,CAMERA_HEIGHT), close_vert):
				close_vert = vert
		while not np.array_equal(poly[0],close_vert):
			poly = np.roll(poly, 1, axis=0)
		return poly

	image = cv2.GaussianBlur(image, (3,3), 0)
	image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	_, image_thresh = cv2.threshold(image_gray, THRESHOLD, 255, cv2.THRESH_BINARY)
	# cv2.imshow('thres', image_thresh)
	# cv2.waitKey()
	_, contours, _ = cv2.findContours(image_thresh, cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_TC89_KCOS)
	# print(contours)
	
	polys = []
	hulls = []
	button = None

	for cont in contours:
		area = cv2.contourArea(cont)
		length = cv2.arcLength(cont, False)

		hull = cv2.convexHull(cont)
		hulls.append(hull)
		poly = cv2.approxPolyDP(cont, 20, True).copy().reshape(-1, 2)

		if len(poly) == 4:
			if area > 40000:
				poly = sort_poly(poly)
				polys.append(poly)
			# elif is_square(poly):
			# 	button = poly
 
	polys = sorted(polys, key= lambda p: cv2.contourArea(p), reverse=True)

	# cv2.drawContours(image, contours,-1,(255, 0, 0),2)
	# cv2.drawContours(image, polys,-1,(255, 0, 0),3)
	# cv2.drawContours(image, hulls,-1,(0, 255, 0),3)
	# cv2.imshow('contours', cv2.resize(image, (512,320)))

	# cv2.waitKey()

	return polys

def get_windows():

	raw_windows = subprocess.Popen("./GetWindows", shell=True, stdout=subprocess.PIPE)

	windows = []

	for line in raw_windows.stdout.readlines():
		line = line.decode().replace("\n", "")
		window = {}
		parts = line.split("\t")
		nums = [int(n) for n in parts[1].split(" ")]
		window = {
			"name" : parts[0],
			"left" : nums[0],
			"top" : nums[1],
			"width" : nums[2],
			"height" : nums[3],
			"last_pos" : (0, 0)
		}
		windows.append(window)

	return windows

def find_centroid(rect):

	M = cv2.moments(rect)

	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])

	return cx, cy

def distance(p1, p2):

	return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def adjust_picture(image, brightness=1, contrast=1):

	pil_image = Image.fromarray(image)

	contrastEnhancer = ImageEnhance.Contrast(pil_image)
	pil_image = contrastEnhancer.enhance(contrast)

	brightnessEnhancer = ImageEnhance.Brightness(pil_image)
	pil_image = brightnessEnhancer.enhance(brightness)

	return np.array(pil_image)

def is_square(poly):
	
	(x, y, w, h) = cv2.boundingRect(poly)
	ar = w/h
	if 0.85 < ar < 1.15:
		return True
	return False

def is_button_pressed(image, button_point):

	# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	MID = 5
	button_area = image[button_point[1]-MID: button_point[1]+MID,button_point[0]-MID:button_point[0]+MID]
	mean = np.mean(button_area, axis=(0, 1))
	distance = np.linalg.norm(BUTTON_COLOR-mean)
	print(distance)
	if distance > 30:
		return True
	return False

def main():

	IS_BUTTON_PRESSED = False

	windows = get_windows()
	print(windows)

	def switch_window():
		global CURRENT_WINDOW
		# print("hello world")
		new_window_id = (CURRENT_WINDOW + 1) % len(windows)
		new_window = windows[new_window_id]

		x = int(new_window["left"] + new_window["width"] / 2)
		y = int(new_window["top"] + 5)
		os.system("./click -x {} -y {}".format(x,y))
		CURRENT_WINDOW = new_window_id

	keyboard.add_hotkey("f1", switch_window)

	cv2.namedWindow(WINDOW_NAME)
	cv2.moveWindow(WINDOW_NAME, 1024, 0)

	projector_points, calibration_points = calibrate()

	homography, _ = cv2.findHomography(np.float32(calibration_points),np.float32(projector_points))
	# switch_window(windows[CURRENT_WINDOW])

	while True:

		# print("windows: ",windows)

		_, img = cam.read()
		rows, cols, _ = img.shape
		warped = cv2.warpPerspective(img, homography, (cols, rows))[0:PROJECTOR_HEIGHT, 0:PROJECTOR_WIDTH]
		projected = np.zeros_like(warped)
		cards = find_cards(warped)

		# button_status = is_button_pressed(warped, button_point)
		# if not IS_BUTTON_PRESSED:
		# 	if button_status:
		# 		IS_BUTTON_PRESSED = True
		# else:
		# 	if not button_status:
		# 		print("button pressed!")

		# 		new_window_id = (CURRENT_WINDOW + 1) % len(windows)
		# 		switch_window(windows[new_window_id])
		# 		CURRENT_WINDOW = new_window_id

		# 		IS_BUTTON_PRESSED = False

		for w in windows:
			w["drawn"] = False
			w["sct_rect"] = None

		for rect in cards:

			centroid = find_centroid(rect)
			closest_window = sorted([w for w in windows if not w["drawn"]], key=lambda w: distance(centroid, w["last_pos"]))

			if len(closest_window) > 0:

				closest_window = closest_window[0]
				closest_window["drawn"] = True
				closest_window["sct_rect"] = rect
				closest_window["last_pos"] = centroid

			else:
				closest_window = windows[0]
				print("Too many windows :(")

			# print("closest_window:", closest_window)
			screenshot = np.array(sct.grab(closest_window))[:,:,:3]
			screenshot_height, screenshot_width, _ = screenshot.shape
			
			screenshot = adjust_picture(screenshot, contrast=1.5, brightness=0.75)
			
			if closest_window == windows[CURRENT_WINDOW]:
				screenshot[0:15,0:screenshot_width] = [0,255,0]
				screenshot[screenshot_height-15:screenshot_height,0:screenshot_width] = [0,255,0]
				screenshot[0:screenshot_height,0:15] = [0,255,0]
				screenshot[0:screenshot_height,screenshot_width-15:screenshot_width] = [0,255,0]

			Mw, _ = cv2.findHomography(
				np.float32([
					(0, 0),
					(0, screenshot_height),
					(screenshot_width, screenshot_height),
					(screenshot_width, 0)
				]),
				np.float32([rect[0], rect[1], rect[2], rect[3]]))

			persp_window = cv2.warpPerspective(screenshot, Mw, (PROJECTOR_WIDTH, PROJECTOR_HEIGHT))

			projected += persp_window
		
		cv2.imshow(WINDOW_NAME, projected)
		if cv2.waitKey(1) == 27: break

main()
	
