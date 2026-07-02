# User-s-Guide-Program-DiDePT
## This is a guide to handle the data analysis software of the DiDePT
There are two options to run the program:
1. Before running the program to install the language program Python 3.13.2 on the PC, which can be downloaded in: https://www.python.org/downloads/, and download the files in the folder DiDePT/DiDePT Analysis.
   or
2. Download the file 'main_for_tif.exe' found in the "releases" with the tag "main for tif v1.0" in the left of the screen. You can use the folder 'photos_treatments_06052026' to do a first try, please put this file in the same folder as the executable 'main_for_tif.exe'.

Firstly, download the folder "DiDePT Analysis", in this you will find the necessary python programs to start the program. Please, put your image folder inside "DiDePT Analysis" folder once you have the images. 

1- Run the file "main_for_tif". Now, that the program is running it would appear the "Initial Settings" as it is shown in the picture:

<img width="1266" height="372" alt="image" src="https://github.com/user-attachments/assets/1b50d64d-6995-482e-a5d9-80c15b75e181" />

Please, set the different boxes as your will, and click on "Save settings". 
2- Now, it will appear the image of the time you have selected for the circles detection,if you want to let the default configuration with the coordinates {x1, y1}:{70, 90} (left upper corner) and {x2, y2}:{570, 428} ( right bottom corner) only press "Confirm crop", but you can select an area holding the left click in the left upper corner until the right bottom corner. 

<img width="797" height="690" alt="image" src="https://github.com/user-attachments/assets/71e1938e-eec1-4620-8181-1cf8c34ecee3" />

*If you are going to select the area please consider that to obtain a good region of interest you must select an area that includes a little empty space in the edges as well as covers all your circles, like it is shown in the following image:*

<img width="797" height="687" alt="image" src="https://github.com/user-attachments/assets/4297c30a-fad9-41f4-9b1a-2ecdd93571c9" />

3-Now, an image of the initial time and the final time will pop-up on the screen, this will help you to corroborate if the time you have selected for the circles detection is ideal.

<img width="1187" height="777" alt="image" src="https://github.com/user-attachments/assets/0a56529b-32e1-4466-9121-7144abdf83a0" />

4-It will pop-up a message to confirm the amount of treatments you will use.

<img width="281" height="132" alt="image" src="https://github.com/user-attachments/assets/6f50b8f3-86bc-4528-8a66-0a2f970df67b" />

5-Select the cells corresponding to "Positive controls" (Blue), "Negative controls" (Red), and "Assays" (Green), and press "OK" when you are done or "Restart" if you want to remove your selections.

<img width="1231" height="627" alt="image" src="https://github.com/user-attachments/assets/5fa2db17-1e22-4fd1-ad1e-5ae192727f88" />

<img width="1232" height="627" alt="image" src="https://github.com/user-attachments/assets/600a8aa6-e721-41d5-9b98-ad48fceb2a3e" />

6-Another pop-up message will appear to confirm your selections.

<img width="476" height="192" alt="image" src="https://github.com/user-attachments/assets/f18c5049-45bc-4c81-a4ba-5d95c173ad35" />

<!--<img width="560" height="422" alt="image" src="https://github.com/user-attachments/assets/6819d89d-0032-4981-b623-17c5b8e14c11" />-->

7- A plot with the filter applied to the image, a histogram of the pixels and the umbralization of the image will appear.

<img width="1486" height="497" alt="image" src="https://github.com/user-attachments/assets/b3cc1c97-407a-433e-8647-b19a568dfdba" />

8- An image signaling all the circles detected will appear, you can use to corroborate the program is able to detect the circles in your image. If you were expecting better detection please close the program and run it again and change the initial settings as you wish.

<img width="627" height="492" alt="image" src="https://github.com/user-attachments/assets/dd88626a-e6e2-4a34-aef1-25a51ae644ec" />

9- Now the intensity plot will appear with the title "Results DiDePT", showing the fluorescence and the "Threshold" to differentiate positive samples from negative samples.

<img width="1031" height="720" alt="image" src="https://github.com/user-attachments/assets/72cea982-4588-460d-8722-8d58efa23036" />

10- Next, it will be shown plots with the slopes,  sigmoidal fit as well as a box plot.

<img width="1062" height="711" alt="image" src="https://github.com/user-attachments/assets/bfe19f37-4980-44bd-9e4d-5335de75fc13" />

<img width="1042" height="727" alt="image" src="https://github.com/user-attachments/assets/ba965594-749b-412c-876c-1486a00bac99" />

<img width="522" height="437" alt="image" src="https://github.com/user-attachments/assets/cd2bff9a-998f-4f39-a1f7-a4cc8c834dd8" />



