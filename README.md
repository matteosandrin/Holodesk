![](https://github.com/matteosandrin/Holodesk/raw/master/images/banner_small.png)

## Holodesk 

- 🏆 PennApps XVIII Finalist  
- 🏆 PennApps XVIII Best UI/UX Prize Winner

### Inspiration
  
I've always been fascinated by the complexities of UX design, and this project was an opportunity to explore an interesting mode of interaction. I drew inspiration from the futuristic UIs that movies have to offer, such as Minority Report's gesture-based OS or Iron Man's heads-up display, Jarvis.

	
### What it does

Each window in your desktop is rendered on a separate piece of paper, creating a tangible version of your everyday computer. It is a fully featured desktop, with specific shortcuts for window management.
<p align="center">
	<img width="500" src="https://github.com/matteosandrin/Holodesk/raw/master/images/holodesk.gif" style="padding: 10px">
<p>


### How it's made	

The hardware is combination of a projector and a webcam. The camera tracks the position of the sheets of paper, on which the projector renders the corresponding window. An OpenCV backend does the heavy lifting, calculating the appropriate translation and warping to apply.

<p align="center">
  <img width="500" src="https://github.com/matteosandrin/Holodesk/raw/master/images/IMG_8223.jpg" style="padding: 10px">
</p>


### Usage

1. Compile the `GetWindows.m` file with `gcc`.

	```
	gcc GetWindows.m -framework Foundation -framework Cocoa -o GetWindows
	```

2. Compile the `click.m` file with `gcc`.

	```
	gcc click.m -framework ApplicationServices -framework Foundation -o click
	```

3. Run the `main.py` file.  
*(the reason it needs to be run as root is because the `keyboard` python library, which is used to implement keyboard shortcuts, needs root access to function properly)*

	```
	sudo python3 main.py
	```

4. The first time the `main.py` file is run, it looks for a `calibration.json` file where the calibration points are contained. If the file is not found, the calibration procedure is started.
5. The calibration process creates two OpenCV windows:
	1. The first one presents four colored dots, which are displayed onto the projecting surface.
	2. The second, smaller one is blank.
6. Switch focus to the smaller window and press the ENTER key to begin the calibration process.
7. A frame from the webcam will be displayed onto the window. Click each of the four colored dots starting from the upper left corner (yellow) in a clockwise fashion, and hit the ESC key when done. 
8. The `calibration.json` file will be created, and the calibration step will be skipped until this file is present in the same folder as `main.py`.
9. If the program needs to be recalibrated, simply delete the `calibration.json` file.


