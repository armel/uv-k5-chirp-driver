# uv-k5-chirp-driver
Quansheng UV-K5 radio CHIRP driver for F4HWN firmware

In Version 2.8.1
Bug fix: In any programable key ( F1, F2, M ), if the action selected is between NONE to MODE, it's working... but any value greather then MORE the value in the driver have error when sent to the radio or read from the radio.

It's texte change to follow the firmware 2.8.0

In Version 2.7.0
it's the url link update for the firware Armel has been update in english and french driver
In the english version text ajustement done by fcatt(francois) as been add to be more accurate...
Add a new help file for the (quick key, quick reference) done by KwWGG to help user


Armel release version 2.7, but no change has been involve to chirp driver with in his modification(bug fix, feature, etc) , so chirp driver not change. The only thing i add, it's the new file pdf from Alain that describle the update in the version 2,7. so i just add this file. so use version 2.6 chirp driver

In version 2.6.0: This is just cosmetic change to follow the radio modification ( version 2.5 and 2.6 are the same functionality )
Rename BackLt to BLTime
Rename BltTRX to BLTxRx 

In version 2.5.0: FLock option PMR446 add. 
change backlight time range, now it's from 5 sec to 5 minutes
change tx timeout range , now it's from 30 sec to 15 minutes
the french driver and the english driver are updated
the file help from 14UVR010 is not update for version 2.5, but the link for the drop box it's now include int the file for update

In version 2.4.0: cosmetic change, text update. 
In the release: A version of the file DOC is copy in a PDF version to be more universal for user reading, 
A other french file has been add to help user to understand their Radio. ( menu armel f4hwn.pdf done by 14UVR010) this is a copy of his file. To get the last update, go on the FB Group UV-K5 france. He allow me to put the file in this release.  

In version 2.3.0: French file of the driver and documentation been had, a release has been done to include all in the same package. 

In version 2.2.1: Add the fly over in extra field in the memories tab. I was request chirp team to add it and they add it on the the last release on the basic setting has it's not in the driver. 

In version 2.2.0: Add the new item in the menu of the programable key. Temporarily backlight off. kind of turn off the backlight now.
Add the help user menu, it's basic, it not yet complete...
Add description text 

In version 2.0.0: Add the new item in the menu of the power on message. Make a visual more standard on the fly of display with the mouse all over the setting...

In the driver chirp for F4HWN version 1.8.2 and futur, their is a textbox with the mouse over option on almost everything. this is to help user to get more info about what is this option is for... :)

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/22f742e6-2346-4f7e-9c2f-72abc4f4412f)

You'll find a [short video](https://www.youtube.com/watch?v=02T2ODufZOA) on how to use the Chirp driver on my Youtube channel. Be aware, this video is in french, so activate subtitle if necessary :)

Otherwise, here's how to use it.

To load the driver, few step need to be done the first time you use chirp.

first thing, in chirp, tab Help , select developement mode

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/6b434f9f-f8bc-4eee-bbc1-835d85c45629)

a warning message will pop up select Yes

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/7c0c8cd1-d346-4c61-b8d6-5602f04d3aa8)

their a other pop up that told you to close chirp and reopen it to make the change to take effect.
![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/5a9a619a-293f-4646-891e-4be7debed135)

close chirp and re open it.

now in the menu View, be sure the show show extra field is selected.

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/65288ab1-7c83-456a-83b9-3381842190d8)

from this point, all the previus step no need to be done any more..

****************************************************
****************************************************
To Load the driver: uvk5_egzumer_f4hwn.py
****************************************************
****************************************************
in file, select Load Module

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/fb2d05a0-248c-4d7a-ab2f-3b6780779d83)

A warning message will pop up, accept it, ( click yes) 

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/9dc4a24d-3a26-480b-8aab-c3a00869dc63)

browsed to the file location where you save the file on your computer then select the file. then click OK
![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/6e3c229d-a1b0-47a9-975f-25a679849e0a)

now chirp will show you that the module has been loaded
in the top bar menu..

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/c09085f3-d9d0-4dba-b285-25dd8fa1ff64)

Now, open the radio in normal mode... ( just turn the knob)  connect the programming cable jack in to the radio and the other end in the computer.

Go in menu Radio, Download from radio..

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/9fba440a-efdd-4c71-b61a-658deb5337a7)

select the port, the vendor and the model.. you need to select the uv-k5 egzumer + f4hwn 

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/b1d717f3-d6bb-4ad2-87c6-114f3e2ae461)

click OK then Wait to reading the be complete.

do not forget to save this reading if you want to keep this data for futur uses.

**********************************************************************************************************************
The option for the F4HWN firmware are under Basic Setting, on the top

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/52e3c299-ebf3-4696-8a04-582f93921114)

If you want to upload the setting of F4HWN to the radio, select the Upload F4HWN setting to radio (1),
then upload to the radio (2), 

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/e8558d44-48f4-44c3-9ae5-c900183397cf)

then press ok, 

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/cbd461c3-6f95-4e54-aff6-4469146f04d9)

The upload will be realy fast ....
when finish, the radio will reboot after.
******************************************************************************************************************
This will ONLY and ONLY upload the setting of F4HWN to the radio, all other setting in chirp will stay in chirp.
******************************************************************************************************************

To upload all the other setting in chirp to the radio, remove the selection of the Upload F4HWN setting to radio (1) and then upload to the radio (2), then press ok, the upload will take some time, when finish the radio will reboot.

Enjoy.
