"""
Created on Wed Apr 13 09:52:52 2022

author: Maor Bouhadana

version = 1.1
"""

import socket
import time
import os
import numpy as np

def scan_devices(subnet = "192.168.0" , start  = 0  , stop = 111):
    print("start scanning...")
    for i in range(start , stop+1):
        ip = subnet+"."+str(i)
        # response = os.popen(f"ping {ip}").read()
        # if "Received = 4" in response:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(0.5)
        try:
            # print(ip)
            soc.connect((ip, 5025))
            soc.send("*IDN?\n".encode())
            response = str(soc.recv(1000))
            # print(response.decode())
            if "N5173B" in response:
                print(ip)
                print("Signal generator - N5173B ")
            elif "N5183B" in response:
                print(ip)
                print("Signal generator - N5183B ")
            elif "N9010B" in response:
                print(ip)
                print("Spectrum analyzer - N9010B ")
            elif "N9020B" in response:
                print(ip)
                print("Spectrum analyzer - N9020B ")
            else:
                print(ip)
                print(response)
            # soc.shutdown(socket.SHUT_RDWR)
            time.sleep(0.01)
        except:
            time.sleep(0.01)
        soc.close()
    print("done..")
    

class KeysightDevice:
    
    def __init__(self , IP = "192.168.0.110"  , PORT = 5025):
        self.__ip = IP
        self.__port = PORT
        self.__type = -1
        self.__brand = -1
        self.__description = -1
        self.__connection = -1
        
    def set_ip(self , IP):
        try:
            self.__ip = IP
        except:
            return -1
        return 1
    
    def get_ip(self):
        try:
            return self.__ip
        except:
            return - 1
    
    def set_tcp_port(self , PORT):
        try:
            self.__port = PORT
        except:
            return -1
        
        return 1
    
    def get_tcp_port (self):
        try:
            return self.__port
        except:
            return  -1
        
    def brand_extraction(self , device_id):
        if "N5173B" in device_id:
            return "N5173B"
        elif "N5183B" in device_id:
            return "N5183B"
        elif "N9010B" in device_id:
            return "N9010B"
        elif "N9020B" in device_id:
            return "N9020B"
        return -1
    
    def set_brand(self , BRAND):
        try:
            self.__brand = BRAND
            if (self.__brand == "N5173B" or self.__brand == "N5183B" ):
                self.__type = "Signal Generator"
            elif(self.__brand == "N9010B" or self.__brand == "N9020B"):
                 self.__type = "Spectrum Analyzer"
        except:
            return -1
        return 1
    
    def get_brand(self):
        try: 
            return self.__brand
        except:
            return -1
    
    def get_type(self):
        try:
            return self.__type
        except:
            return -1
    def connect2device(self):
        
        try:
            self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__connection.connect((self.__ip, self.__port))
            self.__connection.settimeout(1)
        except:
            print("No connection could be made because the target machine actively refused it , please check TCPIP Socket port and IP")
            return -1
        try:
            self.__connection.send("*IDN?\n".encode())
            response = self.__connection.recv(1000)
            # print(response.decode())
            brand = self.brand_extraction(str(response))
            self.set_brand(brand)
            
        except:
            print("The device didnt response")
        return 1
    
   
        
    def close_connection(self):
        try:
            self.__connection.shutdown(socket.SHUT_RDWR)
            self.__connection.close()
        except:
            return -1
        
        return 1
         

        
    def set_rf_on(self):
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send(":OUTPut:STATe ON\n".encode())
                return 1
            except:
                return -1
        else:
            print("set rf on failed - device not recognized as a Signal Generator")
        return -1
             
    
    def set_rf_off(self):
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send(":OUTPut:STATe OFF\n".encode())
                return 1
            except:
                return -1
        else:
            print("set rf off failed - device not recognized as a Signal Generator")
        return -1
    
    def set_tx_frequency(self , FREQUENCY_Hz):
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send((":FREQuency:FIXed +"+str(FREQUENCY_Hz)+"\n").encode())
                return 1
            except:
                return -1
        else:
            print("set tx frequency failed - device not recognized as a Signal Generator")
        return -1 
    
    def get_tx_frequency(self):
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send(":FREQuency:FIXed?\n".encode())
                freq_str = (self.__connection.recv(1000).decode())
                freq_str  = freq_str.split("E")
                freq = float(freq_str[0])*(10**float(freq_str[1]))
                return freq
            except:
               return -1      
        else:
            print("get tx frequency failed - device not recognized as a Signal Generator")
        return -1 
    
    def set_tx_power(self , POWER_dBm):
        
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send((":SOURce:POWer:LEVel:IMMediate:AMPLitude "+str(POWER_dBm)+"\n").encode())
                return 1
            except:
                return -1         
        else:
            print("set rx power faield - device not recognized as a Signal Generator")
        return -1 
    
    def get_tx_power(self):
        if self.__type == "Signal Generator" :
            try:
                self.__connection.send(":SOURce:POWer:LEVel:IMMediate:AMPLitude?\n".encode())
                power = self.__connection.recv(1000).decode()
                return power
            except:
                return -1         
        else:
            print("get rx power failed - device not recognized as a Signal Generator")
        return -1 

    
    def set_tx_sweep_parameters(self , start_power , stop_power , start_frequency  , stop_frequency  , points , time):
        if self.__type == "Signal Generator" :
            try:
                power_vector  = np.linspace(start_power , stop_power , points);
                frequency_vector = np.linspace(start_frequency , stop_frequency , points);
                
                power_string = ":SOURce:LIST:POWer"
                for i in range(len(power_vector)):
                    power_string = power_string +' '+ str(i)
                    
                frequency_string = ":SOURce:LIST:FREQuency"
                for i in range(len(frequency_vector)):
                    frequency_string = frequency_string +' '+ str(i)
                    
                
                print(power_string)
                print(frequency_string)
            except:
                return -1











    def set_attenuation(self , ATTENUATION_dB):
        if self.__type == "Spectrum Analyzer" :
            try:
                if (str(type(ATTENUATION_dB)) == "<class 'int'>" and ATTENUATION_dB >= 0  ):
                    self.__connection.send((":POWer:ATTenuation "+str(ATTENUATION_dB) + "\n").encode()) 
                    return 1
                else:   
                    print("** not a valide value") 
            except:
                return -1
        else:
              print("set attenuation failed - device not recognized as a Spectrum Analyzer")   
              return -1
          
            
    def set_referense_level(self , REFF_dB):
        if self.__type == "Spectrum Analyzer" :
            try:
                if (str(type(REFF_dB)) == "<class 'int'>" or str(type(REFF_dB)) == "<class 'float'>" ):
                    self.__connection.send((":DISPlay:WINDow:TRACe:Y:RLEVel "+str(REFF_dB) + "dBm\n").encode())  
                    return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
              print("set reference level failed - device not recognized as a Spectrum Analyzer")   
        return -1
          
    def set_center_frequency(self , FREQUENCY_Hz):
        if self.__type == "Spectrum Analyzer" :
            try:
                if ( FREQUENCY_Hz > 0  ):
                  self.__connection.send((":FREQuency:CENTer " +str(FREQUENCY_Hz) + "HZ\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set center frequency failed - device not recognized as a Spectrum Analyzer")           
        return -1
    
    
    def set_span(self , SPAN_hz):
        if self.__type == "Spectrum Analyzer" :
            try:
                if (str(type(SPAN_hz)) == "<class 'float'>" or str(type(SPAN_hz)) == "<class 'int'>" ):
                  self.__connection.send((":FREQuency:SPAN " +str(SPAN_hz) + "HZ\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set span failed - device not recognized as a Spectrum Analyzer")          
        return -1
    
    def set_rbw(self , RBW_hz):
        if self.__type == "Spectrum Analyzer" :
            try:
                if ( RBW_hz > 0  ):
                  self.__connection.send((":BWIDth " +str(RBW_hz) + "HZ\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set rbw failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    def set_vbw(self , VBW_hz):
        if self.__type == "Spectrum Analyzer" :
            try:
                if ( VBW_hz > 0  ):
                  self.__connection.send((":BWIDth:VIDeo " +str(VBW_hz) + "HZ\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set vbw failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    
    def set_marker_on(self , INDEX):
        if self.__type == "Spectrum Analyzer" :
            try:
                
                if ( INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                  self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":STATe ON\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set marker on failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    
    def set_marker_off(self , INDEX):
        if self.__type == "Spectrum Analyzer" :
            try:
                
                if ( INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                  self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":STATe OFF\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set marker off failed - device not recognized as a Spectrum Analyzer")   
        return -1
        
    def set_marker(self , INDEX , FREQUENCY_hz):
        if self.__type == "Spectrum Analyzer" :
            try:
                self.set_marker_on(INDEX)
                if (FREQUENCY_hz > 0 and INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                  self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":X "+(str(FREQUENCY_hz).replace(".0", ""))+" HZ\n").encode()) 
                  return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set marker failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    def get_marker(self , INDEX ):
        if self.__type == "Spectrum Analyzer" :
            try:
                self.set_marker_on(INDEX)
                if ( INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                    self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":Y?\n").encode()) 
                    Y = float(self.__connection.recv(1000));
                    self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":X?\n").encode()) 
                    X = float(self.__connection.recv(1000));
                    return [X , Y]
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("get marker failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    def set_peak_search(self , INDEX):
        if self.__type == "Spectrum Analyzer" :
            try:
                self.set_marker_on(INDEX)
                if ( INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                    self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":MAXimum\n").encode()) 
                    return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set peak search failed - device not recognized as a Spectrum Analyzer")   
        return -1

    def next_peak_search(self , INDEX , RIGHT_LEFT = "RIGHT"):
        if self.__type == "Spectrum Analyzer" :
            try:
                self.set_marker_on(INDEX)
                if ( INDEX > 0 and str(type(INDEX)) == "<class 'int'>" ):
                    if (RIGHT_LEFT == "RIGHT"):
                        self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":MAXimum:RIGHt\n").encode()) 
                    elif(RIGHT_LEFT == "LEFT"):
                        self.__connection.send((":CALCulate:MARKer"+str(INDEX) + ":MAXimum:LEFT\n").encode()) 
                    else:
                        return -1
                    return 1
                else:
                   print("** not a valide value") 
            except:
                return -1
        else:
            print("set peak search failed - device not recognized as a Spectrum Analyzer")   
        return -1
    
    def get_peak(self , INDEX ):
        if self.__type == "Spectrum Analyzer" :
            try:
                self.set_marker_on(INDEX)
                self.set_peak_search(INDEX)
                return self.get_marker(INDEX)
            except:
                return -1
        else:
            print("set peak search failed - device not recognized as a Spectrum Analyzer")   
        return -1
        
    
        
       