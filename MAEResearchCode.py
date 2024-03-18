import pandas as pd
import os 
import math
import ast

# Test matrix used to label oscilloscope dataframe column names with respective resistance values based on test matrix. UNIQUE TO EXPERIMENT.

test_matrix = {}
test_matrix['MAEQBlade0Degree(pt32psf)'] = ['second',50,25,10,8,6,4,2,.8,.6,.4,.2,0]
test_matrix['MAEQBlade10Degree(pt32psf)'] = ['second',50,25,10,8,6,4,2,.8,.6,.4,.2,0]
test_matrix['MAEQBlade20Degree(pt32psf)'] = ['second',100,50,25,10,9,8,7,6,5,4,3,2,1,.8,.6,.4,.2,.1,0]
test_matrix['MAETHAT0Degree(pt32psf)'] = ['second',50,25,10,8,6,4,2,.8,.6,.4,.2,0]
test_matrix['MAETHAT10Degree(pt32psf)'] = ['second',50,25,10,8,6,4,2,.8,.6,.4,.2,0]
test_matrix['MAETHAT20Degree(pt32psf)'] = ['second',100,50,25,10,9,8,7,6,5,4,3,2,1,0]
global test_matrix



class Dataset:
    
    # Set local filepaths as class variables
    
    oscope_folder = 'D:\\Documents\\March2024WindTunnelTesting\\'
    labview_folder = 'D:\\Documents\\THATMarch1Test_Matthew Simpson\\'
    output_destination = "D:\Documents\MAEResearchOutput"
    
    def __init__(self, skew = 20, blade_design = 'THAT') -> None:
        
        """
        Initializes the Dataset instance with specific parameters and paths, and starts the data processing sequence.

        Parameters:
        - skew (int): The skew angle of the blade design.
        - blade_design (str): The code representing the blade design (THAT or QBlade)
        """
        
        self.labview_dict = {}
        self.oscope_df = pd.DataFrame()
        self.output = pd.DataFrame()
        self.skew = skew
        self.blade_design = blade_design
        
        self.get_oscilloscope_data()
        self.get_labview_data()
        self.process_data()
        
        
        
    def get_oscilloscope_data(self):
        
        """
        Loads and processes oscilloscope data from files into a DataFrame.

        The function reads CSV files, extracts necessary columns, and handles specific preprocessing steps like skipping rows and selecting relevant data. The resulting DataFrame is stored in `self.oscope_df`.
        """
        
        skipr = [0,*range(2,12)]
        subfolder = self.oscope_folder + '\\' + f'MAE{self.blade_design}{self.skew}Degree(pt32psf)'
        available_files = os.listdir(subfolder)
        prefix = available_files[0].split('_')[0]
        sub_df = pd.DataFrame()
        
        # Looping by number and not just by the files themselves is needed since the folders are not in order and because some of
        # the files have a number after 'oscope' and some don't, for ex: 'oscope3_0'
        
        for i in range(len(available_files)):
            
            file = prefix + f'_{i}.csv'
            filepath = subfolder + '\\' + file
            dfin = pd.read_csv(filepath,skiprows = skipr)
            sub_df['second'] = dfin['second']
            sub_df[f'volt_{i}'] = dfin['Volt']
        
        # Since data was collected twice for each resistance value, we can drop every other column
        
        self.oscope_df = sub_df.drop(columns=sub_df.columns[1::2])
        self.oscope_df.columns = test_matrix[f'MAE{self.blade_design}{self.skew}Degree(pt32psf)']
        
        return self.oscope_df

    
    
    def get_labview_data(self):
        
        """
        Loads and processes LabVIEW data from files into a dictionary of DataFrames.

        Each file's contents are read into a DataFrame, which are then stored in a dictionary with the filenames as keys. This dictionary is stored in `self.labview_dict`.
        """
        
        subfolder = self.labview_folder + '\\' + f'20 Deg {self.blade_design} {self.skew} skew 0.32PSF'
        filenames = os.listdir(subfolder)
        names=['Fx','Fy','Fz','Tx','Ty','Tz','null','current1','current2','rpm']
        df_list = [pd.read_csv(subfolder + '\\' + filename,header=None,names=names) for filename in filenames]
        self.labview_dict = dict(zip(filenames,df_list)) 
        
        return self.labview_dict
    
    
    @staticmethod
    def cp_tsr_calculation(df, temp, atm_pressure_psi, q, resistance_ohms,volt_mean) -> list:
        
        """
        Calculates the coefficient of power and the tip speed ratio for a given set of parameters and measurements.

        Parameters:
        - df (DataFrame): The DataFrame containing the relevant measurement data.
        - temp (float): The temperature, in degrees Fahrenheit.
        - atm_pressure_psi (float): The atmospheric pressure, in PSI.
        - q (float): Dynamic pressure, in lb/sqft.
        - resistance_ohms (float): The resistance, in Ohms.
        - volt_mean (float): The mean voltage, in Volts.

        Returns:
        - list: A list containing the velocity (m/s), radians/sec, tip speed ratio, and coefficient of power.
        """
        
        # Set constants
        
        prop_length_m = .15
        hub_length_m = .0127
        r = 8314.45
        molar_mass_air = 28.96
        names=['Fx','Fy','Fz','Tx','Ty','Tz','null','current1','current2','rpm']

        # keep only the recorded values of rpm
        
        dfrpm = df['rpm']
        dfrpm2 = []
        
        for i in dfrpm:
            if i > 0:
                dfrpm2.append(i)
        
        rpm_average = (sum(dfrpm2) / len(dfrpm2))
        rads = rpm_average*0.104719755

        # The voltage dataset for 0 ohms was recorded at .03 ohms
        
        if resistance_ohms == 0:
            resistance_ohms = .03
            
        power_watts = (volt_mean**2)/resistance_ohms

        air_temp_f = temp
        air_temp_k = ((air_temp_f-32)*5/9) + 273.15

        atm_pressure_pascal = atm_pressure_psi*6895

        density = atm_pressure_pascal / ((r/molar_mass_air)*(air_temp_k))
        
        ## ALTERNATIVE POWER CALCULATIONS
        # averages = df.mean()
        # power_watts = resistance_ohms*(averages[7]**2)
        # power_watts = averages[5]*rads
        
        radius_m = prop_length_m + hub_length_m
        area = math.pi*(radius_m**2)
        
        # Velocity measured in m/s
        vel = math.sqrt((2*(q*47.88))/density)
        
        coefficient_power = (power_watts / (((.5)*density)*(area)*(vel**3)))
        
        # rads = radians / second
        rads = rpm_average*0.104719755

        
        tip_speed_ratio = (radius_m*rads)/vel

        return [vel,rads,tip_speed_ratio,coefficient_power] 
    
    
        
    def process_data(self):
        
        """
        Processes the collected LabVIEW and oscilloscope data to calculate and compile output metrics into a DataFrame.

        This function iterates through the LabVIEW data, performing calculations with both the LabVIEW and oscilloscope data. It compiles the results into `self.output`, a DataFrame with the processed data and calculated metrics.
        """
        
        output = pd.DataFrame(columns = ['blade#','resistor_type','dynamic_pressure(lb/sqft)','velocity(m/s)','radians/sec','tip_speed_ratio','coefficient_power'])
        
        for filename,df in self.labview_dict.items():
            
            fname = os.path.splitext(filename)[0]
            fsplit = fname.split('_')
            q = float(fsplit[-1].split(' ')[0])
            blade = fsplit[0].replace('B','')
            temp = float(fsplit[2])
            atm_pressure_psi = float(fsplit[3])
            resistor_type = ast.literal_eval(fsplit[1])
            volt_mean = self.oscope_df[resistor_type].mean()
            function_output = self.cp_tsr_calculation(df,temp,atm_pressure_psi,q,resistor_type,volt_mean)
            pendage = [blade,resistor_type,q] + function_output
            output.loc[len(output)] = pendage
            
        self.output = output
        print(f"DATA FOR SKEW={self.skew}, DESIGN='{self.blade_design}' HAS BEEN PROCESSED")
        
        return self.output
    
    
    
    def post_to_csv(self) -> '.csv file':
        
        """
        Saves the processed data (`self.output`) to a CSV file at the specified output destination.
        """
        filepath = self.output_destination + '\\' + f'{self.blade_design}{self.skew}Output.csv'
        self.output.to_csv(filepath)
        print(f"DATA FOR SKEW={self.skew}, DESIGN='{self.blade_design}' HAS BEEN EXPORTED")
        
        
    
    def print_df(self):
        print("OUTPUT DF",self.output.head())
        print("OSCOPE DF",self.oscope_df.head())
        



### MAIN ###

def main():
    
    QBlade0 = Dataset(skew = 0, blade_design = 'QBlade')
    QBlade10 = Dataset(skew = 10, blade_design = 'QBlade')
    QBlade20 = Dataset(skew = 20, blade_design = 'QBlade')
    THAT0 = Dataset(skew = 0, blade_design = 'THAT')
    THAT10 = Dataset(skew = 10, blade_design = 'THAT')
    THAT20 = Dataset(skew = 20, blade_design = 'THAT')
    
    QBlade0.post_to_csv()
    QBlade10.post_to_csv()
    QBlade20.post_to_csv()
    THAT0.post_to_csv()
    THAT10.post_to_csv()
    THAT20.post_to_csv()
    
if __name__ == "__main__":
    main()