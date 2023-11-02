import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ipywidgets as widgets
from ipywidgets import HBox, Label
from IPython.display import HTML, display

global lightning
global rain
global temperature

class Forest:
    def __init__(self):
        self.temperature = None
        self.rain = None
        self.lightning = None

    def regenerate_forest(self, probability_of_rain, probability_of_lightning, highest_temperature, display_f=True):
        def plot_state(inputs, labels):
            #green = px.colors.qualitative.Set2[4]
            #red = px.colors.qualitative.Set1[0]
            # colorblind colors: https://davidmathlogic.com/colorblind/#%23E63452-%231E88E5-%23FFC107-%23004D40
            red = "#E63452"
            green = "#05D0EA"
            fig = go.Figure(data=go.Heatmap(
                                z=inputs,
                                text=labels,
                                texttemplate="",#"%{text}",
                                textfont={"size":30},
                                xgap=1,
                                ygap=1,
                                colorscale=[(0.00, green),   (0.5, green),
                                        (0.5, red),  (1.00, red)],
                                colorbar=dict(
                                    tickfont={"size":20},
                                    tickmode="array",
                                    tickvals=[0, 0.25, 0.75, 1],
                                    ticktext=["", "Not Burning", "Burning", ""],
                                    ticks="inside"),
                                hovertemplate = 'Coordinate: %{x},%{y}<br>'+'%{text}<extra></extra>',
            ))
            
            if display_f:
              fig.update_layout(
                  autosize=True,
                  width=900,
                  height=800,
                  plot_bgcolor="#fff",
                  hoverlabel=dict(
                      bgcolor="white",
                      font_size=15,
                  ),
                  title={
                      'text': "Simulation of Forest Wildfires",
                      'x':0.46,
                      'xanchor': 'center',
                      'yanchor': 'top',
                      'font': dict(size=30)
                  },
              )
            else:
              fig.update_layout(
                autosize=True,
                width=10,
                height=10,
                plot_bgcolor="#fff",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=1,
                ),
                title={
                    'text': "Simulation of Forest Wildfires",
                    'x':0.46,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=2)
                },
            )

            return fig
            
        def generate_specific_forest_conditions(size_of_x, size_of_y, probability_of_rain, probability_of_lightning, highest_temperature):
            random_number_generator = np.random.default_rng()
            lightning = random_number_generator.binomial(n=1, p=probability_of_lightning, size=(size_of_x, size_of_y))
            rain = random_number_generator.binomial(n=1, p=probability_of_rain, size=(size_of_x, size_of_y))
            lowest_temperature_vector = random_number_generator.normal(0, 1, size=(size_of_x)) * 10
            highest_temperature_vector = lowest_temperature_vector + highest_temperature - max(lowest_temperature_vector)
            temperature = np.linspace(start=lowest_temperature_vector, stop=highest_temperature_vector, num=size_of_x, dtype=int)
            for idx in range(len(temperature)):
                temperature[idx] = np.convolve(temperature[idx], [0.25,0.25,0.25,0.25], mode='same')
            temperature += highest_temperature - np.max(temperature)
            temperature = np.flip(temperature).T
            return lightning, rain, temperature
            
        def construct_annotation_matrix(lightning, rain, temperature):
            annotations = np.empty_like(lightning, dtype='<U48')
            for i in range(annotations.shape[0]):
                for j in range(annotations.shape[1]):
                    raining_txt = "True" if rain[i][j] else "False"
                    lightning_txt = "True" if lightning[i][j] else "False"
                    annotations[i][j] = 'Rain: ' +  raining_txt +\
                                        '<br>Temp: ' + str(temperature[i][j]) +\
                                        '<br>Lightning: ' + lightning_txt
            return annotations
            
        def construct_wildfire_matrix(lightning, rain, temperature):
            def is_area_on_fire(x_coordinate, y_coordinate, lightning, rain, temperature):
                if lightning[x_coordinate, y_coordinate] == True:
                    area_on_fire = True
                elif temperature[x_coordinate, y_coordinate] > 55 and rain[x_coordinate, y_coordinate] == False:
                    area_on_fire = True
                else:
                    area_on_fire = False
                return area_on_fire
            wildfires = np.empty_like(lightning)
            for i in range(wildfires.shape[0]):
                for j in range(wildfires.shape[1]):
                    wildfires[i][j] = is_area_on_fire(i, j, lightning, rain, temperature)
            return wildfires
            
        self.lightning, self.rain, self.temperature = generate_specific_forest_conditions(size_of_x=35,
                                                                                           size_of_y=35,
                                                                                           probability_of_rain=probability_of_rain,
                                                                                           probability_of_lightning=probability_of_lightning,
                                                                                           highest_temperature=highest_temperature)
        annotations = construct_annotation_matrix(self.lightning, self.rain, self.temperature)
        wildfires = construct_wildfire_matrix(self.lightning, self.rain, self.temperature)
        fig = plot_state(wildfires, annotations)
        display(fig)
        #return fig
    
    def display_forest(self):
        display(HTML('''<style>
            .widget-label { min-width: 30ex !important; }
        </style>'''))
        
        probability_of_rain = widgets.FloatSlider(min=0, 
                                                  max=1,
                                                  step=0.1,
                                                  readout=True)
        probability_of_lightning = widgets.FloatSlider(min=0.1, 
                                                       max=1,
                                                       step=0.1,
                                                       readout=True)
        highest_temperature = widgets.IntSlider(min=20, 
                                                max=100,
                                                step=1,
                                                readout=True)
        
        output = widgets.interactive_output(self.regenerate_forest, {'probability_of_rain': probability_of_rain,
                                                                    'probability_of_lightning': probability_of_lightning,
                                                                    'highest_temperature': highest_temperature})
        self.regenerate_forest(probability_of_rain.value, probability_of_lightning.value, highest_temperature.value, display_f=False)
        widget = widgets.GridBox([widgets.GridBox([HBox([Label('Probability of Rain'), probability_of_rain]),
                                                   HBox([Label('Probability of Lightning'), probability_of_lightning]),
                                                   HBox([Label('Highest Temperature'), highest_temperature])]), output])
        return widget

    def is_lightning(self, x_coordinate, y_coordinate):
        return bool(self.lightning[y_coordinate, x_coordinate])
        
    def is_raining(self, x_coordinate, y_coordinate):
        return bool(self.rain[y_coordinate, x_coordinate])
        
    def get_temperature(self, x_coordinate, y_coordinate):
        return self.temperature[y_coordinate, x_coordinate]
