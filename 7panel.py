#!/usr/bin/env python

import RPi.GPIO as GPIO
import time 
import os
import sys
import commands
import pywapi
import string
import random

# button layout depends on user wiring
#ledpins = [22,11,15,21,24,26,23]
ledpins = [3,11,5,19,13,15,7]
left_button=21
right_button=23

######## functions ########

def setupgpio():
    print "initializing gpio on board"
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(right_button, GPIO.IN, GPIO.PUD_UP) # button on left
    GPIO.setup(left_button, GPIO.IN, GPIO.PUD_UP) # button on right
    for led in ledpins:
        GPIO.setup(led, GPIO.OUT)

def all_leds_off():
    for led in ledpins:
        GPIO.output(led, 0)
        time.sleep(.1)

def binary_to_leds(binin):
    # convert each bit into an element of array
    bits = list(binin)
    position = 0
    # 0=off 1=on working left to right
    for bit in bits:
        GPIO.output(ledpins[position],int(bit))
        position=(position+1)

def lamp_test():
    print "right pressed: counting leds up and down"
    for led in ledpins:
        GPIO.output(led, 0)
        time.sleep(.1)
    for led in ledpins:
        GPIO.output(led, 1)
        time.sleep(.1)
    for led in ledpins:
        GPIO.output(led, 0)
        time.sleep(.1)
    program_number=1

def do_program(prog):
    print "doing program"
    print prog 
    for x in range(0,10):
        binary_to_leds(prog)
        time.sleep(.1)
        GPIO.output(ledpins[0],1)
        time.sleep(.1)
    all_leds_off()
    print "if prog is "
    print prog
    if (prog=="0000001"):
        do_weather("condition","temp") # weather temp
    if (prog=="0000010"):
        do_weather("condition","code") # weather skies
    if (prog=="0000011"):
        do_weather("wind","speed") # wind speed
    if (prog=="0000100"):
        do_weather_forecast("forecasts",0,"high") # wind speed
    if (prog=="0000101"):
        do_magic8() # the magic 8 ball
    if (prog=="0000110"):
        send_sms(1) # send a text msg to person 1
    if (prog=="0000111"):
        send_sms(2) # send a text msg to person 2
    if (prog=="0001000"):
        do_weather_forecast("forecasts",0,"low")
    if (prog=="0001001"):
        do_weather_forecast("forecasts",1,"low")
    if (prog=="0001010"):
        do_weather_forecast("forecasts",1,"high")

def send_sms(person):
    os.system("/home/pi/sendtxt.sh " + str(person))
    binary_to_leds("1111111")

def do_weather(param1,param2):
    yahoo_result = pywapi.get_weather_from_yahoo('06484','imperial')
    print "param 1 is" + param1
    print "param 2 is" + param2
    code = yahoo_result[param1][param2]
    print "code is "
    print code
    code = int(code)
    print "and now code is"
    print code
    print type(code)
    binary_condition_number="{0:b}".format(code)
    binary_condition_number=binary_condition_number.zfill(7)
    print "binary cond number is"
    print binary_condition_number
    binary_to_leds(binary_condition_number)
 
def do_weather_forecast(param1,param2,param3):
    yahoo_result = pywapi.get_weather_from_yahoo('06484','imperial')
    print "param 1 is" + param1
    code = yahoo_result[param1][param2][param3]
    print "code is "
    print code
    code = int(code)
    print "and now code is"
    print code
    print type(code)
    binary_condition_number="{0:b}".format(code)
    binary_condition_number=binary_condition_number.zfill(7)
    print "binary cond number is"
    print binary_condition_number
    binary_to_leds(binary_condition_number)

def do_magic8():
    code = random.randint(1, 20)
    binary_condition_number="{0:b}".format(code)
    binary_condition_number=binary_condition_number.zfill(7)
    print "binary cond number is"
    print binary_condition_number
    binary_to_leds(binary_condition_number)


########### end functions ########

setupgpio()
all_leds_off()
program_number = 1
binary_program_number = "0000001"
input_state = GPIO.input(right_button)
left_state = GPIO.input(left_button)
while True:
    program_number = 1
    print "Push the button on the right to run program"
    print "or push button on left to select another program"
    timer = 2
    while (input_state == True):
        input_state = GPIO.input(right_button)
        left_state = GPIO.input(left_button)
        if (left_state == 0):
            print "left pressed"
            program_number=(program_number+1)
            print "program number is now"
            print program_number
            binary_program_number="{0:b}".format(program_number)
            binary_program_number=binary_program_number.zfill(7)
            binary_to_leds(binary_program_number)
            time.sleep(.1)
        time.sleep(.1)
        timer =(timer-1)

        # if timer is 0 then flash ready light
        # to show we are loaded still

        if (timer==0):
            GPIO.output(ledpins[0],1)
            time.sleep(.1)
            GPIO.output(ledpins[0],0)
            timer = 30

    # if right button is pushed
    lamp_test()
    print "getting ready to do prog number"
    if program_number:
        print binary_program_number
        do_program(binary_program_number)
    binary_program_number="0000001"
    print "push button to reset"
    input_state = GPIO.input(right_button)
    while (input_state == True):
        input_state = GPIO.input(right_button)
        time.sleep(.1)
    lamp_test()
    all_leds_off() 
    program_number=1
    input_state = GPIO.input(right_button)
