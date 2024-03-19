from MAEResearchCode import Dataset
import numpy as np
import pandas as pd
import seaborn as sns

def main():

    QBlade0 = Dataset(skew = 0, blade_design = 'QBlade')
    QBlade10 = Dataset(skew = 10, blade_design = 'QBlade')
    QBlade20 = Dataset(skew = 20, blade_design = 'QBlade')
    THAT0 = Dataset(skew = 0, blade_design = 'THAT')
    THAT10 = Dataset(skew = 10, blade_design = 'THAT')
    THAT20 = Dataset(skew = 20, blade_design = 'THAT')

    master = Dataset.combined_instance_df()
    master = master.filter(items=['blade_design', 'skew_angle', 'tip_speed_ratio', 'coefficient_power'])
    master = master.rename(columns={'blade_design' : 'Blade Design'})

    # 20 DEGREE PLOT
    sns.set_theme()
    sns.set_style("darkgrid")
    g = sns.relplot(data=master,
                    x = 'tip_speed_ratio', 
                    y = 'coefficient_power', 
                    col = 'skew_angle',
                    linewidth=2.5, 
                    hue = 'Blade Design',
                    style = 'Blade Design',
                    kind = 'line',
                    markers = True,
                    dashes = False,
                    legend = 'auto'
                    )

    (g.set_axis_labels("Tip Speed Ratio (rad/s)", "Coefficient of Power")
      .set_titles("Skew Angle: {col_name}")
      .set
    )
    
    g.figure.savefig("MAEResearchOutput.png")
    
    
if __name__ == "__main__":
    main()