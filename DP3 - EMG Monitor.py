## Imports necessary modules
from gpiozero import LED
from gpiozero import Button
from sensor_library import *
import time
from datetime import date
import matplotlib.pyplot as graph
import sys


## Defines input and output device variables by GPIO positions
green_LED = LED(13)
yellow_LED = LED(5)
blue_LED = LED(11)
button = Button(1)


## Defines LED_sys as a function for activating the LEDs by electrical actiivty range (accepts 2 arguments)
def LED_sys(avg,goal):
    
    ## Defines variables for LED_sys function    
    colour_list = []

    ## Compares average value with goal value argument and divides it into 3 ranges, each activating a separate LED and recording as "On" or "Off"
    if avg == None: ## If the average value = None, LED_sys function returns None
        return None
    
    elif avg>(2*goal/3): ## If the average value is in the lowest range, the green LED turns on
        green_LED.on()
        yellow_LED.off()
        blue_LED.off()
        colour_list = ["On", "Off", "Off"]
        
    elif (2*goal/3)>=avg>(goal/3): ## If the average value is in the middle range, the yellow LED turns on
        green_LED.off()
        yellow_LED.on()
        blue_LED.off()
        colour_list = ["Off", "On", "Off"]
        
    else:## If the average value is in the highest range, the blue LED turns on
        green_LED.off()
        yellow_LED.off()
        blue_LED.on()
        colour_list = ["Off", "Off", "On"]
    return colour_list


## Defines graph_func as a function for displaying a graph (accepts 2 arguments)
def graph_func(x, y):
    graph.plot(x, y,"o-")
    graph.ion()
    
    if len(x)<51:
        graph.xlim(0,len(x))
    else:
        graph.xlim(len(x)-50,len(x))
        
    graph.ylim(0,250)
    graph.xlabel("Time")
    graph.ylabel("EMG average (V)")
    graph.title("Muscle Mark")
    graph.pause(0.2)


## Defines rolling_avg as a function for calculating the rolling average of sensor input data (accepts 3 arguments)
def rolling_avg(data_point, list_name, index_var):
    list_name[index_var%len(list_name)] = data_point ## Assigns sensor input value  to a list ##???
    
    if index_var>(len(list_name)-1): ## Calculates average of last 5 sensor input values
        average = sum(list_name)/len(list_name)
        return round(average, 2)
    
    else:
        return None


## Defines baseline_high as a function for calculating the highest sensor input value during a baseline test   
def baseline_high(highest_emg, new_point):
    if new_point>highest_emg: 
        return new_point
    
    else:
        return highest_emg


## Defines main as a function for main program  
def main():

    start = input("Enter 'Y' to start the Muscle Mark.\n")
    while start == "Y" or start == "y":
        ## Defines variables for tracking user activity
        power = True
        track_type = True
        goal = False
        test_type = None
        counter = 0

        ## Defines variables for functions
        LED_avg = 0
        goal_voltage = 0
        high = 0
        avg_list = [0 for i in range(5)]
        graph_x = []
        graph_y = []

        ## Defines variables based on time and sensor inputs
        today = date.today()
        day = today.strftime("%d/%m/%Y")
        MuscleEV = Muscle_Sensor(1)
        
        ## Defines variables for appending to text files
        tracker = open("Progress Tracker.txt", "a")

        ## Asks for user input on type of test user wishes to run
        while track_type==True: 
            test_type = input("What type of electrical activity tests would you like to perform? Enter ‘A’ for a baseline test, ‘B’ for a progress check. ")

            if test_type == "A": ## If input = "A", program runs a "Baseline Test" and formats a text file accordingly 
                tracker.write("Baseline Test"+"\t"+str(day)+"\n")
                track_type = False
                print("Note: lights will display as N/A because lights are not activated for a baseline test.")

            elif test_type == "B": ## If input = "B", program runs "Progress Track" and formats a text file accordingly
                tracker.write(str(day)+"\n")
                track_type = False

                while goal == False: ## Asks for user input on goal electrical activity if goal is False
                    goal_voltage = int(input("Enter your goal voltage. (If you've used the baseline test, this can be the highest recorded electrical activity value from your test.) "))

                    if goal_voltage<450: ## If goal electrical activity is less than 450, the program will run, else an error message will be displayed
                        print("Note: the green light will display for values above "+str(round(2*goal_voltage/3,2))+", the blue below "+str(round(goal_voltage/3,2))+", and yellow in between.")
                        goal = True

                    else:
                        print("Please enter a valid goal voltage (below 243)")
                        
            else: ## Asks user to re-input for test_type if not "A" or "B"
                print("Please enter a valid letter.")

        ## Tracks when the button is pressed
        button.wait_for_press()

        ## Prints header for formatting information on python shell display and text file
        header = "Voltage (raw)\t"+"Voltage (avg)\t"+"Green LED\t"+"Yellow LED\t"+"Blue LED\t"+"Graph Status\t"
        print (header)
        tracker.write(header+"\n")

        ## Starts timer 
        start = time.time()

        ## Sets data input from sensor on a loop
        while power == True:
            data = MuscleEV.muscle_raw() ## Uses MuscleEV class to input data from the sensor
            time.sleep(0.2) ## Pauses program 
            LED_avg = rolling_avg(data, avg_list, counter) ## Calls rolling_avg function as LED_avg

            ## Writes formatted data, rolling average and LED information to a text file and displays it on the python shell
            if test_type == "A": 
                if LED_avg!=None:
                    line = str(data)+"\t\t"+str(LED_avg)+"\t\t"+"N/A\t\t"+"N/A\t\t"+"N/A\t\t"+"On\t\t"
                    tracker.write(line+"\n")
                    print (line)
                    high = baseline_high(high, LED_avg) ## Calls the baseline_high function 

            elif test_type == "B": 
                lights = LED_sys(LED_avg, goal_voltage) ## Calls the LED_sys function to activate LEDs according to rolling average values
                if LED_avg!=None: ## Writes and displays formatted data if LED_avg does NOT = None
                    line = str(data)+"\t\t"+str(LED_avg)+"\t\t"+lights[0]+"\t\t"+lights[1]+"\t\t"+lights[2]+"\t\tOn"
                    tracker.write(line+"\n")
                    print (line)

            if LED_avg!=None: ## Creates graph
                graph_y.append(LED_avg) ## Adds LED_avg values to a list for graph y values
                graph_x.append(len(graph_y)-1) ## Adds number of y values - 1 to a list for graph x values
                graph_func(graph_x, graph_y) ## Calls graph_func function, accepting
            
            if button.is_pressed: ## Tracks button input and stops sensor input once button is pressed
                power = False
                    
            counter+=1 ## Counts number of loop runs

        ## Turns off LEDs
        green_LED.off()
        yellow_LED.off()
        blue_LED.off()

        ## Stops timer and calculates elapsed time
        end = time.time() 
        elapsed_time = round(end - start)

        ## Closes text file
        tracker.close()


        ## Displays highest electrical activity for baseline test
        if test_type == "A":
            print("The highest electrical activity for the baseline test is "+str(high)+str(". Please record it somewhere for future use."))

        ## Displays elapsed time
        print("The time spent working out is "+str(elapsed_time)+" seconds.")

        start = input("Enter 'Y' if you wish to run another test. Hit any key to close the program.\n")

    print ("Goodbye.")

main()
