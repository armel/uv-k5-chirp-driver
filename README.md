# uv-k5-chirp-driver
Quansheng UV-K5 radio CHIRP driver for F4HWN firmware

In version 3.8.1 :

fix UNUSED bug (Duplicate definition for UNUSED #48)

In version 3.8.0 :

add POWER HIGH and REMOVE OFFSET action

In version 3.7.1 :

fix bug with MicBar upload
fix bug with BatTxt upload

In version 3.7.0 :

add support for RescueOps special version
add the new link for the pdf of alain   

In version 3.6.3 :

updade duplex from issue #33 in github

In version 3.6.2 :

fix error setoff

In version 3.6.1 :

in version FR the BatSav 32/68 was missing the value 1:5
text correction in fr version
update link pdf for the 3.6 

In version 3.6.0 :

change BatSav 32/68 and 1:5 value to follow firmware
add SetNFM 68/68 to follow firmware
add new video link (Youtube from 4S7JL_SRI_LANKA)

In version 3.5.2 :

Modify the way the setting of f4hwn is upload to the radio, now it's standard, when send data  all setting are sent

In version 3.5.1 :

Fix the duplex mode related to issue in github, 
update link pdf for the 3.5 

In version 3.5.0 :

change ScnRev 24/67 (Scan Resume Mode) to follow firmware
add D Live checkbox in DTMF Settings
change KeyLck 30/67 to follow firmware
some code refactoring

In version 3.4.0 :

remove tx250 tx350 tx500 Setting has firmware not use it any more ,
add the SetOff to turn off the radio ,
change ScnRev 24/67 (Scan Resume Mode) to follow firmware ,
update link pdf for the 3.4 ,
Add 2 more youtube link

In version 3.3.0 :

#3.3.0: Add the Set Timer
update info in help menu

In version 3.2.0 :

#3.2.0: some info still in english in the french version, translates it
add web link in firmware
add tx lock in all channel
update link pdf for 3.2

In version 3.1.0 :

unknow bit change for specify name
 
add web link

explain how the change chirp language

add User, low1 to low5 to the power level

AM fix message information this has not change

update info how to change language in chirp

rename set_low to set pwr

add the 3500ma battery selection

![image](https://github.com/user-attachments/assets/8d593ea3-f0d9-44b0-9ddf-b3817a89d8c6)

![image](https://github.com/user-attachments/assets/c10e4c17-eb50-4526-b69d-6c66bfb0310a)

![image](https://github.com/user-attachments/assets/b32783f2-de66-4824-acf6-9cadf6de9c14)



In Version 3.0.1
Bug Fix: the scanlist priority was not working

In Version 3.0.0  
Bug Fix: the pop-up window in the menu unlock all was not done on the right item. 

New thing : Add Flock option has Armel Add it

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/cc81c77b-2897-4f41-af70-e366d12fd7d7)

  Add the new scan list number 3, add the selection of this scan list in slit option  ( in memory and in steeing scan list)

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/079b93cb-54ae-4da1-9ff5-3b8f6a55cada)

![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/a4e1be78-a24e-48cf-a5bd-06cd5e6802b6)
  
  Add a new menu firmware in the setting, on the top of the list, to display firmware version and what version is it,, bandcope or broadcast
  
  ![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/25b91461-7f2b-4889-8d62-bcf1de0b0126)

  
  ![image](https://github.com/armel/uv-k5-chirp-driver/assets/56229329/9482c6a0-259d-4973-96c2-49ca8713711c)



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

Enjoy.
