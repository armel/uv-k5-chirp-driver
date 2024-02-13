# uv-k5-chirp-driver
Quansheng UV-K5 radio CHIRP driver for F4HWN firmware

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

To upload all the other in chirp setting to the radio, remove the selection of the Upload F4HWN setting to radio (1) and then upload to the radio (2), then press ok, the upload will take some time, when finish the radio will reboot.

Enjoy.
