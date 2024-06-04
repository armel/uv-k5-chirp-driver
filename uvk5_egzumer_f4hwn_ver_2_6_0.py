# Quansheng UV-K5 driver (c) 2023 Jacek Lipkowski <sq5bpf@lipkowski.org>
# Adapted For UV-K5 EGZUMER custom software By EGZUMER, JOC2
# Re-Adapted For UV-K5 EGZUMER/F4HWN custom software By JOC2
#
# based on template.py Copyright 2012 Dan Smith <dsmith@danplanet.com>
#
#
# This is a preliminary version of a driver for the UV-K5
# It is based on my reverse engineering effort described here:
# https://github.com/sq5bpf/uvk5-reverse-engineering
#
# Warning: this driver is experimental, it may brick your radio,
# eat your lunch and mess up your configuration.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# change/ modification
#
# 2024-02-09 :section password has been commented, because the new chirp give error with int.
# 2024-02-18 : a bug fix has been remove, that seem not work under mac os.. under investigation..
#              search for (bugfix calibration)

import struct
import logging
import wx

from chirp import chirp_common, directory, bitwise, memmap, errors, util
from chirp.settings import RadioSetting, RadioSettingGroup, \
    RadioSettingValueBoolean, RadioSettingValueList, \
    RadioSettingValueInteger, RadioSettingValueString, \
    RadioSettings, InvalidValueError

LOG = logging.getLogger(__name__)

# Show the obfuscated version of commands. Not needed normally, but
# might be useful for someone who is debugging a similar radio
DEBUG_SHOW_OBFUSCATED_COMMANDS = False

# Show the memory being written/received. Not needed normally, because
# this is the same information as in the packet hexdumps, but
# might be useful for someone debugging some obscure memory issue
DEBUG_SHOW_MEMORY_ACTIONS = False

# TODO: remove the driver version when it's in mainline chirp 
DRIVER_VERSION = "Quansheng UV-K5/K6/5R driver ver: 2024/04/25 (c) EGZUMER + F4HWN v2.6.0"
FIRMWARE_DRIVER_VERSION_UPDATE = "https://github.com/armel/uv-k5-firmware-custom"
CHIRP_DRIVER_VERSION_UPDATE = "https://github.com/armel/uv-k5-chirp-driver"
 
VALEUR_COMPILER = "ENABLE"

MEM_FORMAT = """
//#seekto 0x0000;
struct {
  ul32 freq;
  ul32 offset;

// 0x08
  u8 rxcode;
  u8 txcode;

// 0x0A
  u8 txcodeflag:4,
  rxcodeflag:4;

// 0x0B
  u8 modulation:4,
  offsetDir:4;

// 0x0C
  u8 __UNUSED1:3,
  busyChLockout:1,
  txpower:2,
  bandwidth:1,
  freq_reverse:1;

  // 0x0D
  u8 __UNUSED2:4,
  dtmf_pttid:3,
  dtmf_decode:1;

  // 0x0E
  u8 step;
  u8 scrambler;

} channel[214];

//#seekto 0xd60;
struct {
u8 is_scanlist1:1,
is_scanlist2:1,
compander:2,
is_free:1,
band:3;
} ch_attr[207];

#seekto 0xe40;
ul16 fmfreq[20];

#seekto 0xe70;
u8 call_channel;
u8 squelch;
u8 max_talk_time;
u8 noaa_autoscan;
u8 key_lock;
u8 vox_switch;
u8 vox_level;
u8 mic_gain;


u8 backlight_min:4,
backlight_max:4;

u8 channel_display_mode;
u8 crossband;
u8 battery_save;
u8 dual_watch;
u8 backlight_time;
u8 ste;
u8 freq_mode_allowed;

#seekto 0xe80;
u8 ScreenChannel_A;
u8 MrChannel_A;
u8 FreqChannel_A;
u8 ScreenChannel_B;
u8 MrChannel_B;
u8 FreqChannel_B;
u8 NoaaChannel_A;
u8 NoaaChannel_B;

#seekto 0xe90;

u8 keyM_longpress_action:7,
    button_beep:1;

u8 key1_shortpress_action;
u8 key1_longpress_action;
u8 key2_shortpress_action;
u8 key2_longpress_action;
u8 scan_resume_mode;
u8 auto_keypad_lock;
u8 power_on_dispmode;
ul32 password;

#seekto 0xea0;
u8 voice;
u8 s0_level;
u8 s9_level;

#seekto 0xea8;
u8 alarm_mode;
u8 roger_beep;
u8 rp_ste;
u8 TX_VFO;
u8 Battery_type;

#seekto 0xeb0;
char logo_line1[16];
char logo_line2[16];

//#seekto 0xed0;
struct {
    u8 side_tone;
    char separate_code;
    char group_call_code;
    u8 decode_response;
    u8 auto_reset_time;
    u8 preload_time;
    u8 first_code_persist_time;
    u8 hash_persist_time;
    u8 code_persist_time;
    u8 code_interval_time;
    u8 permit_remote_kill;

    #seekto 0xee0;
    char local_code[3];
    #seek 5;
    char kill_code[5];
    #seek 3;
    char revive_code[5];
    #seek 3;
    char up_code[16];
    char down_code[16];
} dtmf;

//#seekto 0xf18;
u8 slDef;
u8 sl1PriorEnab;
u8 sl1PriorCh1;
u8 sl1PriorCh2;
u8 sl2PriorEnab;
u8 sl2PriorCh1;
u8 sl2PriorCh2;

#seekto 0xf40;
u8 int_flock;
u8 int_350tx;
u8 int_KILLED;
u8 int_200tx;
u8 int_500tx;
u8 int_350en;
u8 int_scren;


u8  backlight_on_TX_RX:2,
    AM_fix:1,
    mic_bar:1,
    battery_text:2,
    live_DTMF_decoder:1,
    unknown:1;


#seekto 0xf50;
struct {
char name[16];
} channelname[200];

#seekto 0x1c00;
struct {
char name[8];
char number[3];
#seek 5;
} dtmfcontact[16];

struct {
    struct {
        #seekto 0x1E00;
        u8 openRssiThr[10];
        #seekto 0x1E10;
        u8 closeRssiThr[10];
        #seekto 0x1E20;
        u8 openNoiseThr[10];
        #seekto 0x1E30;
        u8 closeNoiseThr[10];
        #seekto 0x1E40;
        u8 closeGlitchThr[10];
        #seekto 0x1E50;
        u8 openGlitchThr[10];
    } sqlBand4_7;

    struct {
        #seekto 0x1E60;
        u8 openRssiThr[10];
        #seekto 0x1E70;
        u8 closeRssiThr[10];
        #seekto 0x1E80;
        u8 openNoiseThr[10];
        #seekto 0x1E90;
        u8 closeNoiseThr[10];
        #seekto 0x1EA0;
        u8 closeGlitchThr[10];
        #seekto 0x1EB0;
        u8 openGlitchThr[10];
    } sqlBand1_3;

    #seekto 0x1EC0;
    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands3_7;

    struct {
        ul16 level1;
        ul16 level2;
        ul16 level4;
        ul16 level6;
    } rssiLevelsBands1_2;

    struct {
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } low;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } mid;
        struct {
            u8 lower;
            u8 center;
            u8 upper;
        } hi;
        #seek 7;
    } txp[7];

    #seekto 0x1F40;
    ul16 batLvl[6];

    #seekto 0x1F50;
    ul16 vox1Thr[10];

    #seekto 0x1F68;
    ul16 vox0Thr[10];

    #seekto 0x1F80;
    u8 micLevel[5];

    #seekto 0x1F88;
    il16 xtalFreqLow;

    #seekto 0x1F8E;
    u8 volumeGain;
    u8 dacGain;
} cal;


#seekto 0x1FF0;
struct {
u8 ENABLE_DTMF_CALLING:1,
   ENABLE_PWRON_PASSWORD:1,
   ENABLE_TX1750:1,
   ENABLE_ALARM:1,
   ENABLE_VOX:1,
   ENABLE_VOICE:1,
   ENABLE_NOAA:1,
   ENABLE_FMRADIO:1;
u8 __UNUSED:3,
   ENABLE_AM_FIX:1,
   ENABLE_BLMIN_TMP_OFF:1,
   ENABLE_RAW_DEMODULATORS:1,
   ENABLE_WIDE_RX:1,
   ENABLE_FLASHLIGHT:1;
} BUILD_OPTIONS;

#seekto 0x1FF2;
u8 eeprom0x1ff2;
u8 eeprom0x1ff3;
u8 eeprom0x1ff4;

u8 set_gui:1,
set_met:1,
set_lck:1,
set_inv:1,
set_contrast:4;

u8 set_tot:4,
set_eot:4;

u8 set_low:4,
set_ptt:4;

u8 eeprom0x1ff8;
u8 eeprom0x1ff9;
u8 eeprom0x1ffa;
u8 eeprom0x1ffb;
u8 eeprom0x1ffc;
u8 eeprom0x1ffd;
u8 eeprom0x1ffe;
u8 eeprom0x1fff;
"""


# flags1
FLAGS1_OFFSET_NONE = 0b00
FLAGS1_OFFSET_MINUS = 0b10
FLAGS1_OFFSET_PLUS = 0b01

POWER_HIGH = 0b10
POWER_MEDIUM = 0b01
POWER_LOW = 0b00

# SET_LOW_POWER f4hwn
SET_LOW_LIST = [ "< 20mW", "125mW", "250mW", "500mW", "1W"]

# SET_PTT f4hwn
SET_PTT_LIST = ["CLASSIC", "ONEPUSH"]

# SET_TOT and SET_EOT f4hwn
SET_TOT_EOT_LIST = ["OFF", "SOUND", "VISUAL", "ALL"]

# SET_OFF_ON f4hwn
SET_OFF_ON_LIST = ["OFF", "ON"]

# SET_lck f4hwn
SET_LCK_LIST = ["KEYS", "KEYS+PTT"]

# SET_MET SET_GUI f4hwn
SET_MET_LIST = ["TINY", "CLASSIC"]


# dtmf_flags
PTTID_LIST = ["OFF", "UP CODE", "DOWN CODE", "UP+DOWN CODE", "APOLLO QUINDAR"]

# power
UVK5_POWER_LEVELS = [chirp_common.PowerLevel("Low",  watts=1.50),
                     chirp_common.PowerLevel("Med",  watts=3.00),
                     chirp_common.PowerLevel("High", watts=5.00),
                     ]

# scrambler
SCRAMBLER_LIST = ["OFF", "2600Hz", "2700Hz", "2800Hz", "2900Hz", "3000Hz",
                  "3100Hz", "3200Hz", "3300Hz", "3400Hz", "3500Hz"]
# compander
COMPANDER_LIST = ["OFF", "TX", "RX", "TX/RX"]

# rx mode
RXMODE_LIST = ["MAIN ONLY", "DUAL RX RESPOND", "CROSS BAND", "MAIN TX DUAL RX"]

# channel display mode
CHANNELDISP_LIST = ["Frequency (FREQ)", "CHANNEL NUMBER", "NAME", "Name + Frequency (NAME + FREQ)"]

# TalkTime
TALK_TIME_LIST = ["N/U", "N/U", "N/U", "N/U", "N/U", "30 sec", "35 sec", "40 sec", "45 sec", "50 sec", "55 sec", 
                  "1 min", "1 min : 5 sec", "1 min : 10 sec", "1 min : 15 sec", "1 min : 20 sec", "1 min : 25 sec", "1 min : 30 sec", "1 min : 35 sec", "1 min : 40 sec", "1 min : 45 sec", "1 min : 50 sec", "1 min : 55 sec", 
                  "2 min", "2 min : 5 sec", "2 min : 10 sec", "2 min : 15 sec", "2 min : 20 sec", "2 min : 25 sec", "2 min : 30 sec", "2 min : 35 sec", "2 min : 40 sec", "2 min : 45 sec", "2 min : 50 sec", "2 min : 55 sec", 
                  "3 min", "3 min : 5 sec", "3 min : 10 sec", "3 min : 15 sec", "3 min : 20 sec", "3 min : 25 sec", "3 min : 30 sec", "3 min : 35 sec", "3 min : 40 sec", "3 min : 45 sec", "3 min : 50 sec", "3 min : 55 sec", 
                  "4 min", "4 min : 5 sec", "4 min : 10 sec", "4 min : 15 sec", "4 min : 20 sec", "4 min : 25 sec", "4 min : 30 sec", "4 min : 35 sec", "4 min : 40 sec", "4 min : 45 sec", "4 min : 50 sec", "4 min : 55 sec",
                  "5 min", "5 min : 5 sec", "5 min : 10 sec", "5 min : 15 sec", "5 min : 20 sec", "5 min : 25 sec", "5 min : 30 sec", "5 min : 35 sec", "5 min : 40 sec", "5 min : 45 sec", "5 min : 50 sec", "5 min : 55 sec",
                  "6 min", "6 min : 5 sec", "6 min : 10 sec", "6 min : 15 sec", "6 min : 20 sec", "6 min : 25 sec", "6 min : 30 sec", "6 min : 35 sec", "6 min : 40 sec", "6 min : 45 sec", "6 min : 50 sec", "6 min : 55 sec", 
                  "7 min", "7 min : 5 sec", "7 min : 10 sec", "7 min : 15 sec", "7 min : 20 sec", "7 min : 25 sec", "7 min : 30 sec", "7 min : 35 sec", "7 min : 40 sec", "7 min : 45 sec", "7 min : 50 sec", "7 min : 55 sec", 
                  "8 min", "8 min : 5 sec", "8 min : 10 sec", "8 min : 15 sec", "8 min : 20 sec", "8 min : 25 sec", "8 min : 30 sec", "8 min : 35 sec", "8 min : 40 sec", "8 min : 45 sec", "8 min : 50 sec", "8 min : 55 sec", 
                  "9 min", "9 min : 5 sec", "9 min : 10 sec", "9 min : 15 sec", "9 min : 20 sec", "9 min : 25 sec", "9 min : 30 sec", "9 min : 35 sec", "9 min : 40 sec", "9 min : 45 sec", "9 min : 50 sec", "9 min : 55 sec",
                  "10 min", "10 min : 5 sec", "10 min : 10 sec", "10 min : 15 sec", "10 min : 20 sec", "10 min : 25 sec", "10 min : 30 sec", "10 min : 35 sec", "10 min : 40 sec", "10 min : 45 sec", "10 min : 50 sec", "10 min : 55 sec",
                  "11 min", "11 min : 5 sec", "11 min : 10 sec", "11 min : 15 sec", "11 min : 20 sec", "11 min : 25 sec", "11 min : 30 sec", "11 min : 35 sec", "11 min : 40 sec", "11 min : 45 sec", "11 min : 50 sec", "11 min : 55 sec", 
                  "12 min", "12 min : 5 sec", "12 min : 10 sec", "12 min : 15 sec", "12 min : 20 sec", "12 min : 25 sec", "12 min : 30 sec", "12 min : 35 sec", "12 min : 40 sec", "12 min : 45 sec", "12 min : 50 sec", "12 min : 55 sec", 
                  "13 min", "13 min : 5 sec", "13 min : 10 sec", "13 min : 15 sec", "13 min : 20 sec", "13 min : 25 sec", "13 min : 30 sec", "13 min : 35 sec", "13 min : 40 sec", "13 min : 45 sec", "13 min : 50 sec", "13 min : 55 sec", 
                  "14 min", "14 min : 5 sec", "14 min : 10 sec", "14 min : 15 sec", "14 min : 20 sec", "14 min : 25 sec", "14 min : 30 sec", "14 min : 35 sec", "14 min : 40 sec", "14 min : 45 sec", "14 min : 50 sec", "14 min : 55 sec",
                  "15 min"]

# Auto Keypad Lock
AUTO_KEYPAD_LOCK_LIST = ["OFF", "AUTO"]

# battery save
BATSAVE_LIST = ["OFF", "1:1", "1:2", "1:3", "1:4"]

# battery type
BATTYPE_LIST = ["1600 mAh", "2200 mAh"]
# bat txt
BAT_TXT_LIST = ["NONE", "VOLTAGE", "PERCENT"]
# Backlight auto mode
BACKLIGHT_LIST = ["OFF", "5 sec", "10 sec", "15 sec", "20 sec", "25 sec", "30 sec", "35 sec", "40 sec", "45 sec", "50 sec", "55 sec", 
                  "1 min", "1 min : 5 sec", "1 min : 10 sec", "1 min : 15 sec", "1 min : 20 sec", "1 min : 25 sec", "1 min : 30 sec", "1 min : 35 sec", "1 min : 40 sec", "1 min : 45 sec", "1 min : 50 sec", "1 min : 55 sec", 
                  "2 min", "2 min : 5 sec", "2 min : 10 sec", "2 min : 15 sec", "2 min : 20 sec", "2 min : 25 sec", "2 min : 30 sec", "2 min : 35 sec", "2 min : 40 sec", "2 min : 45 sec", "2 min : 50 sec", "2 min : 55 sec", 
                  "3 min", "3 min : 5 sec", "3 min : 10 sec", "3 min : 15 sec", "3 min : 20 sec", "3 min : 25 sec", "3 min : 30 sec", "3 min : 35 sec", "3 min : 40 sec", "3 min : 45 sec", "3 min : 50 sec", "3 min : 55 sec", 
                  "4 min", "4 min : 5 sec", "4 min : 10 sec", "4 min : 15 sec", "4 min : 20 sec", "4 min : 25 sec", "4 min : 30 sec", "4 min : 35 sec", "4 min : 40 sec", "4 min : 45 sec", "4 min : 50 sec", "4 min : 55 sec",
                  "5 min", "Always On (ON)"]

# Backlight LVL
BACKLIGHT_LVL_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

# Backlight _TX_RX_LIST
BACKLIGHT_TX_RX_LIST = ["OFF", "TX", "RX", "TX/RX"]

# steps TODO: change order
STEPS = [2.5, 5, 6.25, 10, 12.5, 25, 8.33, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 1.25,
         9, 15, 20, 30, 50, 100, 125, 200, 250, 500]

# ctcss/dcs codes
TMODES = ["", "Tone", "DTCS", "DTCS"]
TONE_NONE = 0
TONE_CTCSS = 1
TONE_DCS = 2
TONE_RDCS = 3


CTCSS_TONES = [
    67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4,
    88.5, 91.5, 94.8, 97.4, 100.0, 103.5, 107.2, 110.9,
    114.8, 118.8, 123.0, 127.3, 131.8, 136.5, 141.3, 146.2,
    151.4, 156.7, 159.8, 162.2, 165.5, 167.9, 171.3, 173.8,
    177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5,
    203.5, 206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8,
    250.3, 254.1
]

# lifted from ft4.py
DTCS_CODES = [  # TODO: add negative codes
    23,  25,  26,  31,  32,  36,  43,  47,  51,  53,  54,
    65,  71,  72,  73,  74,  114, 115, 116, 122, 125, 131,
    132, 134, 143, 145, 152, 155, 156, 162, 165, 172, 174,
    205, 212, 223, 225, 226, 243, 244, 245, 246, 251, 252,
    255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325,
    331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412,
    413, 423, 431, 432, 445, 446, 452, 454, 455, 462, 464,
    465, 466, 503, 506, 516, 523, 526, 532, 546, 565, 606,
    612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723,
    731, 732, 734, 743, 754
]

# flock list extended
FLOCK_LIST = ["DEFAULT+ (137-174, 400-470 + Tx200, Tx350, Tx500)",
              "FCC HAM (144-148, 420-450)",
              "CE HAM (144-146, 430-440)",
              "GB HAM (144-148, 430-440)",
              "137-174, 400-430",
              "137-174, 400-438",
              "PMR 446",
              "DISABLE ALL",
              "UNLOCK ALL"]

SCANRESUME_LIST = ["Listen for 5 seconds and resume (TIMEOUT)",
                   "Listen until the signal disappears (CARRIER)",
                   "Stop scan when a signal is received (STOP)"]
WELCOME_LIST = ["Message line 1, Voltage, Sound (ALL)", "Make 2 short sounds (SOUND)", "User message line 1 and line 2 (MESSAGE)", "Battery voltage (VOLTAGE)", "NONE"]
VOICE_LIST = ["OFF", "Chinese", "English"]

# ACTIVE CHANNEL
TX_VFO_LIST = ["A", "B"]
ALARMMODE_LIST = ["SITE", "TONE"]
ROGER_LIST = ["OFF", "Roger beep (ROGER)", "MDC data burst (MDC)"]
RTE_LIST = ["OFF", "100ms", "200ms", "300ms", "400ms",
            "500ms", "600ms", "700ms", "800ms", "900ms", "1000ms"]
VOX_LIST = ["OFF", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

MEM_SIZE = 0x2000  # size of all memory
PROG_SIZE = 0x1d00  # size of the memory that we will write
MEM_BLOCK = 0x80  # largest block of memory that we can reliably write
CAL_START = 0x1E00  # calibration memory start address
F4HWN_START =0x1FF2 # calibration F4HWN memory start address

# fm radio supported frequencies
FMMIN = 76.0
FMMAX = 108.0

# bands supported by the UV-K5
BANDS_STANDARD = {
        0: [50.0, 76.0],
        1: [108.0, 136.9999],
        2: [137.0, 173.9999],
        3: [174.0, 349.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 600.0]
        }

BANDS_WIDE = {
        0: [18.0, 108.0],
        1: [108.0, 136.9999],
        2: [137.0, 173.9999],
        3: [174.0, 349.9999],
        4: [350.0, 399.9999],
        5: [400.0, 469.9999],
        6: [470.0, 1300.0]
        }

SCANLIST_LIST = ["None", "List1", "List2", "Both"]
SCANLIST_SELECT_LIST = ["LIST 1", "LIST 2", "All Channel (ALL)"]

DTMF_CHARS = "0123456789ABCD*# "
DTMF_CHARS_ID = "0123456789ABCDabcd"
DTMF_CHARS_KILL = "0123456789ABCDabcd"
DTMF_CHARS_UPDOWN = "0123456789ABCDabcd#* "
DTMF_CODE_CHARS = "ABCD*# "
DTMF_DECODE_RESPONSE_LIST = ["DO NOTHING", "Local ringing (RING)", "Replay response (REPLY)",
                             "Local ringing + reply response (BOTH)"]

KEYACTIONS_LIST = ["NONE",
                   "FLASHLIGHT",
                   "POWER",
                   "MONITOR",
                   "SCAN",
                   "Voice detection (VOX)",
                   "ALARM",
                   "FM RADIO",
                   "1750Hz TONE",
                   "LOCK KEYPAD",
                   "Switch main VFO (SWITCH VFO)",
                   "Switch frequency/memory mode (VFO/MR)",
                   "Switch demodulation (SWITCH DEMODUL)",
                   "Put the backlight OFF temporarily (BL_MIN_TMP_OFF)",
                   "Change RxMode: *Main only,*Dual RX,*Cross Band,*TX Dual RX (SWITCH RX MODE)",
                   "Toggle CLASSIC to ONE PUSH ptt (SWITCH PTT)",                   
                   "SWITCH WIDE NARROW"
                  ]

MIC_GAIN_LIST = ["+1.1dB", "+4.0dB", "+8.0dB", "+12.0dB", "+15.1dB"]


def xorarr(data: bytes):
    """the communication is obfuscated using this fine mechanism"""
    tbl = [22, 108, 20, 230, 46, 145, 13, 64, 33, 53, 213, 64, 19, 3, 233, 128]
    ret = b""
    idx = 0
    for byte in data:
        ret += bytes([byte ^ tbl[idx]])
        idx = (idx+1) % len(tbl)
    return ret


def calculate_crc16_xmodem(data: bytes):
    """
    if this crc was used for communication to AND from the radio, then it
    would be a measure to increase reliability.
    but it's only used towards the radio, so it's for further obfuscation
    """
    poly = 0x1021
    crc = 0x0
    for byte in data:
        crc = crc ^ (byte << 8)
        for _ in range(8):
            crc = crc << 1
            if crc & 0x10000:
                crc = (crc ^ poly) & 0xFFFF
    return crc & 0xFFFF


def _send_command(serport, data: bytes):
    """Send a command to UV-K5 radio"""
    LOG.debug("Sending command (unobfuscated) len=0x%4.4x:\n%s",
              len(data), util.hexprint(data))

    crc = calculate_crc16_xmodem(data)
    data2 = data + struct.pack("<H", crc)

    command = struct.pack(">HBB", 0xabcd, len(data), 0) + \
        xorarr(data2) + \
        struct.pack(">H", 0xdcba)
    if DEBUG_SHOW_OBFUSCATED_COMMANDS:
        LOG.debug("Sending command (obfuscated):\n%s", util.hexprint(command))
    try:
        result = serport.write(command)
    except Exception as e:
        raise errors.RadioError("Error writing data to radio") from e
    return result


def _receive_reply(serport):
    header = serport.read(4)
    if len(header) != 4:
        LOG.warning("Header short read: [%s] len=%i",
                    util.hexprint(header), len(header))
        raise errors.RadioError("Header short read")
    if header[0] != 0xAB or header[1] != 0xCD or header[3] != 0x00:
        LOG.warning("Bad response header: %s len=%i",
                    util.hexprint(header), len(header))
        raise errors.RadioError("Bad response header")

    cmd = serport.read(int(header[2]))
    if len(cmd) != int(header[2]):
        LOG.warning("Body short read: [%s] len=%i",
                    util.hexprint(cmd), len(cmd))
        raise errors.RadioError("Command body short read")

    footer = serport.read(4)

    if len(footer) != 4:
        LOG.warning("Footer short read: [%s] len=%i",
                    util.hexprint(footer), len(footer))
        raise errors.RadioError("Footer short read")

    if footer[2] != 0xDC or footer[3] != 0xBA:
        LOG.debug("Reply before bad response footer (obfuscated)"
                  "len=0x%4.4x:\n%s", len(cmd), util.hexprint(cmd))
        LOG.warning("Bad response footer: %s len=%i",
                    util.hexprint(footer), len(footer))
        raise errors.RadioError("Bad response footer")

    if DEBUG_SHOW_OBFUSCATED_COMMANDS:
        LOG.debug("Received reply (obfuscated) len=0x%4.4x:\n%s",
                  len(cmd), util.hexprint(cmd))

    cmd2 = xorarr(cmd)

    LOG.debug("Received reply (unobfuscated) len=0x%4.4x:\n%s",
              len(cmd2), util.hexprint(cmd2))

    return cmd2


def _getstring(data: bytes, begin, maxlen):
    tmplen = min(maxlen+1, len(data))
    ss = [data[i] for i in range(begin, tmplen)]
    key = 0
    for key, val in enumerate(ss):
        if val < ord(' ') or val > ord('~'):
            return ''.join(chr(x) for x in ss[0:key])
    return ''


def _sayhello(serport):
    hellopacket = b"\x14\x05\x04\x00\x6a\x39\x57\x64"

    tries = 5
    while True:
        LOG.debug("Sending hello packet")
        _send_command(serport, hellopacket)
        rep = _receive_reply(serport)
        if rep:
            break
        tries -= 1
        if tries == 0:
            LOG.warning("Failed to initialise radio")
            raise errors.RadioError("Failed to initialize radio")
    if rep.startswith(b'\x18\x05'):
        raise errors.RadioError("Radio is in programming mode, "
                                "restart radio into normal mode")
    firmware = _getstring(rep, 4, 24)

    LOG.info("Found firmware: %s", firmware)
    return firmware


def _readmem(serport, offset, length):
    LOG.debug("Sending readmem offset=0x%4.4x len=0x%4.4x", offset, length)

    readmem = b"\x1b\x05\x08\x00" + \
        struct.pack("<HBB", offset, length, 0) + \
        b"\x6a\x39\x57\x64"
    _send_command(serport, readmem)
    rep = _receive_reply(serport)
    if DEBUG_SHOW_MEMORY_ACTIONS:
        LOG.debug("readmem Received data len=0x%4.4x:\n%s",
                  len(rep), util.hexprint(rep))
    return rep[8:]


def _writemem(serport, data, offset):
    LOG.debug("Sending writemem offset=0x%4.4x len=0x%4.4x",
              offset, len(data))

    if DEBUG_SHOW_MEMORY_ACTIONS:
        LOG.debug("writemem sent data offset=0x%4.4x len=0x%4.4x:\n%s",
                  offset, len(data), util.hexprint(data))

    dlen = len(data)
    writemem = b"\x1d\x05" + \
        struct.pack("<BBHBB", dlen+8, 0, offset, dlen, 1) + \
        b"\x6a\x39\x57\x64"+data

    _send_command(serport, writemem)
    rep = _receive_reply(serport)

    LOG.debug("writemem Received data: %s len=%i",
              util.hexprint(rep), len(rep))

    if (rep[0] == 0x1e and
       rep[4] == (offset & 0xff) and
       rep[5] == (offset >> 8) & 0xff):
        return True

    LOG.warning("Bad data from writemem")
    raise errors.RadioError("Bad response to writemem")


def _resetradio(serport):
    resetpacket = b"\xdd\x05\x00\x00"
    _send_command(serport, resetpacket)


def do_download(radio):
    """download eeprom from radio"""
    serport = radio.pipe
    serport.timeout = 0.5
    status = chirp_common.Status()
    status.cur = 0
    status.max = MEM_SIZE
    status.msg = "Downloading from radio"
    radio.status_fn(status)

    eeprom = b""
    f = _sayhello(serport)
    if f:
        radio.FIRMWARE_VERSION = f
    else:
        raise errors.RadioError("Failed to initialize radio")

    addr = 0
    while addr < MEM_SIZE:
        data = _readmem(serport, addr, MEM_BLOCK)
        status.cur = addr
        radio.status_fn(status)

        if data and len(data) == MEM_BLOCK:
            eeprom += data
            addr += MEM_BLOCK
        else:
            raise errors.RadioError("Memory download incomplete")

    return memmap.MemoryMapBytes(eeprom)


def do_upload(radio):
    """upload configuration to radio eeprom"""
    serport = radio.pipe
    serport.timeout = 0.5
    status = chirp_common.Status()
    status.cur = 0
    status.msg = "Uploading to radio"

    if radio.upload_f4hwn:
        status.max = MEM_SIZE-F4HWN_START
        start_addr = F4HWN_START
        stop_addr = MEM_SIZE
    
    else:    
        if radio.upload_calibration:
            status.max = F4HWN_START-CAL_START
            start_addr = CAL_START
            stop_addr = F4HWN_START
        
        else:
            status.max = PROG_SIZE
            start_addr = 0
            stop_addr = PROG_SIZE

    radio.status_fn(status)

    f = _sayhello(serport)
    if f:
        radio.FIRMWARE_VERSION = f
    else:
        return False

    addr = start_addr
    while addr < stop_addr:
        dat = radio.get_mmap()[addr:addr+MEM_BLOCK]
        _writemem(serport, dat, addr)
        status.cur = addr - start_addr
        radio.status_fn(status)
        if dat:
            addr += MEM_BLOCK
        else:
            raise errors.RadioError("Memory upload incomplete")
    status.msg = "Uploaded OK"

    _resetradio(serport)

    return True


def min_max_def(value, min_val, max_val, default):
    """returns value if in bounds or default otherwise"""
    if min_val is not None and value < min_val:
        return default
    if max_val is not None and value > max_val:
        return default
    return value


def list_def(value, lst, default):
    """return value if is in the list, default otherwise"""
    if isinstance(default, str):
        default = lst.index(default)
    if value < 0 or value >= len(lst):
        return default
    return value


@directory.register
class UVK5RadioEgzumer(chirp_common.CloneModeRadio):
    """Quansheng UV-K5 (egzumer + f4hwn)"""
    VENDOR = "Quansheng"
    MODEL = "UV-K5 (egzumer + f4hwn)"
    BAUD_RATE = 38400
    NEEDS_COMPAT_SERIAL = False
    FIRMWARE_VERSION = ""

# this change to send power level chan in the calibration but under macos it give error
# bugfix calibration : put in comment next line: upload_calibration = False
    upload_calibration = False
    upload_f4hwn = False

    def _get_bands(self):
        is_wide = self._memobj.BUILD_OPTIONS.ENABLE_WIDE_RX \
            if self._memobj is not None else True
        bands = BANDS_WIDE if is_wide else BANDS_STANDARD
        return bands

    def _find_band(self, hz):
        mhz = hz/1000000.0
        bands = self._get_bands()
        for bnd, rng in bands.items():
            if rng[0] <= mhz <= rng[1]:
                return bnd
        return False

    def _get_vfo_channel_names(self):
        """generates VFO_CHANNEL_NAMES"""
        bands = self._get_bands()
        names = []
        for bnd, rng in bands.items():
            name = f"F{bnd + 1}({round(rng[0])}M-{round(rng[1])}M)"
            names.append(name + "A")
            names.append(name + "B")
        return names

    def _get_specials(self):
        """generates SPECIALS"""
        specials = {}
        for idx, name in enumerate(self._get_vfo_channel_names()):
            specials[name] = 200 + idx
        return specials

    @classmethod
    def get_prompts(cls):
        rp = chirp_common.RadioPrompts()
        rp.experimental = \
            'This is an experimental driver for the Quansheng UV-K5. ' \
            'It may harm your radio, or worse. Use at your own risk.\n\n' \
            'Before attempting to do any changes please download' \
            'the memory image from the radio with chirp ' \
            'and keep it. This can be later used to recover the ' \
            'original settings. \n\n' \
            'some details are not yet implemented'
        rp.pre_download = \
            "1. Turn radio on.\n" \
            "2. Connect cable to mic/spkr connector.\n" \
            "3. Make sure connector is firmly connected.\n" \
            "4. Click OK to download image from radio.\n\n" \
            "It may not work if you turn on the radio " \
            "with the cable already attached\n"
        rp.pre_upload = \
            "1. Turn radio on.\n" \
            "2. Connect cable to mic/spkr connector.\n" \
            "3. Make sure connector is firmly connected.\n" \
            "4. Click OK to upload the image to radio.\n\n" \
            "It may not work if you turn on the radio " \
            "with the cable already attached"
        return rp

    # Return information about this radio's features, including
    # how many memories it has, what bands it supports, etc
    def get_features(self):
        rf = chirp_common.RadioFeatures()
        rf.has_bank = False
        rf.valid_dtcs_codes = DTCS_CODES
        rf.has_rx_dtcs = True
        rf.has_ctone = True
        rf.has_settings = True
        rf.has_comment = False
        rf.valid_name_length = 10
        rf.valid_power_levels = UVK5_POWER_LEVELS
        rf.valid_special_chans = self._get_vfo_channel_names()
        rf.valid_duplexes = ["", "-", "+", "off"]

        steps = STEPS.copy()
        steps.sort()
        rf.valid_tuning_steps = steps

        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]
        rf.valid_cross_modes = ["Tone->Tone", "Tone->DTCS", "DTCS->Tone",
                                "->Tone", "->DTCS", "DTCS->", "DTCS->DTCS"]

        rf.valid_characters = chirp_common.CHARSET_ASCII
        rf.valid_modes = ["FM", "NFM", "AM", "NAM", "USB"]

        rf.valid_skips = [""]

        # This radio supports memories 1-200, 201-214 are the VFO memories
        rf.memory_bounds = (1, 200)

        # This is what the BK4819 chip supports
        # Will leave it in a comment, might be useful someday
        # rf.valid_bands = [(18000000,  620000000),
        #                  (840000000, 1300000000)
        #                  ]
        rf.valid_bands = []
        bands = self._get_bands()
        for _, rng in bands.items():
            rf.valid_bands.append(
                    (int(rng[0]*1000000), int(rng[1]*1000000)))
        return rf

    # Do a download of the radio from the serial port
    def sync_in(self):
        self._mmap = do_download(self)
        self.process_mmap()

    # Do an upload of the radio to the serial port
    def sync_out(self):
        do_upload(self)

    # Convert the raw byte array into a memory object structure
    def process_mmap(self):
        self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)

    # Return a raw representation of the memory object, which
    # is very helpful for development
    def get_raw_memory(self, number):
        return repr(self._memobj.channel[number-1])

    def validate_memory(self, mem):
        msgs = super().validate_memory(mem)

        if mem.duplex == 'off':
            return msgs

        # find tx frequency
        if mem.duplex == '-':
            txfreq = mem.freq - mem.offset
        elif mem.duplex == '+':
            txfreq = mem.freq + mem.offset
        else:
            txfreq = mem.freq

        # find band
        band = self._find_band(txfreq)
        if band is False:
            msg = f"Transmit frequency {txfreq/1000000.0:.4f}MHz " \
                   "is not supported by this radio"
            msgs.append(chirp_common.ValidationWarning(msg))

        band = self._find_band(mem.freq)
        if band is False:
            msg = f"The frequency {mem.freq/1000000.0:%.4f}MHz " \
                   "is not supported by this radio"
            msgs.append(chirp_common.ValidationWarning(msg))

        return msgs

    def _set_tone(self, mem, _mem):
        ((txmode, txtone, txpol),
         (rxmode, rxtone, rxpol)) = chirp_common.split_tone_encode(mem)

        if txmode == "Tone":
            txtoval = CTCSS_TONES.index(txtone)
            txmoval = 0b01
        elif txmode == "DTCS":
            txmoval = txpol == "R" and 0b11 or 0b10
            txtoval = DTCS_CODES.index(txtone)
        else:
            txmoval = 0
            txtoval = 0

        if rxmode == "Tone":
            rxtoval = CTCSS_TONES.index(rxtone)
            rxmoval = 0b01
        elif rxmode == "DTCS":
            rxmoval = rxpol == "R" and 0b11 or 0b10
            rxtoval = DTCS_CODES.index(rxtone)
        else:
            rxmoval = 0
            rxtoval = 0

        _mem.rxcodeflag = rxmoval
        _mem.txcodeflag = txmoval
        _mem.rxcode = rxtoval
        _mem.txcode = txtoval

    def _get_tone(self, mem, _mem):
        rxtype = _mem.rxcodeflag
        txtype = _mem.txcodeflag
        rx_tmode = TMODES[rxtype]
        tx_tmode = TMODES[txtype]

        rx_tone = tx_tone = None

        if tx_tmode == "Tone":
            if _mem.txcode < len(CTCSS_TONES):
                tx_tone = CTCSS_TONES[_mem.txcode]
            else:
                tx_tone = 0
                tx_tmode = ""
        elif tx_tmode == "DTCS":
            if _mem.txcode < len(DTCS_CODES):
                tx_tone = DTCS_CODES[_mem.txcode]
            else:
                tx_tone = 0
                tx_tmode = ""

        if rx_tmode == "Tone":
            if _mem.rxcode < len(CTCSS_TONES):
                rx_tone = CTCSS_TONES[_mem.rxcode]
            else:
                rx_tone = 0
                rx_tmode = ""
        elif rx_tmode == "DTCS":
            if _mem.rxcode < len(DTCS_CODES):
                rx_tone = DTCS_CODES[_mem.rxcode]
            else:
                rx_tone = 0
                rx_tmode = ""

        tx_pol = txtype == 0x03 and "R" or "N"
        rx_pol = rxtype == 0x03 and "R" or "N"

        chirp_common.split_tone_decode(mem, (tx_tmode, tx_tone, tx_pol),
                                       (rx_tmode, rx_tone, rx_pol))

    # Extract a high-level memory object from the low-level memory map
    # This is called to populate a memory in the UI
    def get_memory(self, number):

        mem = chirp_common.Memory()

        if isinstance(number, str):
            ch_num = self._get_specials()[number]
            mem.extd_number = number
        else:
            ch_num = number - 1

        mem.number = ch_num + 1

        _mem = self._memobj.channel[ch_num]

        is_empty = False
        # We'll consider any blank (i.e. 0MHz frequency) to be empty
        if (_mem.freq == 0xffffffff) or (_mem.freq == 0):
            is_empty = True

        # We'll also look at the channel attributes if a memory has them
        tmpscn = 0
        tmp_comp = 0
        if ch_num < 200:
            _mem3 = self._memobj.ch_attr[ch_num]
            # free memory bit
            is_empty |= _mem3.is_free
            # scanlists
            tmpscn = _mem3.is_scanlist1 + _mem3.is_scanlist2 * 2
            tmp_comp = list_def(_mem3.compander, COMPANDER_LIST, 0)
        elif ch_num < 214:
            att_num = 200 + int((ch_num - 200) / 2)
            _mem3 = self._memobj.ch_attr[att_num]
            is_empty |= _mem3.is_free
            tmp_comp = list_def(_mem3.compander, COMPANDER_LIST, 0)

        if is_empty:
            mem.empty = True
            # set some sane defaults:
            mem.power = UVK5_POWER_LEVELS[2]
            mem.extra = RadioSettingGroup("Extra", "extra")

            val = RadioSettingValueBoolean(False)
            rs = RadioSetting("busyChLockout", "BusyCL", val)
            mem.extra.append(rs)

            val = RadioSettingValueBoolean(False)
            rs = RadioSetting("frev", "FreqRev", val)
            mem.extra.append(rs)

            val = RadioSettingValueList(PTTID_LIST)
            rs = RadioSetting("pttid", "PTTID", val)
            mem.extra.append(rs)

            val = RadioSettingValueBoolean(False)
            rs = RadioSetting("dtmfdecode", "DTMF decode", val)
            if self._memobj.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
                mem.extra.append(rs)

            val = RadioSettingValueList(SCRAMBLER_LIST)
            rs = RadioSetting("scrambler", "Scrambler", val)
            mem.extra.append(rs)

            val = RadioSettingValueList(COMPANDER_LIST)
            rs = RadioSetting("compander", "Compander", val)
            mem.extra.append(rs)

            val = RadioSettingValueList(SCANLIST_LIST)
            rs = RadioSetting("scanlists", "Scanlists", val)
            mem.extra.append(rs)

            # actually the step and duplex are overwritten by chirp based on
            # bandplan. they are here to document sane defaults for IARU r1
            # mem.tuning_step = 25.0
            # mem.duplex = "off"

            return mem

        if ch_num > 199:
            mem.name = self._get_vfo_channel_names()[ch_num-200]
            mem.immutable = ["name", "scanlists"]
        else:
            _mem2 = self._memobj.channelname[ch_num]
            for char in _mem2.name:
                if str(char) == "\xFF" or str(char) == "\x00":
                    break
                mem.name += str(char)
            mem.name = mem.name.rstrip()

        # Convert your low-level frequency to Hertz
        mem.freq = int(_mem.freq)*10
        mem.offset = int(_mem.offset)*10

        if mem.offset == 0:
            mem.duplex = ''
        else:
            if _mem.offsetDir == FLAGS1_OFFSET_MINUS:
                if _mem.freq == _mem.offset:
                    # fake tx disable by setting tx to 0 MHz
                    mem.duplex = 'off'
                    mem.offset = 0
                else:
                    mem.duplex = '-'
            elif _mem.offsetDir == FLAGS1_OFFSET_PLUS:
                mem.duplex = '+'
            else:
                mem.duplex = ''

        # tone data
        self._get_tone(mem, _mem)

        # mode
        temp_modes = self.get_features().valid_modes
        temp_modul = _mem.modulation*2 + _mem.bandwidth
        if temp_modul < len(temp_modes):
            mem.mode = temp_modes[temp_modul]
        elif temp_modul == 5:  # USB with narrow setting
            mem.mode = temp_modes[4]
        elif temp_modul >= len(temp_modes):
            mem.mode = "UNSUPPORTED BY CHIRP"

        # tuning step
        tstep = _mem.step
        if tstep < len(STEPS):
            mem.tuning_step = STEPS[tstep]
        else:
            mem.tuning_step = 2.5

        # power
        if _mem.txpower == POWER_HIGH:
            mem.power = UVK5_POWER_LEVELS[2]
        elif _mem.txpower == POWER_MEDIUM:
            mem.power = UVK5_POWER_LEVELS[1]
        else:
            mem.power = UVK5_POWER_LEVELS[0]

        # We'll consider any blank (i.e. 0MHz frequency) to be empty
        if (_mem.freq == 0xffffffff) or (_mem.freq == 0):
            mem.empty = True
        else:
            mem.empty = False

        mem.extra = RadioSettingGroup("Extra", "extra")

        # BusyCL
        val = RadioSettingValueBoolean(_mem.busyChLockout)
        rs = RadioSetting("busyChLockout", "Busy Ch Lockout (BusyCL)", val)
        rs.set_doc('BusyCL: If the channel is Busy, do not allow TX.') 
        mem.extra.append(rs)

        # Frequency reverse
        val = RadioSettingValueBoolean(_mem.freq_reverse)
        rs = RadioSetting("frev", "Reverse Frequencies (R)", val)
        rs.set_doc('R: Is this need to be reverse ?') 
        mem.extra.append(rs)

        # PTTID
        pttid = list_def(_mem.dtmf_pttid, PTTID_LIST, 0)
        val = RadioSettingValueList(PTTID_LIST, None, pttid)
        rs = RadioSetting("pttid", "PTT ID (PTT ID)", val)
        rs.set_doc('PTT ID :  How do you want the ID to be sent or sound.\n' + \
                   '* NONE : Nothing sent\n' + \
                   '* UP CODE : Send UPCODE when TX.\n' + \
                   '* DOWW CODE : Send DWCODE when back to RX\n' + \
                   '* UP+DOWN Code : Send UPCODE and DWCODE\n' + \
                   '* APOLLO QUINDAR : Send beep at start and end of TX')
        mem.extra.append(rs)

        # DTMF DECODE
        val = RadioSettingValueBoolean(_mem.dtmf_decode)
        rs = RadioSetting("dtmfdecode", "DTMF decode (D Decd)", val)
        if self._memobj.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            mem.extra.append(rs)

        # Scrambler
        enc = list_def(_mem.scrambler, SCRAMBLER_LIST, 0)
        val = RadioSettingValueList(SCRAMBLER_LIST, None, enc)
        rs = RadioSetting("scrambler", "Scrambler (Scramb)", val)
        rs.set_doc('Scramb: How do you want scrambler on this frequency.') 
        mem.extra.append(rs)

        # Compander
        val = RadioSettingValueList(COMPANDER_LIST, None, tmp_comp)
        rs = RadioSetting("compander", "Compander (Compnd)", val)
        rs.set_doc('Compnd: How do you want Compander on this frequency.') 
        mem.extra.append(rs)

        val = RadioSettingValueList(SCANLIST_LIST, None, tmpscn)
        rs = RadioSetting("scanlists", "Scanlists (SList)", val)
        rs.set_doc('SList: Is this frequency is part of a scan list.') 
        mem.extra.append(rs)

        return mem

    def set_settings(self, settings):
        _mem = self._memobj
        for element in settings:
            if not isinstance(element, RadioSetting):
                self.set_settings(element)
                continue

            elname = element.get_name()

            # basic settings

            # VFO_A e80 ScreenChannel_A
            if elname == "VFO_A_chn":
                _mem.ScreenChannel_A = int(element.value)
                if _mem.ScreenChannel_A < 200:
                    _mem.MrChannel_A = _mem.ScreenChannel_A
                elif _mem.ScreenChannel_A < 207:
                    _mem.FreqChannel_A = _mem.ScreenChannel_A
                else:
                    _mem.NoaaChannel_A = _mem.ScreenChannel_A

            # VFO_B e83
            elif elname == "VFO_B_chn":
                _mem.ScreenChannel_B = int(element.value)
                if _mem.ScreenChannel_B < 200:
                    _mem.MrChannel_B = _mem.ScreenChannel_B
                elif _mem.ScreenChannel_B < 207:
                    _mem.FreqChannel_B = _mem.ScreenChannel_B
                else:
                    _mem.NoaaChannel_B = _mem.ScreenChannel_B

            # TX_VFO  channel selected A,B
            elif elname == "TX_VFO":
                _mem.TX_VFO = int(element.value)

            # call channel
            elif elname == "call_channel":
                _mem.call_channel = int(element.value)

            # squelch
            elif elname == "squelch":
                _mem.squelch = int(element.value)

            # TOT
            elif elname == "tot":
                _mem.max_talk_time = int(element.value)

            # NOAA autoscan
            elif elname == "noaa_autoscan":
                _mem.noaa_autoscan = int(element.value)

            # VOX
            elif elname == "vox":
                voxvalue = int(element.value)
                _mem.vox_switch = voxvalue > 0
                _mem.vox_level = (voxvalue - 1) if _mem.vox_switch else 0

            # mic gain
            elif elname == "mic_gain":
                _mem.mic_gain = int(element.value)

            # Channel display mode
            elif elname == "channel_display_mode":
                _mem.channel_display_mode = int(element.value)

            # RX Mode
            elif elname == "rx_mode":
                tmptxmode = int(element.value)
                tmpmainvfo = _mem.TX_VFO + 1
                _mem.crossband = tmpmainvfo * bool(tmptxmode & 0b10)
                _mem.dual_watch = tmpmainvfo * bool(tmptxmode & 0b01)

            # Battery Save
            elif elname == "battery_save":
                _mem.battery_save = int(element.value)

            # Backlight auto mode
            elif elname == "backlight_time":
                _mem.backlight_time = int(element.value)

            # Backlight min
            elif elname == "backlight_min":
                _mem.backlight_min = int(element.value)

            # Backlight max
            elif elname == "backlight_max":
                _mem.backlight_max = int(element.value)

            # Backlight TX_RX
            elif elname == "backlight_on_TX_RX":
                _mem.backlight_on_TX_RX = int(element.value)
            # AM_fix
            elif elname == "AM_fix":
                _mem.AM_fix = int(element.value)

            # mic_bar
            elif elname == "mem.mic_bar":
                _mem.mic_bar = int(element.value)

            # Batterie txt
            elif elname == "_mem.battery_text":
                _mem.battery_text = int(element.value)

            # Tail tone elimination
            elif elname == "ste":
                _mem.ste = int(element.value)

            # VFO Open
            elif elname == "freq_mode_allowed":
                _mem.freq_mode_allowed = int(element.value)

            # Beep control
            elif elname == "button_beep":
                _mem.button_beep = int(element.value)

            # Scan resume mode
            elif elname == "scan_resume_mode":
                _mem.scan_resume_mode = int(element.value)

            # Keypad lock
            elif elname == "key_lock":
                _mem.key_lock = int(element.value)

            # Auto keypad lock
            elif elname == "auto_keypad_lock":
                _mem.auto_keypad_lock = int(element.value)

            # Power on display mode
            elif elname == "welcome_mode":
                _mem.power_on_dispmode = int(element.value)

            # Keypad Tone
            elif elname == "voice":
                _mem.voice = int(element.value)

            elif elname == "s0_level":
                _mem.s0_level = -int(element.value)

            elif elname == "s9_level":
                _mem.s9_level = -int(element.value)

#            elif elname == "password":
#                if element.value.get_value() is None or element.value == "":
#                    _mem.password = 0xFFFFFFFF
#                else:
#                    _mem.password = int(element.value)

            # Alarm mode
            elif elname == "alarm_mode":
                _mem.alarm_mode = int(element.value)

            # Reminding of end of talk
            elif elname == "roger_beep":
                _mem.roger_beep = int(element.value)

            # Repeater tail tone elimination
            elif elname == "rp_ste":
                _mem.rp_ste = int(element.value)

            # Logo string 1
            elif elname == "logo1":
                bts = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line1 = bts[0:12]+"\x00\xff\xff\xff"

            # Logo string 2
            elif elname == "logo2":
                bts = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line2 = bts[0:12]+"\x00\xff\xff\xff"

            # unlock settings

            # FLOCK
            elif elname == "int_flock":
                _mem.int_flock = int(element.value)

            # 350TX
            elif elname == "int_350tx":
                _mem.int_350tx = int(element.value)

            # KILLED
            elif elname == "int_KILLED":
                _mem.int_KILLED = int(element.value)

            # 200TX
            elif elname == "int_200tx":
                _mem.int_200tx = int(element.value)

            # 500TX
            elif elname == "int_500tx":
                _mem.int_500tx = int(element.value)

            # 350EN
            elif elname == "int_350en":
                _mem.int_350en = int(element.value)

            # SCREN
            elif elname == "int_scren":
                _mem.int_scren = int(element.value)

            # battery type
            elif elname == "Battery_type":
                _mem.Battery_type = int(element.value)

            # set low_power f4hwn
            elif elname == "set_low":
                _mem.set_low = int(element.value)

            # set ptt f4hwn
            elif elname == "set_ptt":
                _mem.set_ptt = int(element.value)

            # set tot f4hwn
            elif elname == "set_tot":
                _mem.set_tot = int(element.value)

            # set eot f4hwn
            elif elname == "set_eot":
                _mem.set_eot = int(element.value)

            # set_contrast f4hwn
            elif elname == "set_contrast":
                _mem.set_contrast = int(element.value)

            # set inv f4hwn
            elif elname == "set_inv":
                _mem.set_inv = int(element.value)

            # set lck f4hwn
            elif elname == "set_lck":
                _mem.set_lck = int(element.value)

            # set met f4hwn
            elif elname == "set_met":
                _mem.set_met = int(element.value)

            # set gui f4hwn
            elif elname == "set_gui":
                _mem.set_gui = int(element.value)
                               
            # fm radio
            for i in range(1, 21):
                freqname = "FM_" + str(i)
                if elname == freqname:
                    val = str(element.value).strip()
                    try:
                        val2 = int(float(val)*10)
                    except Exception:
                        val2 = 0xffff

                    if val2 < FMMIN*10 or val2 > FMMAX*10:
                        val2 = 0xffff
#                        raise errors.InvalidValueError(
#                                "FM radio frequency should be a value "
#                                "in the range %.1f - %.1f" % (FMMIN , FMMAX))
                    _mem.fmfreq[i-1] = val2

            # dtmf settings
            if elname == "dtmf_side_tone":
                _mem.dtmf.side_tone = int(element.value)

            elif elname == "dtmf_separate_code":
                _mem.dtmf.separate_code = str(element.value)

            elif elname == "dtmf_group_call_code":
                _mem.dtmf.group_call_code = element.value

            elif elname == "dtmf_decode_response":
                _mem.dtmf.decode_response = int(element.value)

            elif elname == "dtmf_auto_reset_time":
                _mem.dtmf.auto_reset_time = int(element.value)

            elif elname == "dtmf_preload_time":
                _mem.dtmf.preload_time = int(int(element.value)/10)

            elif elname == "dtmf_first_code_persist_time":
                _mem.dtmf.first_code_persist_time = int(int(element.value)/10)

            elif elname == "dtmf_hash_persist_time":
                _mem.dtmf.hash_persist_time = int(int(element.value)/10)

            elif elname == "dtmf_code_persist_time":
                _mem.dtmf.code_persist_time = \
                        int(int(element.value)/10)

            elif elname == "dtmf_code_interval_time":
                _mem.dtmf.code_interval_time = \
                        int(int(element.value)/10)

            elif elname == "dtmf_permit_remote_kill":
                _mem.dtmf.permit_remote_kill = \
                        int(element.value)

            elif elname == "dtmf_dtmf_local_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*3
                _mem.dtmf.local_code = k[0:3]

            elif elname == "dtmf_dtmf_up_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf.up_code = k[0:16]

            elif elname == "dtmf_dtmf_down_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf.down_code = k[0:16]

            elif elname == "dtmf_kill_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf.kill_code = k[0:5]

            elif elname == "dtmf_revive_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf.revive_code = k[0:5]

            elif elname == "live_DTMF_decoder":
                _mem.live_DTMF_decoder = int(element.value)

            # dtmf contacts
            for i in range(1, 17):
                varname = "DTMF_" + str(i)
                if elname == varname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*8
                    _mem.dtmfcontact[i-1].name = k[0:8]

                varnumname = "DTMFNUM_" + str(i)
                if elname == varnumname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\xff"*3
                    _mem.dtmfcontact[i-1].number = k[0:3]

            # scanlist stuff
            if elname == "slDef":
                _mem.slDef = int(element.value)

            elif elname == "sl1PriorEnab":
                _mem.sl1PriorEnab = int(element.value)

            elif elname == "sl2PriorEnab":
                _mem.sl2PriorEnab = int(element.value)

            elif elname in ["sl1PriorCh1", "sl1PriorCh2", "sl2PriorCh1",
                            "sl2PriorCh2"]:
                val = int(element.value)

                if val > 200 or val < 1:
                    val = 0xff
                else:
                    val -= 1

                _mem[elname] = val

            if elname == "key1_shortpress_action":
                _mem.key1_shortpress_action = KEYACTIONS_LIST.index(element.value)

            elif elname == "key1_longpress_action":
                _mem.key1_longpress_action = KEYACTIONS_LIST.index(element.value)

            elif elname == "key2_shortpress_action":
                _mem.key2_shortpress_action = KEYACTIONS_LIST.index(element.value)

            elif elname == "key2_longpress_action":
                _mem.key2_longpress_action = KEYACTIONS_LIST.index(element.value)

            elif elname == "keyM_longpress_action":
                _mem.keyM_longpress_action = KEYACTIONS_LIST.index(element.value)

# this change to send power level chan in the calibration but under macos it give error
# bugfix calibration : remove the comment on next 2 line:
#            elif elname == "upload_calibration":
#                self._upload_calibration = bool(element.value)

            elif element.changed() and elname.startswith("_mem.cal."):
                exec(elname + " = element.value.get_value()")

    def get_settings(self):
        _mem = self._memobj
        basic = RadioSettingGroup("basic", "Basic Settings")
        advanced = RadioSettingGroup("advanced", "Advanced Settings")
        keya = RadioSettingGroup("keya", "Programmable Keys")
        dtmf = RadioSettingGroup("dtmf", "DTMF Settings")
        dtmfc = RadioSettingGroup("dtmfc", "DTMF Contacts")
        scanl = RadioSettingGroup("scn", "Scan Lists")
        unlock = RadioSettingGroup("unlock", "Unlock Settings")
        fmradio = RadioSettingGroup("fmradio", "FM Broadcast Receiver")
        calibration = RadioSettingGroup("calibration", "Calibration")
        help_user = RadioSettingGroup("help_user", "Help For User")
        
        roinfo = RadioSettingGroup("roinfo", "Driver Information + Link to get latest F4HWN driver")
        top = RadioSettings()
        top.append(basic)
        top.append(advanced)
        top.append(keya)
        top.append(dtmf)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            top.append(dtmfc)
        top.append(scanl)
        top.append(unlock)
        if _mem.BUILD_OPTIONS.ENABLE_FMRADIO:
            top.append(fmradio)
        top.append(roinfo)
        top.append(calibration)
        top.append(help_user)
        
        # helper function
        def append_label(radio_setting, label, descr=""):
            if not hasattr(append_label, 'idx'):
                append_label.idx = 0

            val = RadioSettingValueString(len(descr), len(descr), descr)
            val.set_mutable(False)
            rs = RadioSetting("label" + str(append_label.idx), label, val)
            append_label.idx += 1
            radio_setting.append(rs)

        # Programmable keys
        def get_action(action_num):
            """"get actual key action"""
            has_alarm = self._memobj.BUILD_OPTIONS.ENABLE_ALARM
            has1750 = self._memobj.BUILD_OPTIONS.ENABLE_TX1750
            has_flashlight = self._memobj.BUILD_OPTIONS.ENABLE_FLASHLIGHT

            has_backlight_off = self._memobj.BUILD_OPTIONS.ENABLE_BLMIN_TMP_OFF
            
            lst = KEYACTIONS_LIST.copy()
            if not has_alarm:
                lst.remove("ALARM")
            if not has1750:
                lst.remove("1750Hz TONE")
            if not has_flashlight:
                lst.remove("FLASHLIGHT")
            if not has_backlight_off:
                lst.remove("Put the backlight OFF temporarily (BL_MIN_TMP_OFF)")

            action_num = int(action_num)
            if action_num >= len(KEYACTIONS_LIST) or \
               KEYACTIONS_LIST[action_num] not in lst:
                action_num = 0
            return lst, KEYACTIONS_LIST[action_num]

        val1s = RadioSettingValueList(*get_action(_mem.key1_shortpress_action))
        rs = RadioSetting("key1_shortpress_action",
                          "Side key 1 short press (F1Shrt)", val1s)
        rs.set_doc('F1Shrt: Select the action to do when pressing F1 key for a ' + \
                   'SHORT time, F1 key is located on the left side, first key under PTT')
        keya.append(rs)

        val1l = RadioSettingValueList(*get_action(_mem.key1_longpress_action))
        rs = RadioSetting("key1_longpress_action",
                          "Side key 1 long press (F1Long)", val1l)
        rs.set_doc('F1Long: Select the action to do when pressing F1 key for a ' + \
                   'LONG time, F1 key is located on the left side, first key under PTT ')
        keya.append(rs)

        val2s = RadioSettingValueList(*get_action(_mem.key2_shortpress_action))
        rs = RadioSetting("key2_shortpress_action",
                          "Side key 2 short press (F2Shrt)", val2s)
        rs.set_doc('F2Shrt: Select the action to do when pressing F2 key for a ' + \
                   'SHORT time, F2 key is located on the left side, second key under PTT ')
        keya.append(rs)

        val2l = RadioSettingValueList(*get_action(_mem.key2_longpress_action))
        rs = RadioSetting("key2_longpress_action",
                          "Side key 2 long press (F2Long)", val2l)
        rs.set_doc('F2Long: Select the action to do when pressing F2 key for a ' + \
                   'LONG time, F2 key is located on the left side, second key under PTT ')
        keya.append(rs)

        valm = RadioSettingValueList(*get_action(_mem.keyM_longpress_action))
        rs = RadioSetting("keyM_longpress_action",
                          "Menu key long press (M Long)", valm)
        rs.set_doc('M Long: Select the action to do when pressing M key for a ' + \
                   'LONG time, M key is located below the screen on the left.')
        keya.append(rs)

        # ----------------- DTMF settings

        tmpval = str(_mem.dtmf.separate_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '*'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        sep_code_setting = RadioSetting("dtmf_separate_code",
                                        "Separate Code", val)
        sep_code_setting.set_doc('Separate Code: ')

        tmpval = str(_mem.dtmf.group_call_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '#'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        group_code_setting = RadioSetting("dtmf_group_call_code",
                                          "Group Call Code", val)
        group_code_setting.set_doc('Group Call Code: ')

        tmpval = min_max_def(_mem.dtmf.first_code_persist_time * 10,
                             30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        first_code_per_setting = \
            RadioSetting("dtmf_first_code_persist_time",
                         "First code persist time (ms)", val)
        first_code_per_setting.set_doc('First code persist time: How long to you want the first DTMF ' + \
                                       'will be sent in milisecond')

        tmpval = min_max_def(_mem.dtmf.hash_persist_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        spec_per_setting = RadioSetting("dtmf_hash_persist_time",
                                        "#/* persist time (ms)", val)
        spec_per_setting.set_doc('#/* persist time: How long this code # or / or * will be sent in milisecond')
        
        tmpval = min_max_def(_mem.dtmf.code_persist_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        code_per_setting = RadioSetting("dtmf_code_persist_time",
                                        "Code persist time (ms)", val)
        code_per_setting.set_doc('Code persist time: How long the code will be sent in milisecond')

        tmpval = min_max_def(_mem.dtmf.code_interval_time * 10, 30, 1000, 300)
        val = RadioSettingValueInteger(30, 1000, tmpval, 10)
        code_int_setting = RadioSetting("dtmf_code_interval_time",
                                        "Code interval time (ms)", val)
        code_int_setting.set_doc('Code interval time: How long to wait between each code sent in milisecond ')

        tmpval = str(_mem.dtmf.local_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_ID:
                continue
            tmpval = "103"
            break
        val = RadioSettingValueString(3, 3, tmpval)
        val.set_charset(DTMF_CHARS_ID)
        ani_id_setting = \
            RadioSetting("dtmf_dtmf_local_code",
                         "Local code (3 chars 0-9 ABCD) (ANI ID)", val)
        ani_id_setting.set_doc('ANI ID: DTMF communication radio ID ')                         

        tmpval = str(_mem.dtmf.up_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN or i == "":
                continue
            else:
                tmpval = "123"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        up_code_setting = \
            RadioSetting("dtmf_dtmf_up_code",
                         "Up code (1-16 chars 0-9 ABCD*#) (UPCode)", val)
        up_code_setting.set_doc('UPCode: DTMF code that is sent at the beginning of transmission ')

        tmpval = str(_mem.dtmf.down_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN:
                continue
            else:
                tmpval = "456"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        dw_code_setting = \
            RadioSetting("dtmf_dtmf_down_code",
                         "Down code (1-16 chars 0-9 ABCD*#) (DWCode)", val)
        dw_code_setting.set_doc('DWCode: DTMF code that is sent at the end of a transmission ')

        val = RadioSettingValueBoolean(_mem.dtmf.side_tone)
        dtmf_side_tone_setting = \
            RadioSetting("dtmf_side_tone",
                         "DTMF Sidetone on speaker when sent (D ST)", val)
        dtmf_side_tone_setting.set_doc('D ST: DTMF side tone switch, lets you hear transmitted  ' + \
                                       'tones in the radio speaker ')

        tmpval = list_def(_mem.dtmf.decode_response,
                          DTMF_DECODE_RESPONSE_LIST, 0)
        val = RadioSettingValueList(DTMF_DECODE_RESPONSE_LIST, None, tmpval)
        dtmf_resp_setting = RadioSetting("dtmf_decode_response",
                                         "Decode Response (D Resp)", val)
        dtmf_resp_setting.set_doc('D Resp: DTMF decoding response ')

        tmpval = min_max_def(_mem.dtmf.auto_reset_time, 5, 60, 10)
        val = RadioSettingValueInteger(5, 60, tmpval)
        d_hold_setting = RadioSetting("dtmf_auto_reset_time",
                                      "Auto reset time (s) (D Hold)", val)
        d_hold_setting.set_doc('D Hold: DTMF auto reset time ')

        # D Prel
        tmpval = min_max_def(_mem.dtmf.preload_time * 10, 30, 990, 300)
        val = RadioSettingValueInteger(30, 990, tmpval, 10)
        d_prel_setting = RadioSetting("dtmf_preload_time",
                                      "Pre-load time (ms) (D Prel)", val)
        d_prel_setting.set_doc('D Prel: DTMF pre-load time ')
        
        # D LIVE
        val = RadioSettingValueBoolean(_mem.live_DTMF_decoder)
        d_live_setting = \
            RadioSetting("live_DTMF_decoder", "Displays DTMF codes"
                         " received in the middle of the screen (D Live)", val)
        d_live_setting.set_doc('D Live: Displays DTMF codes received by radio in the middle of the screen ')
        
        val = RadioSettingValueBoolean(_mem.dtmf.permit_remote_kill)
        perm_kill_setting = RadioSetting("dtmf_permit_remote_kill",
                                         "Permit remote kill", val)

        tmpval = str(_mem.dtmf.kill_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "77777"
                break
        if not len(tmpval) == 5:
            tmpval = "77777"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        kill_code_setting = RadioSetting("dtmf_kill_code",
                                         "Kill code (5 chars 0-9 ABCD)", val)

        tmpval = str(_mem.dtmf.revive_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "88888"
                break
        if not len(tmpval) == 5:
            tmpval = "88888"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rev_code_setting = RadioSetting("dtmf_revive_code",
                                        "Revive code (5 chars 0-9 ABCD)", val)

        val = RadioSettingValueBoolean(_mem.int_KILLED)
        killed_setting = RadioSetting("int_KILLED", "DTMF kill lock", val)

        # ----------------- DTMF Contacts

        append_label(dtmfc, "DTMF Contacts  (D List)",
                     "All DTMF Contacts are 3 codes "
                     "(valid: 0-9 * # ABCD), "
                     "or an empty string")

        for i in range(1, 17):
            varname = "DTMF_"+str(i)
            varnumname = "DTMFNUM_"+str(i)
            vardescr = "DTMF Contact "+str(i)+" name"
            varinumdescr = "DTMF Contact "+str(i)+" number"

            cntn = str(_mem.dtmfcontact[i-1].name).strip("\x20\x00\xff")
            cntnum = str(_mem.dtmfcontact[i-1].number).strip("\x20\x00\xff")

            val = RadioSettingValueString(0, 8, cntn)
            rs = RadioSetting(varname, vardescr, val)
            dtmfc.append(rs)

            val = RadioSettingValueString(0, 3, cntnum)
            val.set_charset(DTMF_CHARS)
            rs = RadioSetting(varnumname, varinumdescr, val)
            dtmfc.append(rs)

        # ----------------- Scan Lists

        tmpscanl = list_def(_mem.slDef, SCANLIST_SELECT_LIST, 0)
        val = RadioSettingValueList(SCANLIST_SELECT_LIST, None, tmpscanl)
        rs = RadioSetting("slDef", "Default scan lists (SList)", val)
        rs.set_doc('SList: Selects which lists are used by the memory scan\n' + \
                    '* ALL: All lists\n' + \
                    '* LIST1: List 1 only\n' + \
                    '* LIST2: List 2 only')
        scanl.append(rs)

        val = RadioSettingValueBoolean(_mem.sl1PriorEnab)
        rs = RadioSetting("sl1PriorEnab", "List 1 priority channel scan", val)
        rs.set_doc('List 1 priority: Is this list has priority ')
        scanl.append(rs)

        ch_list = ["None"]
        for ch in range(1, 201):
            ch_list.append("Channel M" + str(ch))

        tmpch = list_def(_mem.sl1PriorCh1 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl1PriorCh1", "List 1 priority channel 1", val)
        rs.set_doc('List 1 priority channel 1: Select the channel you want for priority ')        
        scanl.append(rs)

        tmpch = list_def(_mem.sl1PriorCh2 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl1PriorCh2", "List 1 priority channel 2", val)
        rs.set_doc('List 1 priority channel 2: Select the channel you want for priority ')
        scanl.append(rs)

        val = RadioSettingValueBoolean(_mem.sl2PriorEnab)
        rs = RadioSetting("sl2PriorEnab", "List 2 priority channel scan", val)
        rs.set_doc('List 2 priority: Is this list as priority ')
        scanl.append(rs)

        tmpch = list_def(_mem.sl2PriorCh1 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl2PriorCh1", "List 2 priority channel 1", val)
        rs.set_doc('List 2 priority channel 1: Select the channel you want for priority ')
        scanl.append(rs)

        tmpch = list_def(_mem.sl2PriorCh2 + 1, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpch)
        rs = RadioSetting("sl2PriorCh2", "List 2 priority channel 2", val)
        rs.set_doc('List 2 priority channel 2: Select the channel you want for priority ')
        scanl.append(rs)

        # ----------------- Basic settings

        ch_list = []
        for ch in range(1, 201):
            ch_list.append("Channel M" + str(ch))
        for bnd in range(1, 8):
            ch_list.append("Band F" + str(bnd))
        if _mem.BUILD_OPTIONS.ENABLE_NOAA:
            for bnd in range(1, 11):
                ch_list.append("NOAA N" + str(bnd))

        tmpfreq0 = list_def(_mem.ScreenChannel_A, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpfreq0)
        freq0_setting = RadioSetting("VFO_A_chn",
                                     "VFO A current channel/band", val)
        freq0_setting.set_doc('VFO A current channel/band: To select what is it displayed on the VFO A\n' + \
                              '* CHANNEL number M1-M200\n' + \
                              '* BAND F1-F7\n' + \
                              'look at the memory tab to view what is program their ')

        tmpfreq1 = list_def(_mem.ScreenChannel_B, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpfreq1)
        freq1_setting = RadioSetting("VFO_B_chn",
                                      "VFO B current channel/band", val)
        freq1_setting.set_doc('VFO B current channel/band: To select what is in the VFO B\n' + \
                              '* CHANNEL number M1-M200\n' + \
                              '* BAND F1-F7\n' + \
                              'look in memory tab to view to see which memories are already programmed')

        tmptxvfo = list_def(_mem.TX_VFO, TX_VFO_LIST, 0)
        val = RadioSettingValueList(TX_VFO_LIST, None, tmptxvfo)
        tx_vfo_setting = RadioSetting("TX_VFO", "Main VFO", val)
        tx_vfo_setting.set_doc('Main VFO: To select which VFO is active, ' + \
                               '( A is on TOP, B is on the BOTTOM ) ')
        val = RadioSettingValueBoolean(False)

        def validate_upload_f4hwn(value):
            return value

        val.set_validate_callback(validate_upload_f4hwn)
        Upload_f4hwn = RadioSetting("upload_f4hwn",
                                     "Upload F4HWN's settings to radio", val)
        Upload_f4hwn.set_doc('This section of settings is in a different memory space, ' + \
                             'so it needs to be uploaded to radio separately. Check this case to ' + \
                             'upload ONLY all the sections of F4HWN\'s settings to radio. ' + \
                             'It will be very fast to upload, then the radio will reboot.\n' + \
                             'After uploading, uncheck the box to be able to upload all other settings.')
        self.upload_f4hwn = val
                                     
        # Set_Low_Power f4hwn
        tmpsetlow = list_def(_mem.set_low, SET_LOW_LIST, 0)
        val = RadioSettingValueList(SET_LOW_LIST, SET_LOW_LIST[tmpsetlow])
        SetLowSetting = RadioSetting("set_low", "Low Power Value [SetLow]", val)
        SetLowSetting.set_doc('SetLow: TX power when [TxPwr] is set to low.\n' + \
                              '(see also the "Power" column in the memories tab to set the TX level for each channel), ' + \
                              'the low level will use this TX power level ')
        
        # Set_Ptt f4hwn
        tmpsetptt = list_def(_mem.set_ptt, SET_PTT_LIST, 0)
        val = RadioSettingValueList(SET_PTT_LIST, SET_PTT_LIST[tmpsetptt])
        SetPttSetting = RadioSetting("set_ptt", "Ptt Mode: Set PTT Key Operating Mode [SetPtt]", val)
        SetPttSetting.set_doc('SetPtt :\n' + \
                              '* CLASSIC : press and hold to transmit, release to stop the transmission.\n' + \
                              '* ONEPUSH : press once to transmit, no need to hold.\n' + \
                              '                 Simply press once to start transmission, and press a second time to stop.\n' + \
                              ' No more finger cramps :) ')

        # Set_tot f4hwn
        tmpsettot = list_def(_mem.set_tot, SET_TOT_EOT_LIST, 0)
        val = RadioSettingValueList(SET_TOT_EOT_LIST, SET_TOT_EOT_LIST[tmpsettot])
        SetTotSetting = RadioSetting("set_tot", "Set TX Timeout Indicator [SetTot]", val)
        SetTotSetting.set_doc('SetTot: Indication of the TX timeout\n' + \
                                '* NONE : no information\n' + \
                                '* SOUND : audio information\n' + \
                                '* VISUAL : screen blinking\n' + \
                                '* ALL : audio and screen blinking')

        # Set_eot f4hwn
        tmpseteot = list_def(_mem.set_eot, SET_TOT_EOT_LIST, 0)
        val = RadioSettingValueList(SET_TOT_EOT_LIST, SET_TOT_EOT_LIST[tmpseteot])
        SetEotSetting = RadioSetting("set_eot", "Set End Of Transmission Indicator [SetEot]", val)
        SetEotSetting.set_doc('SetEot: End Of Transmission indication\n' + \
                                '* NONE : no information\n' + \
                                '* SOUND : audio information\n' + \
                                '* VISUAL : screen blinking\n' + \
                                '* ALL : audio and screen blinking')

        # Set_contrast f4hwn
        tmpcontrast = min_max_def(_mem.set_contrast, 0, 15, 11)
        val = RadioSettingValueInteger(0, 15, tmpcontrast)
        contrastSetting = RadioSetting("set_contrast", "Set Contrast Level [SetCtr]", val)
        contrastSetting.set_doc('SetCtr: Set the display contrast level from 0 to 15, default is 10')
       
        # Set_inv f4hwn
        tmpsetinv = list_def(_mem.set_inv, SET_OFF_ON_LIST, 0)
        val = RadioSettingValueList(SET_OFF_ON_LIST, SET_OFF_ON_LIST[tmpsetinv])
        SetInvSetting = RadioSetting("set_inv", "Invert Display [SetInv]", val)
        SetInvSetting.set_doc('SetInv: black text on light background or light text on black background\n' + \
                              '* OFF : black text (default)\n' + \
                              '* ON : light text')

        # Set_lck, uses
        tmpsetlck = list_def(_mem.set_lck, SET_LCK_LIST, 0)
        val = RadioSettingValueList(SET_LCK_LIST, SET_LCK_LIST[tmpsetlck])
        SetLckSetting = RadioSetting("set_lck", "Lock PTT Key When Keypad Is Locked [SetLck]", val)
        SetLckSetting.set_doc('SetLck: When the keypad is locked, lock also the PTT key')
        
        # Set_met f4hwn
        tmpsetmet = list_def(_mem.set_met, SET_MET_LIST, 0)
        val = RadioSettingValueList(SET_MET_LIST, SET_MET_LIST[tmpsetmet])
        SetMetSetting = RadioSetting("set_met", "S-Meter Display Style [SetMet]", val)
        SetMetSetting.set_doc('SetMet: Change the style of the S-meter display\n' + \
                              '* CLASSIC : classic display\n' + \
                              '* TINY : smaller display')

        # Set_gui f4hwn
        tmpsetgui = list_def(_mem.set_gui, SET_MET_LIST, 0)
        val = RadioSettingValueList(SET_MET_LIST, SET_MET_LIST[tmpsetgui])
        SetGuiSetting = RadioSetting("set_gui", "Display Text Style [SetGui]", val)
        SetGuiSetting.set_doc('SetGui: Change the display text style\n' + \
                              '* CLASSIC : normal font\n' + \
                              '* TINY : smaller font')

        tmpsq = min_max_def(_mem.squelch, 0, 9, 1)
        val = RadioSettingValueInteger(0, 9, tmpsq)
        squelch_setting = RadioSetting("squelch", "Squelch [Sql]", val)
        squelch_setting.set_doc('Sql: Squelch sensitivity level from 0 to 9, 0 to disable squelch')
        
        ch_list = []
        for ch in range(1, 201):
            ch_list.append("Channel M" + str(ch))

        tmpc = list_def(_mem.call_channel, ch_list, 0)
        val = RadioSettingValueList(ch_list, None, tmpc)
        call_channel_setting = RadioSetting("call_channel", "One-Key Call Channel [1 Call]", val)
        call_channel_setting.set_doc('1 Call: One-key call channel, lets you quickly switch to the ' + \
                                     'designed channel with the "9 Call" key ')

        val = RadioSettingValueBoolean(_mem.key_lock)
        keypad_lock_setting = RadioSetting("key_lock", "Keypad Locked", val)
        keypad_lock_setting.set_doc('Keypad locked: Lock the keypad now')
        
        tmpval = list_def(_mem.auto_keypad_lock, AUTO_KEYPAD_LOCK_LIST, 1)
        val = RadioSettingValueList(AUTO_KEYPAD_LOCK_LIST, None, tmpval)
        auto_keypad_lock_setting = RadioSetting("auto_keypad_lock", "Auto Lock Keypad After Inactivity (≈15s) [KeyLck]", val)
        auto_keypad_lock_setting.set_doc('KeyLck: Keypad lock\n' + \
                                         '* AUTO : After ≈15s of inactivity\n' + \
                                         '* OFF : No keypad lock')
        
        tmptot = list_def(_mem.max_talk_time,  TALK_TIME_LIST, 1)
        val = RadioSettingValueList(TALK_TIME_LIST, None, tmptot)
        tx_t_out_setting = RadioSetting("tot", "Max TX Timeout [TxTOut]", val)
        tx_t_out_setting.set_doc('TxTOut: Select the TX time limit\n' + \
                                 'See option [SetTot] of F4HWN\'s firmware')

        tmpbatsave = list_def(_mem.battery_save, BATSAVE_LIST, 4)
        val = RadioSettingValueList(BATSAVE_LIST, None, tmpbatsave)
        bat_save_setting = RadioSetting("battery_save", "Battery Saver [BatSav]", val)
        bat_save_setting.set_doc('BatSav: Battery saver option, ratio between active time and sleep time')
        
        val = RadioSettingValueBoolean(_mem.noaa_autoscan)
        noaa_auto_scan_setting = RadioSetting("noaa_autoscan", "NOAA Autoscan (NOAA-S)", val)
        noaa_auto_scan_setting.set_doc('NOAA-S: ')
        
        tmpmicgain = list_def(_mem.mic_gain, MIC_GAIN_LIST, 2)
        val = RadioSettingValueList(MIC_GAIN_LIST, None, tmpmicgain)
        mic_gain_setting = RadioSetting("mic_gain", "Mic Gain [Mic]", val)
        mic_gain_setting.set_doc('Mic: Set the microphone sensitivity level (Gain)')
        
        val = RadioSettingValueBoolean(_mem.mic_bar)
        mic_bar_setting = RadioSetting("mic_bar", "Microphone Level Bar Display [MicBar]", val)
        mic_bar_setting.set_doc('MicBar: Display the microphone level bar while transmitting')

        tmpchdispmode = list_def(_mem.channel_display_mode,
                                 CHANNELDISP_LIST, 0)
        val = RadioSettingValueList(CHANNELDISP_LIST, None, tmpchdispmode)
        ch_disp_setting = RadioSetting("channel_display_mode", "Channel Display Mode [ChDisp]", val)
        ch_disp_setting.set_doc('ChDisp: What to display on screen:\n' + \
                                '* NAME\n' + \
                                '* CHANNEL NUMBER\n' + \
                                '* FREQ\n' + \
                                '* NAME + FREQ')

        tmpdispmode = list_def(_mem.power_on_dispmode, WELCOME_LIST, 0)
        val = RadioSettingValueList(WELCOME_LIST, None, tmpdispmode)
        p_on_msg_setting = RadioSetting("welcome_mode", "Power On Display Message [POnMsg]", val)
        p_on_msg_setting.set_doc('POnMsg: When powering up the radio, what to display:\n' + \
                                 '* ALL : message line 1 + voltage + sound\n' + \
                                 '* SOUND : beep beep 2 only\n' + \
                                 '* MESSAGE : message lines 1 and 2 only\n' + \
                                 '* VOLTAGE : battery voltage only\n' + \
                                 '* NONE : nothing')

        logo1 = str(_mem.logo_line1).strip("\x20\x00\xff") + "\x00"
        logo1 = _getstring(logo1.encode('ascii', errors='ignore'), 0, 12)
        val = RadioSettingValueString(0, 12, logo1)
        logo1_setting = RadioSetting("logo1", "Message Line 1 (12 characters max)", val)
        logo1_setting.set_doc('Message line 1: The first message line,\n' + \
                              'with a maximum of 12 characters\n' + \
                              'See option [POnMsg] to display it')
                               
        logo2 = str(_mem.logo_line2).strip("\x20\x00\xff") + "\x00"
        logo2 = _getstring(logo2.encode('ascii', errors='ignore'), 0, 12)
        val = RadioSettingValueString(0, 12, logo2)
        logo2_setting = RadioSetting("logo2", "Message Line 2 (12 characters max)", val)
        logo2_setting.set_doc('Message line 2: the second message line,\n' + \
                              'with a maximum of 12 characters\n' + \
                              'See option [POnMsg] to display it')

        tmpbattxt = list_def(_mem.battery_text, BAT_TXT_LIST, 2)
        val = RadioSettingValueList(BAT_TXT_LIST, None, tmpbattxt)
        bat_txt_setting = RadioSetting("battery_text", "Battery Level Display [BatTXT]", val)
        bat_txt_setting.set_doc('BatTXT: Display additional battery info on the status bar\n' + \
                                '* PERCENT : Percentage of remaining power\n' + \
                                '* VOLTAGE : Voltage\n' + \
                                '* NONE : Nothing')

        tmpback = list_def(_mem.backlight_time, BACKLIGHT_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_LIST, None, tmpback)
        back_lt_setting = RadioSetting("backlight_time", "Backlight Time [BLTime]", val)
        back_lt_setting.set_doc('BLTime: Backlight duration, how long the backlight will stay on\n' + \
                                'after the end of an action')

        tmpback = list_def(_mem.backlight_min, BACKLIGHT_LVL_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_LVL_LIST, None, tmpback)
        bl_min_setting = RadioSetting("backlight_min", "Minimum Backlight Level [BLMin]", val)
        bl_min_setting.set_doc('BLMin: Minimum backlight brightness, when the screen backlight turns off\n' + \
                               'it will dim to this value')

        tmpback = list_def(_mem.backlight_max, BACKLIGHT_LVL_LIST, 10)
        val = RadioSettingValueList(BACKLIGHT_LVL_LIST, None, tmpback)
        bl_max_setting = RadioSetting("backlight_max", "Maximum Backlight Level [BLMax]", val)
        bl_max_setting.set_doc('BLMax: Maximum backlight brightness, when the screen backlight turns on\n' + \
                               'it will light up to this value')
        
        tmpback = list_def(_mem.backlight_on_TX_RX, BACKLIGHT_TX_RX_LIST, 0)
        val = RadioSettingValueList(BACKLIGHT_TX_RX_LIST, None, tmpback)
        blt_trx_setting = RadioSetting("backlight_on_TX_RX", "Backlight on TX/RX [BLTxRx]", val)
        blt_trx_setting.set_doc('BLTxRx : Backlight activation on TX or RX or both TX and RX or no backlight at all\n' + \
                                '* OFF : OFF in all cases\n' + \
                                '* TX : turn ON when TX only\n' + \
                                '* RX : ON when RX only\n' + \
                                '* TX/RX : ON when TX and RX')
        
        val = RadioSettingValueBoolean(_mem.button_beep)
        beep_setting = RadioSetting("button_beep", "Keypad Beep [Beep]", val)
        beep_setting.set_doc('Beep: Beep sound when a key is pressed')

        tmpalarmmode = list_def(_mem.roger_beep, ROGER_LIST, 0)
        val = RadioSettingValueList(ROGER_LIST, None, tmpalarmmode)
        roger_setting = RadioSetting("roger_beep", "End Of Transmission Beep [Roger]", val)
        roger_setting.set_doc('Roger: Squelch tail eliminator, eliminates noise at the end of a transmission')

        val = RadioSettingValueBoolean(_mem.ste)
        ste_setting = RadioSetting("ste", "Squelch Tail Elimination [STE]", val)
        ste_setting.set_doc('STE: Squelch tail eliminator, eliminates noise at the end of a transmission')

        tmprte = list_def(_mem.rp_ste, RTE_LIST, 0)
        val = RadioSettingValueList(RTE_LIST, None, tmprte)
        rp_ste_setting = RadioSetting("rp_ste", "Repeater Squelch Tail Elimination [RP STE]", val)
        rp_ste_setting.set_doc('RP STE: Repeater squelch tail eliminator')

        val = RadioSettingValueBoolean(_mem.AM_fix)
        am_fix_setting = RadioSetting("AM_fix", "AM Reception Fix [AM Fix]", val)
        am_fix_setting.set_doc('AM Fix: Activates autogain in AM reception')

        tmpvox = min_max_def((_mem.vox_level + 1) * _mem.vox_switch, 0, 10, 0)
        val = RadioSettingValueList(VOX_LIST, None, tmpvox)
        vox_setting = RadioSetting("vox", "Voice-Operated Switch [VOX]", val)
        vox_setting.set_doc('VOX: Voice TX activation sensitivity level')
        
        tmprxmode = list_def((bool(_mem.crossband) << 1)
                             + bool(_mem.dual_watch),
                             RXMODE_LIST, 0)
        val = RadioSettingValueList(RXMODE_LIST, None, tmprxmode)
        rx_mode_setting = RadioSetting("rx_mode", "RX Mode [RxMode]", val)
        rx_mode_setting.set_doc('RxMode:\n' + \
                                '* MAIN ONLY : Transmits and listens on the main frequency\n' + \
                                '* DUAL RX RESPOND : Listens both frequencies, if signal received on the secondary frequency, it locks to \n' + \
                                'it for a couple of seconds so you can respond to the call (DWR)\n' + \
                                '* CROSS BAND : Always transmits on the primary and listens on the secondary frequency (XB)\n' + \
                                '* MAIN TX DUAL RX : Always transmits on the primary, listens to both (DW)')

        val = RadioSettingValueBoolean(_mem.freq_mode_allowed)
        freq_mode_allowed_setting = RadioSetting("freq_mode_allowed", "Frequency Mode Allowed", val)
        freq_mode_allowed_setting.set_doc('Frequency mode allowed')

        tmpscanres = list_def(_mem.scan_resume_mode, SCANRESUME_LIST, 0)
        val = RadioSettingValueList(SCANRESUME_LIST, None, tmpscanres)
        scn_rev_setting = RadioSetting("scan_resume_mode", "Scan Resume Mode [ScnRev]", val)
        scn_rev_setting.set_doc('ScnRev: Scan Resume Mode\n' + \
                                '* CARRIER : Resume scan after signal disappears\n' + \
                                '* TIMEOUT : Resume scan after 5 seconds pause\n' + \
                                '* STOP : After receiving a signal, stop the scan')
        
        tmpvoice = list_def(_mem.voice, VOICE_LIST, 0)
        val = RadioSettingValueList(VOICE_LIST, None, tmpvoice)
        voice_setting = RadioSetting("voice", "Voice", val)
        voice_setting.set_doc('Voice: Voice announcement\n' + \
                                '* NONE : No voice\n' + \
                                '* CHINA : Chinese voice\n' + \
                                '* ENGLISH : English voice')

        tmpalarmmode = list_def(_mem.alarm_mode, ALARMMODE_LIST, 0)
        val = RadioSettingValueList(ALARMMODE_LIST, None, tmpalarmmode)
        alarm_setting = RadioSetting("alarm_mode", "Alarm Mode", val)

        # ----------------- Extra settings

        # S-meter
        tmp_s0 = -int(_mem.s0_level)
        tmp_s9 = -int(_mem.s9_level)

        if tmp_s0 not in range(-200, -91) or tmp_s9 not in range(-160, -51) \
           or tmp_s9 < tmp_s0+9:

            tmp_s0 = -130
            tmp_s9 = -76
        val = RadioSettingValueInteger(-200, -90, tmp_s0)
        s0_level_setting = RadioSetting("s0_level", "S-Meter S0 Level (dBm)", val)
        s0_level_setting.set_doc('S-meter S0 level (dBm): To set the level calibration for S0')

        val = RadioSettingValueInteger(-160, -50, tmp_s9)
        s9_level_setting = RadioSetting("s9_level", "S-Meter S9 Level (dBm)", val)
        s9_level_setting.set_doc('S-meter S9 level (dBm): To set the level calibration for S9')

        # Battery Type
        tmpbtype = list_def(_mem.Battery_type, BATTYPE_LIST, 0)
        val = RadioSettingValueList(BATTYPE_LIST, BATTYPE_LIST[tmpbtype])
        bat_type_setting = RadioSetting("Battery_type", "Battery Type [BatTyp]", val)
        bat_type_setting.set_doc('BatTyp: What type of battery the radio is using, this affect\n' + \
                                 'the level value of the battery on the display')

        # Power on password
#        def validate_password(value):
#            value = value.strip(" ")
#            if value.isdigit():
#                return value.zfill(6)
#            if value != "":
#                raise InvalidValueError("Power on password "
#                                        "can only have digits")
#            return ""

#        pswd_str = str(int(_mem.password)).zfill(6) \
#            if _mem.password < 1000000 else ""
#        val = RadioSettingValueString(0, 6, pswd_str)
#        val.set_validate_callback(validate_password)
#        pswd_setting = RadioSetting("password", "Power on password", val)

        # ----------------- FM radio

        append_label(fmradio, "Channel Memory Radio (MR)", "Frequency (MHz)")

        for i in range(1, 21):
            fmfreq = _mem.fmfreq[i-1]/10.0
            freq_name = str(fmfreq)
            if fmfreq < FMMIN or fmfreq > FMMAX:
                freq_name = ""
            rs = RadioSetting("FM_" + str(i), "Ch " + str(i),
                              RadioSettingValueString(0, 5, freq_name))
            rs.set_doc('FM Broadcast frequency: Enter the frequency in MHz, example: 96.9\n' + \
                       'To listen the FM Broadcast band, Long press the 5 key, then if you want to scan for\n' + \
                       'stations around, press *. Scan result will erase the existing FM broadcast list.')
            fmradio.append(rs)

        # ----------------- Unlock settings

        # F-LOCK
        def validate_int_flock(value):
            mem_val = self._memobj.int_flock
            if mem_val != 7 and value == FLOCK_LIST[7]:
                msg = "\"" + value + "\" can only be enabled from radio menu"
                raise InvalidValueError(msg)
            return value

        tmpflock = list_def(_mem.int_flock, FLOCK_LIST, 0)
        val = RadioSettingValueList(FLOCK_LIST, None, tmpflock)
        val.set_validate_callback(validate_int_flock)
        f_lock_setting = RadioSetting("int_flock", "TX Frequency Lock [F Lock]", val)
        f_lock_setting.set_doc('F Lock: Sets the TX frequency band plan')

        val = RadioSettingValueBoolean(_mem.int_200tx)
        tx200_setting = RadioSetting("int_200tx", "Unlock 174-350 MHz TX [Tx 200]", val)
        tx200_setting.set_doc('Enables transmission on 200 MHz')

        val = RadioSettingValueBoolean(_mem.int_350tx)
        tx350_setting = RadioSetting("int_350tx", "Unlock 350-400 MHz TX [Tx 350]", val)
        tx350_setting.set_doc('Enables transmission on 350 MHz')
        
        val = RadioSettingValueBoolean(_mem.int_500tx)
        tx500_setting = RadioSetting("int_500tx", "Unlock 500-600 MHz TX [Tx 500]", val)
        tx500_setting.set_doc('Enables transmission on 500 MHz')
        
        val = RadioSettingValueBoolean(_mem.int_350en)
        en350_setting = RadioSetting("int_350en", "Unlock 350-400 MHz RX [350 En]", val)
        en350_setting.set_doc('Enables reception on 350 MHz')
        
        val = RadioSettingValueBoolean(_mem.int_scren)
        en_scrambler_setting = RadioSetting("int_scren", "Scrambler Enabled [ScraEn]", val)
        en_scrambler_setting.set_doc('Enables Scrambler')
        
        # ----------------- Driver Info

        if self.FIRMWARE_VERSION == "":
            firmware = "To get the firmware version please download " \
                       "the image from the radio first"
        else:
            firmware = self.FIRMWARE_VERSION

        append_label(roinfo,
                     "=" * 6 + " Firmware F4HWN " + "=" * 300, "=" * 300)

        append_label(roinfo, "Firmware Version", firmware)
        val = RadioSettingValueString(0,75,FIRMWARE_DRIVER_VERSION_UPDATE)
        rs = RadioSetting("Update","Latest F4HWN firmware" + ", copy link (CTRL-C), paste (CTRL-V) to your browser -> ", val)
        rs.set_doc('Be sure you have the latest firmware available!')
        roinfo.append(rs)
        
        append_label(roinfo,
                     "=" * 6 + " Chirp Driver F4HWN " + "=" * 300, "=" * 300)
                     
        append_label(roinfo, "Driver Chirp Version", DRIVER_VERSION)
        val = RadioSettingValueString(0,75,CHIRP_DRIVER_VERSION_UPDATE)
        rs = RadioSetting("Update1","Latest Driver " + self.MODEL + ", copy link (CTRL-C), paste (CTRL-V) to your browser -> ", val)
        rs.set_doc('Be sure you have the latest CHIRP driver available!')
        roinfo.append(rs)

        append_label(roinfo,
                     "=" * 6 + "=" * 300, "=" * 300)

        append_label(roinfo, "The driver module is done by VE2ZJM", )

        append_label(roinfo,
                     "=" * 6 + " Special Thank to : " + "=" * 300, "=" * 300)

        append_label(roinfo, "The french translation was done by FLIXX", )

                
        # ----------------- Calibration

        val = RadioSettingValueBoolean(False)

        def validate_upload_calibration(value):
            if value and not self.upload_calibration:
                msg = "This option may break your radio!!!\n" \
                    "You are doing this at your own risk.\n" \
                    "Make sure you have a working calibration backup.\n" \
                    "Don't use it unless you know what you're doing."
                ret = wx.MessageBox(msg, "Warning", wx.OK | wx.CANCEL |
                                    wx.CANCEL_DEFAULT | wx.ICON_WARNING)
                value = ret == wx.OK
            self.upload_calibration = value
            return value

        val.set_validate_callback(validate_upload_calibration)
        radio_setting = RadioSetting("upload_calibration",
                                     "Upload Calibration", val)
        radio_setting.set_doc('To Upload only the setting in the calibration section to the radio, ' + \
                              'you need to check this box, then upload to radio.')
        calibration.append(radio_setting)

        radio_setting_group = RadioSettingGroup("squelch_calibration",
                                                "Squelch")
        calibration.append(radio_setting_group)

        bands = {"sqlBand1_3": "Frequency Band 1-3",
                 "sqlBand4_7": "Frequency Band 4-7"}
        for bnd, bndn in bands.items():
            append_label(radio_setting_group,
                         "=" * 6 + " " + bndn + " " + "=" * 300, "=" * 300)
            for sql in range(0, 10):
                prefix = "_mem.cal." + bnd + "."
                postfix = "[" + str(sql) + "]"
                append_label(radio_setting_group, "Squelch " + str(sql))

                name = prefix + "openRssiThr" + postfix
                tempval = min_max_def(eval(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Open RSSI Threshold", val)
                radio_setting_group.append(radio_setting)

                name = prefix + "closeRssiThr" + postfix
                tempval = min_max_def(eval(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Close RSSI Threshold", val)
                radio_setting_group.append(radio_setting)

                name = prefix + "openNoiseThr" + postfix
                tempval = min_max_def(eval(name), 0, 127, 0)
                val = RadioSettingValueInteger(0, 127, tempval)
                radio_setting = RadioSetting(name, "Open Noise Threshold", val)
                radio_setting_group.append(radio_setting)

                name = prefix + "closeNoiseThr" + postfix
                tempval = min_max_def(eval(name), 0, 127, 0)
                val = RadioSettingValueInteger(0, 127, tempval)
                radio_setting = RadioSetting(name, "Close Noise Threshold",
                                             val)
                radio_setting_group.append(radio_setting)

                name = prefix + "openGlitchThr" + postfix
                tempval = min_max_def(eval(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Open Glitch Threshold",
                                             val)
                radio_setting_group.append(radio_setting)

                name = prefix + "closeGlitchThr" + postfix
                tempval = min_max_def(eval(name), 0, 255, 0)
                val = RadioSettingValueInteger(0, 255, tempval)
                radio_setting = RadioSetting(name, "Close Glitch Threshold",
                                             val)
                radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("rssi_level_calibration",
                                                "RSSI Levels")
        calibration.append(radio_setting_group)

        bands = {"rssiLevelsBands1_2": "1-2 ", "rssiLevelsBands3_7": "3-7 "}
        for bnd, bndn in bands.items():
            append_label(radio_setting_group,
                         "=" * 6 +
                         " RSSI levels for QS original small bar graph, bands "
                         + bndn + "=" * 300, "=" * 300)
            for lvl in [1, 2, 4, 6]:
                name = "_mem.cal." + bnd + ".level" + str(lvl)
                tempval = min_max_def(eval(name), 0, 65535, 0)
                val = RadioSettingValueInteger(0, 65535, tempval)
                radio_setting = RadioSetting(name, "Level " + str(lvl), val)
                radio_setting_group.append(radio_setting)

#

        radio_setting_group = RadioSettingGroup("tx_power_calibration",
                                                "TX power")
        calibration.append(radio_setting_group)

        for bnd in range(0, 7):
            append_label(radio_setting_group, "=" * 6 + " TX power band "
                         + str(bnd+1) + " " + "=" * 300, "=" * 300)
            powers = {"low": "Low", "mid": "Medium", "hi": "High"}
            for pwr, pwrn in powers.items():
                append_label(radio_setting_group, pwrn)
                bounds = ["lower", "center", "upper"]
                for bound in bounds:
                    name = f"_mem.cal.txp[{bnd}].{pwr}.{bound}"
                    tempval = min_max_def(eval(name), 0, 255, 0)
                    val = RadioSettingValueInteger(0, 255, tempval)
                    radio_setting = RadioSetting(name, bound.capitalize(), val)
                    radio_setting_group.append(radio_setting)

#

        radio_setting_group = RadioSettingGroup("battery_calibration",
                                                "Battery")
        calibration.append(radio_setting_group)

        for lvl in range(0, 6):
            name = "_mem.cal.batLvl[" + str(lvl) + "]"
            temp_val = min_max_def(eval(name), 0, 4999, 4999)
            val = RadioSettingValueInteger(0, 4999, temp_val)
            radio_setting = \
                RadioSetting(name, "Level " + str(lvl) +
                             (" (voltage calibration)" if lvl == 3 else ""),
                             val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("vox_calibration", "Vox Calibration")
        calibration.append(radio_setting_group)

        for lvl in range(0, 10):
            append_label(radio_setting_group, "Level " + str(lvl + 1))

            name = "_mem.cal.vox1Thr[" + str(lvl) + "]"
            val = RadioSettingValueInteger(0, 65535, eval(name))
            radio_setting = RadioSetting(name, "On", val)
            radio_setting_group.append(radio_setting)

            name = "_mem.cal.vox0Thr[" + str(lvl) + "]"
            val = RadioSettingValueInteger(0, 65535, eval(name))
            radio_setting = RadioSetting(name, "Off", val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("mic_calibration",
                                                "Microphone Sensitivity")
        calibration.append(radio_setting_group)

        for lvl in range(0, 5):
            name = "_mem.cal.micLevel[" + str(lvl) + "]"
            tempval = min_max_def(eval(name), 0, 31, 31)
            val = RadioSettingValueInteger(0, 31, tempval)
            radio_setting = RadioSetting(name, "Level " + str(lvl), val)
            radio_setting_group.append(radio_setting)

        radio_setting_group = RadioSettingGroup("other_calibration", "Other")
        calibration.append(radio_setting_group)

        name = "_mem.cal.xtalFreqLow"
        temp_val = min_max_def(eval(name), -1000, 1000, 0)
        val = RadioSettingValueInteger(-1000, 1000, temp_val)
        radio_setting = RadioSetting(name, "Xtal Frequency Low", val)
        radio_setting_group.append(radio_setting)

        name = "_mem.cal.volumeGain"
        temp_val = min_max_def(eval(name), 0, 63, 58)
        val = RadioSettingValueInteger(0, 63, temp_val)
        radio_setting = RadioSetting(name, "Volume Gain", val)
        radio_setting_group.append(radio_setting)

        name = "_mem.cal.dacGain"
        temp_val = min_max_def(eval(name), 0, 15, 8)
        val = RadioSettingValueInteger(0, 15, temp_val)
        radio_setting = RadioSetting(name, "DAC Gain", val)
        radio_setting_group.append(radio_setting)



        # ----------------- Help User

        help_group = RadioSettingGroup("Explain_Display_HELP",
                                                "Documentation Display")
        help_user.append(help_group)

        append_label(help_group, "=" * 6 + " Documentation Display " + "=" * 50, "=" * 6  + " Location on display " + "=" * 50)
                         
        append_label(help_group,"Status Line", "First line on the display, on the top of the display" )
        append_label(help_group,"(PS) = Power Save", "Status line" )
        append_label(help_group,"(S) = Scan active", "Status line" )
        append_label(help_group,"(I) = Scan memories on list 1", "Status line" )
        append_label(help_group,"(II) = Scan Memories on list 2", "Status line" )
        append_label(help_group,"(INFINI) = Scan all lists", "Status line" )
        append_label(help_group,"(MO) = Main only, display only one VFO", "Status line" )
        append_label(help_group,"(DWR) = Dual RX respond", "Status line" )
        append_label(help_group,"(DW) = Main TX dual RX", "Status line" )
        append_label(help_group,"(XD) = Cross Band", "Status line" )
        append_label(help_group,"(VX) = VOX active", "Status line" )
        append_label(help_group,"(CL) = PTT classic mode" , "Status line" )
        append_label(help_group,"(OP) = PTT one push mode" , "Status line" )
        append_label(help_group,"(F) = Activates the second function of a key" , "Status line" )

        append_label(help_group,"" , "" )

        append_label(help_group,"(Dark Arrow) = Active VFO" , "On the left side of the VFO" )
        append_label(help_group,"(Mxxx) = Memory number M1-M200", "On the left side of the VFO" )
        append_label(help_group,"(Fx) =  Band number F1-F7 " , "On the left side of the VFO" )
        append_label(help_group,"(TX) = VFO used when TX" , "On the left side of the VFO" )
        append_label(help_group,"(RX) = Radio receiving" , "On the left side of the VFO" )

        append_label(help_group,"" , "" )

        append_label(help_group, "=" * 6 + " if (SetGui) is set on CLASSIC " + "=" * 50, "=" * 6  + "=" * 100)

        append_label(help_group,"(FM,USB,AM) = Reception mode" , "Under each VFO" )
        append_label(help_group,"(DC) = RX DCS active" , "Under each VFO" )
        append_label(help_group,"(CT) = RX CTCSS active" , "Under each VFO" )
        append_label(help_group,"(H) = High TX power" , "Under each VFO" )
        append_label(help_group,"(M) = Medium TX power" , "Under each VFO" )
        append_label(help_group,"(Lx) = Low TX power, with x = level 1 to 5" , "Under each VFO" )
        append_label(help_group,"(W) = Wide BF filter: 12.5kHz (WIDE)" , "Under each VFO" )
        append_label(help_group,"(N) = Narrow BF filter: 6.25kHz (NARROW)" , "Under each VFO" )

        append_label(help_group,"" , "" )

        append_label(help_group, "=" * 6 + " If (SetGui) is set on TINY " + "=" * 50, "=" * 6  + "=" * 100)

        append_label(help_group,"(FM,USB,AM) = Reception Mode" , "Under each VFO" )
        append_label(help_group,"(HIGH) = High TX power" , "Under each VFO" )
        append_label(help_group,"(MID) = Medium TX power" , "Under each VFO" )
        append_label(help_group,"(LOWx) = Low TX power, with x = level 1 to 5" , "Under each VFO" )
        append_label(help_group,"(CT x) = RX CTCSS active, with x = value" , "Under each VFO" )
        append_label(help_group,"(DC x) = RX CTCSS active, with x = value" , "Under each VFO" )
        append_label(help_group,"(x.xxK) = no incrementation of the frequency" , "Under each VFO" )
        append_label(help_group,"(WIDE) = Wide BF filter: 12.5kHz" , "Under each VFO" )
        append_label(help_group,"(NAR) = Narrow BF filter: 6.25kHz" , "Under each VFO" )
       
        append_label(help_group,"" , "" )

        append_label(help_group, "=" * 6 + "=" * 100, "=" * 6  + "=" * 100)
       
        append_label(help_group,"(SQLx) = Squelch level, with x = value from 1 to 9" , "Displayed below each VFO" )
        append_label(help_group,"(MONI) = RX monitoring (squelch disabled)" , "Displayed below each VFO" )
       
        help_group = RadioSettingGroup("Explain_Keyboard_HELP", "Keypad documentation" )
        help_user.append(help_group)

        append_label(help_group, "=" * 6 + " Keypad and buttons' function " + "=" * 50, "=" * 6  + " When pressing (F #) before the key " + "=" * 50)
                                                   
        append_label(help_group,"(1 BAND) = long press: change the active frequency band (F1 to F7)  " , "Same as long press  " )
        append_label(help_group,"(1 BAND) = short press: digit 1  "," " )
        append_label(help_group,"","" )

        append_label(help_group,"(2 A/B) = long press: change the active VFO, A(top) / B(bottom) " , "Same as long press " )
        append_label(help_group,"(2 A/B) = short press: digit 2  "," " )

        append_label(help_group,"","" )
        
        append_label(help_group,"(3 VFO MR) = long press: toggle between VFO and memory " , "Same as long press  " )
        append_label(help_group,"(3 VFO MR) = short press: digit 3  "," " )

        append_label(help_group,"","" )
        
        append_label(help_group,"(* SCAN) = long press: if in VFO mode, start a scan ", "Make a scan list from the active channel" )
        append_label(help_group,"(* SCAN) = long press, if in memory mode: = switch scan list (1,2, ALL) ", "Make a scan list from the active channel" )
        append_label(help_group,"(* SCAN) = short press:  DTMF input mode (S) ", "Start CTCSS listening on the current frequency" )

        append_label(help_group,"","" )

        append_label(help_group,"(4 FC) = long press: start the CTCSS & frequency scan " , "Same as long press " )
        append_label(help_group,"(4 FC) = short press: digit 4  "," " )

        append_label(help_group,"","" ) 
        
        append_label(help_group,"(5 NOAA) = long press: if in VFO mode: display ScnRnG " , "Display fagci spectrum analyze " )
        append_label(help_group,"(5 NOAA) = long press: if in memory mode,  change the scan list " , " ")
        append_label(help_group,"(5 NOAA) = short press: digit 5  "," " )

        append_label(help_group,"","" )
                
        append_label(help_group,"(6 H/M/L) = long press: change the TX power level (High/Medium/Low) of the active VFO " , "Same as long press " )
        append_label(help_group,"(6 H/M/L) = short press: digit 6  "," " )

        append_label(help_group,"","" )
                
        append_label(help_group,"(0 FM) = long press: FM Broadcast listening ", "Same as long press " )
        append_label(help_group,"(0 FM) = short press: digit 0  "," " )

        append_label(help_group,"","")
        
        append_label(help_group,"(7 VOX) = long press: change voice Activation (VX) " , "Same as long press " )
        append_label(help_group,"(7 VOX) = short press: digit 7  "," " )

        append_label(help_group,"","" )
                
        append_label(help_group,"(8 R) = long press: reverse (if using a shift) (R) " , "Same as long press ")
        append_label(help_group,"(8 R) = short press: digit 8  ","Force backlight on/off " )
        append_label(help_group,"","Disable backlight timeout (BLTime)")

        append_label(help_group,"","" )
        
        append_label(help_group,"(9 CALL) = long press: switch current channel to 1-Call channel" , "Same as long press")
        append_label(help_group,"(9 CALL) = short press: digit 9","Enable backlight timeout (BLTime)" )

        append_label(help_group,"","" )
        
        append_label(help_group,"(F #) = long, press: keypad lock/unlock", )
        append_label(help_group,"(F #) = short press: activates the secondary button function", )

        append_label(help_group,"","" )
        
        append_label(help_group,"(M A) = long press: user programmable button","" )
        append_label(help_group,"(M A) = short press: Menu access","" )

        append_label(help_group,"","" )

        append_label(help_group,"(Arrow UP B) = long press: scroll VFO/MR upwards","" )
        append_label(help_group,"(Arrow UP B) = short press: increase VFO/MR value ","increase squelch value" )

        append_label(help_group,"","" )

        append_label(help_group,"(Arrow DOWN C) = long press: scroll VFO/MR downwards","" )
        append_label(help_group,"(Arrow DOWN C) = short press: decrease VFO/MR value","decrease squelch value" )

        append_label(help_group,"","" )
        
        append_label(help_group, "=" * 6 + " side button" + "=" * 50, "=" * 6  + "" + "=" * 50)

        append_label(help_group,"","" )
        
        append_label(help_group,"(PTT)  = long press: transmit on active TX","" )
        append_label(help_group,"(PTT)  = short press: transmit on active TX","" )

        append_label(help_group,"","" )
        
        append_label(help_group,"(.)  = long press: user programmable button","" )
        append_label(help_group,"(.)  = short press, user programmable button","" )

        append_label(help_group,"","" )

        append_label(help_group,"(..)  = long press, user programmable button","" )
        append_label(help_group,"(..)  = short press, user programmable button","" )

        append_label(help_group,"","" )
        
        append_label(help_group, "=" * 6 + " special function " + "=" * 50, "=" * 6  + "" + "=" * 50)

        append_label(help_group,"","" )
        
        append_label(help_group,"To put the radio in programming MODE firmware","Hold PTT key then switch on the radio, the flashlight will light up" )

        append_label(help_group,"","" )
        
        append_label(help_group,"To activate the hidden menu","Hold the PTT key and the button just below it then turn on the radio" )
        append_label(help_group,"", "The hidden items are at the end of the regular menu" )


 
        help_group = RadioSettingGroup("How_To_Upload_F4HWN_HELP",
                                                "How to upload F4HWN settings")
        help_user.append(help_group)

        append_label(help_group,"Special upload need to be done to upload F4HWN firmware settings to the radio", )
        append_label(help_group,"since the features of F4HWN's firmware are located in a different memory range.", )
        append_label(help_group,"You need to select the box \"Upload F4HWN\", to upload ONLY and ONLY the ", )
        append_label(help_group,"section of F4HWN to the radio. Go in menu Radio, Upload to Radio...", )
        append_label(help_group,"It will be very fast to upload, then the radio will reboot.", )
        append_label(help_group,"After uploading, uncheck the box \"Upload F4HWN\" to be able to upload all other settings", )
        append_label(help_group,"of the radio. Go in Radio menu, Upload to Radio... and now all the settings will be sent to the radio ", )
        
        help_group = RadioSettingGroup("Chirp_Language_HELP",
                                                "How to change CHIRP language")
        help_user.append(help_group)
        
        append_label(help_group,"It's not possible to change the language directly in CHIRP but...", )
        append_label(help_group,"You need to change the openrating system parameter, since CHIRP is using OS settings to set the language ", )
        append_label(help_group,"it's a bit hard to explain with description in text only, so go see the file ", )
        append_label(help_group,"[how_to_do_for_module_in_chirp_release_1.doc] included in the release version ", )
        append_label(help_group,"or go at the github project page to see the file ", CHIRP_DRIVER_VERSION_UPDATE )

        # -------- LAYOUT
        append_label(basic,
                     "=" * 6 + " Start of F4HWN Settings. If this area needs to be uploaded, select \"Upload F4HWN's settings to radio\" below " + "=" * 300, "=" * 300)
        basic.append(Upload_f4hwn)
        basic.append(SetLowSetting)
        basic.append(SetPttSetting)
        basic.append(SetTotSetting)
        basic.append(SetEotSetting)
        basic.append(contrastSetting)
        basic.append(SetInvSetting)
        basic.append(SetLckSetting)
        basic.append(SetMetSetting)
        basic.append(SetGuiSetting)
        append_label(basic,
                     "=" * 6 + " End of F4HWN settings " + "=" * 300, "=" * 300)

        append_label(basic,
                     "=" * 6 + " General settings " + "=" * 300, "=" * 300)

        basic.append(squelch_setting)
        basic.append(rx_mode_setting)
        basic.append(call_channel_setting)
        basic.append(auto_keypad_lock_setting)
        basic.append(tx_t_out_setting)
        basic.append(bat_save_setting)
        basic.append(scn_rev_setting)
        if _mem.BUILD_OPTIONS.ENABLE_NOAA:
            basic.append(noaa_auto_scan_setting)
        if _mem.BUILD_OPTIONS.ENABLE_AM_FIX:
            basic.append(am_fix_setting)

        append_label(basic,
                     "=" * 6 + " Display settings " + "=" * 300, "=" * 300)

        basic.append(bat_txt_setting)
        basic.append(mic_bar_setting)
        basic.append(ch_disp_setting)
        basic.append(p_on_msg_setting)
        basic.append(logo1_setting)
        basic.append(logo2_setting)

        append_label(basic, "=" * 6 + " Backlight settings "
                     + "=" * 300, "=" * 300)

        basic.append(back_lt_setting)
        basic.append(bl_min_setting)
        basic.append(bl_max_setting)
        basic.append(blt_trx_setting)

        append_label(basic, "=" * 6 + " Audio related settings "
                     + "=" * 300, "=" * 300)

        if _mem.BUILD_OPTIONS.ENABLE_VOX:
            basic.append(vox_setting)
        basic.append(mic_gain_setting)
        basic.append(beep_setting)
        basic.append(roger_setting)
        basic.append(ste_setting)
        basic.append(rp_ste_setting)
        if _mem.BUILD_OPTIONS.ENABLE_VOICE:
            basic.append(voice_setting)
        if _mem.BUILD_OPTIONS.ENABLE_ALARM:
            basic.append(alarm_setting)

        append_label(basic, "=" * 6 + " Radio state " + "=" * 300, "=" * 300)

        basic.append(freq0_setting)
        basic.append(freq1_setting)
        basic.append(tx_vfo_setting)
        basic.append(keypad_lock_setting)

        advanced.append(freq_mode_allowed_setting)
        advanced.append(bat_type_setting)
        advanced.append(s0_level_setting)
        advanced.append(s9_level_setting)
#        if _mem.BUILD_OPTIONS.ENABLE_PWRON_PASSWORD:
#            advanced.append(pswd_setting)

        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(sep_code_setting)
            dtmf.append(group_code_setting)
        dtmf.append(first_code_per_setting)
        dtmf.append(spec_per_setting)
        dtmf.append(code_per_setting)
        dtmf.append(code_int_setting)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(ani_id_setting)
        dtmf.append(up_code_setting)
        dtmf.append(dw_code_setting)
        dtmf.append(d_prel_setting)
        dtmf.append(dtmf_side_tone_setting)
        if _mem.BUILD_OPTIONS.ENABLE_DTMF_CALLING:
            dtmf.append(dtmf_resp_setting)
            dtmf.append(d_hold_setting)
            dtmf.append(d_live_setting)
            dtmf.append(perm_kill_setting)
            dtmf.append(kill_code_setting)
            dtmf.append(rev_code_setting)
            dtmf.append(killed_setting)

        unlock.append(f_lock_setting)
        unlock.append(tx200_setting)
        unlock.append(tx350_setting)
        unlock.append(tx500_setting)
        unlock.append(en350_setting)      
# desable by f4hwn
#       unlock.append(en_scrambler_setting)

        return top

    def set_memory(self, memory):
        """
        Store details about a high-level memory to the memory map
        This is called when a user edits a memory in the UI
        """
        number = memory.number-1
        att_num = number if number < 200 else 200 + int((number - 200) / 2)

        # Get a low-level memory object mapped to the image
        _mem_chan = self._memobj.channel[number]
        _mem_attr = self._memobj.ch_attr[att_num]

        _mem_attr.is_scanlist1 = 0
        _mem_attr.is_scanlist2 = 0
        _mem_attr.compander = 0
        _mem_attr.is_free = 1
        _mem_attr.band = 0x7

        # empty memory
        if memory.empty:
            _mem_chan.set_raw("\xFF" * 16)
            if number < 200:
                _mem_chname = self._memobj.channelname[number]
                _mem_chname.set_raw("\xFF" * 16)
            return memory

        # find band
        band = self._find_band(memory.freq)

        # mode
        tmp_mode = self.get_features().valid_modes.index(memory.mode)
        _mem_chan.modulation = tmp_mode / 2
        _mem_chan.bandwidth = tmp_mode % 2
        if memory.mode == "USB":
            _mem_chan.bandwidth = 1  # narrow

        # frequency/offset
        _mem_chan.freq = memory.freq/10
        _mem_chan.offset = memory.offset/10

        if memory.duplex == "":
            _mem_chan.offset = 0
            _mem_chan.offsetDir = 0
        elif memory.duplex == '-':
            _mem_chan.offsetDir = FLAGS1_OFFSET_MINUS
        elif memory.duplex == '+':
            _mem_chan.offsetDir = FLAGS1_OFFSET_PLUS
        elif memory.duplex == 'off':
            # we fake tx disable by setting the tx freq to 0 MHz
            _mem_chan.offsetDir = FLAGS1_OFFSET_MINUS
            _mem_chan.offset = _mem_chan.freq
        # set band

        _mem_attr.is_free = 0
        _mem_attr.band = band

        # channels >200 are the 14 VFO chanells and don't have names
        if number < 200:
            _mem_chname = self._memobj.channelname[number]
            tag = memory.name.ljust(10) + "\x00"*6
            _mem_chname.name = tag  # Store the alpha tag

        # tone data
        self._set_tone(memory, _mem_chan)

        # step
        _mem_chan.step = STEPS.index(memory.tuning_step)

        # tx power
        if str(memory.power) == str(UVK5_POWER_LEVELS[2]):
            _mem_chan.txpower = POWER_HIGH
        elif str(memory.power) == str(UVK5_POWER_LEVELS[1]):
            _mem_chan.txpower = POWER_MEDIUM
        else:
            _mem_chan.txpower = POWER_LOW

        # -------- EXTRA SETTINGS

        def get_setting(name, def_val):
            if name in memory.extra:
                return int(memory.extra[name].value)
            return def_val

        _mem_chan.busyChLockout = get_setting("busyChLockout", False)
        _mem_chan.dtmf_pttid = get_setting("pttid", 0)
        _mem_chan.freq_reverse = get_setting("frev", False)
        _mem_chan.dtmf_decode = get_setting("dtmfdecode", False)
        _mem_chan.scrambler = get_setting("scrambler", 0)
        _mem_attr.compander = get_setting("compander", 0)
        if number < 200:
            tmp_val = get_setting("scanlists", 0)
            _mem_attr.is_scanlist1 = bool(tmp_val & 1)
            _mem_attr.is_scanlist2 = bool(tmp_val & 2)

        return memory
