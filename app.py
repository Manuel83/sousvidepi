
from flask import Flask
from flask import session
from flask import render_template
from flask import request
from random import randint
from random import uniform
from subprocess import Popen, PIPE, call
from multiprocessing import Process, Pipe, Queue, current_process, Value
import time
import pidypi as PIDController
#import RPi.GPIO as GPIO
import logging

app = Flask(__name__)


logging.basicConfig(filename='example.log',level=logging.DEBUG)

tt = Value('i', 50)
kp = Value('i', 102)
ki = Value('i', 100)
kd = Value('i', 5)
cycle_duty = Value('d', 0)

job = None

w1_sensorid = "28-03146215acff"
testMode = True
pinNum = 17
cycle_time=5


@app.route("/")
def index():
    if job is None:
        automode = "Off"
    else: 
        automode = "On"
        
    return render_template('index.html', targetTemp=tt.value, kp=kp.value ,  ki=ki.value , kd=kd.value, automode=automode )


@app.route("/auto")
def auto(): 
    
    global job
    if job is None:
        print("AUTO MODE Started")
        startAutoMode(tt, kp, ki, kd)
    else:
        print("AUTO MODE Stopped")
        job.terminate()
        job = None
        
    
    return "OK"

@app.route("/setData")
def setData(): 
    print("SET DATA")
    tt.value = int(request.args.get('tt', ''))
    kp.value = int(request.args.get('kp', ''))
    ki.value = int(request.args.get('ki', ''))
    kd.value = int(request.args.get('kd', ''))
    return "OK"

@app.route("/getTemp")
def getTemp(): 
    
   
    
    t = float(tempData1Wire(w1_sensorid))  
    i = str(round(t,1))
    return "{\"temp\":\"%s\",\"heat\":\"%s\"}" % (i,cycle_duty.value,) 

@app.route("/heat")
def heatOn(): 
    print("HEAT ON")
    return "ON"

def startAutoMode(tt, kp, ki, kd):
    print("START JOB")
    global job 
    
    job = Process(name = "gettempProc1", target=gettempProc, args=(tt,kp,ki,kd,cycle_duty,))
    job.start()   
    

def gettempProc(targetTemp, kp, ki, kd, dc):
    
    ## SETUP PID
    pid = PIDController.pidpy(cycle_time, kp.value, ki.value, kd.value) 

    ## SETUP GPIO
    if testMode == False:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinNum, GPIO.OUT)
        GPIO.output(pinNum, 1)
    
    while (True):
     
        print("TT", targetTemp.value)
        print("KP", kp.value)
        print("KI", ki.value)
        print("KD", kd.value)
       
        temp_ma = float(tempData1Wire(w1_sensorid))  
        duty_cycle = pid.calcPID_reg4(temp_ma, targetTemp.value, True)
       
        #print 'DUTY CYCLE', duty_cycle
        print(cycle_time)
        
        dc.value = float(duty_cycle)
    
        
        if duty_cycle == 0:
            print "--> 100% OFF"
            #GPIO.output(pinNum, 0)
            time.sleep(5)
        elif duty_cycle == 100:
            print "--> 100% ON"
            #GPIO.output(pinNum, 1)
            time.sleep(5)
        else:
            print "--> INDIVIDUAL"
            on_time, off_time = getonofftime(cycle_time, duty_cycle)
            #GPIO.output(pinNum, 1)
            time.sleep(on_time)
            #GPIO.output(pinNum, 0)
            time.sleep(off_time)
                
def getonofftime(cycle_time, duty_cycle):
    duty = duty_cycle/100.0
    on_time = cycle_time*(duty)
    off_time = cycle_time*(1.0-duty)   
    return [on_time, off_time]

def tempData1Wire(tempSensorId):
    
    if testMode == True:
        pipe = Popen(["cat","w1_slave"], stdout=PIPE)
    else:
        pipe = Popen(["cat","/sys/bus/w1/devices/w1_bus_master1/" + tempSensorId + "/w1_slave"], stdout=PIPE)
    
    result = pipe.communicate()[0]
    if (result.split('\n')[0].split(' ')[11] == "YES"):
        temp_C = float(result.split("=")[-1])/1000 # temp in Celcius
    else:
        temp_C = -99 #bad temp reading
      
    
    return temp_C

if __name__ == "__main__":
    #start thermometer
    if testMode == False:
        call(["modprobe", "w1-gpio"])
        call(["modprobe", "w1-therm"])
    
    #session setup
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=False, host='0.0.0.0')

