import numpy as np
import ipywidgets as widgets
from ipywidgets import HBox, Label, Image, Output, interact, interact_manual, GridspecLayout
from ipycanvas import Canvas, hold_canvas
from ipycanvas import RoughCanvas as Canvas
from IPython.display import HTML, clear_output

from random import choice, randint, uniform


global lightning
global rain
global temperature

class Forest:
    def __init__(self):
        self.temperature = None
        self.rain = None
        self.lightning = None
        self.wildfires = None
        size_x = 20
        size_y = 20
        self.construct_wildfire_matrix(size_x, size_y, probability_of_rain=0.4, probability_of_lightning=0.2, highest_temperature=90)

    def generate_specific_forest_conditions(self, size_of_x, size_of_y, probability_of_rain, probability_of_lightning, highest_temperature):
        random_number_generator = np.random.default_rng()
        lightning = random_number_generator.binomial(n=1, p=probability_of_lightning, size=(size_of_x, size_of_y))
        rain = random_number_generator.binomial(n=1, p=probability_of_rain, size=(size_of_x, size_of_y))
        lowest_temperature_vector = random_number_generator.normal(0, 1, size=(size_of_x)) * 10
        highest_temperature_vector = lowest_temperature_vector + highest_temperature - max(lowest_temperature_vector)
        temperature = np.linspace(start=lowest_temperature_vector, stop=highest_temperature_vector, num=size_of_x, dtype=int)
        for idx in range(len(temperature)):
            temperature[idx] = np.convolve(temperature[idx], [0.25,0.25,0.25,0.25], mode='same')
        temperature += highest_temperature - np.max(temperature)
        #temperature = np.flip(temperature).T
        return lightning, rain, temperature
        
    def construct_annotation_matrix(self, lightning, rain, temperature):
        annotations = np.empty_like(lightning, dtype='<U48')
        for i in range(annotations.shape[0]):
            for j in range(annotations.shape[1]):
                raining_txt = "True" if rain[i][j] else "False"
                lightning_txt = "True" if lightning[i][j] else "False"
                annotations[i][j] = 'Rain: ' +  raining_txt +\
                                    '<br>Temp: ' + str(temperature[i][j]) +\
                                    '<br>Lightning: ' + lightning_txt
        return annotations
        
    def construct_wildfire_matrix(self, size_x, size_y, probability_of_rain = 0.3, probability_of_lightning = 0.4, highest_temperature=85):
        self.lightning, self.rain, self.temperature = self.generate_specific_forest_conditions(size_of_x=size_x,
                                                                               size_of_y=size_y,
                                                                               probability_of_rain=probability_of_rain,
                                                                               probability_of_lightning=probability_of_lightning,
                                                                               highest_temperature=highest_temperature)

        def is_area_on_fire(x_coordinate, y_coordinate, lightning, rain, temperature):
            if lightning[x_coordinate, y_coordinate] == True:
                area_on_fire = True
            elif temperature[x_coordinate, y_coordinate] > 55 and rain[x_coordinate, y_coordinate] == True:
                area_on_fire = True
            else:
                area_on_fire = False
            return area_on_fire
        wildfires = np.empty_like(self.lightning)
        for i in range(wildfires.shape[0]):
            for j in range(wildfires.shape[1]):
                wildfires[i][j] = is_area_on_fire(i, j, self.lightning, self.rain, self.temperature)
        self.wildfires = wildfires
        return wildfires

    def predict_area_on_fire(self, x_coordinate, y_coordinate, lightning_value, temp_value, rain_value):
        if bool(self.lightning[x_coordinate, y_coordinate]) == (lightning_value == "Yes"):
            area_on_fire = True
        elif self.temperature[x_coordinate, y_coordinate] > temp_value and bool(self.rain[x_coordinate, y_coordinate]) == (rain_value == "Yes"):
            area_on_fire = True
        else:
            area_on_fire = False
        return area_on_fire
        
    def is_lightning(self, x_coordinate, y_coordinate):
        return bool(self.lightning[y_coordinate, x_coordinate])
        
    def is_rainshadow(self, x_coordinate, y_coordinate):
        return bool(self.rain[y_coordinate, x_coordinate])
        
    def get_temperature(self, x_coordinate, y_coordinate):
        return self.temperature[y_coordinate, x_coordinate]

class Drawer:
    def __init__(self, sprite_locations):
        self.sprite_locations  = sprite_locations
        self.canvas = Canvas(width=1500, height=1000//2, sync_image_data=True)
        self.forest_image = Image.from_file("forest.png")

    def draw_canvas(self,
                    forest,
                    canvas_size_x,
                    canvas_size_y,
                    size_x,
                    size_y,
                    draw_predictions=False,
                    predictions=None,
                    lightning_input=None,
                    temperature_input=None,
                    rain_shadow_input=None):


        self.canvas.draw_image(self.forest_image)

        with hold_canvas(self.canvas):
            self.canvas.fill_style = "#ff3636"
            self.canvas.roughness = 0
            self.canvas.line_width = 4.0
            self.canvas.rough_fill_style = "solid"

            if draw_predictions:
                for i in range(predictions.shape[0]):
                    for j in range(predictions.shape[1]):
                        if predictions[i][j]:
                            x, y, scale = self.sprite_locations[str([i, j])]
                            self.canvas.scale(scale)
                            #canvas.draw_image(fire_sprite, x, y, height=15, width=15)
                            self.canvas.fill_rect(x+50, y+50, height=15*scale, width=15*scale)


        out = Output()
        @out.capture()
        def handle_mouse_down(x, y):
            x = x-50
            y = y-50
            coord_x = int(size_x*(x-100)/canvas_size_x)
            coord_y = int(size_y*y/canvas_size_y)
            if coord_x > size_x-1 or coord_y > size_y-1 or coord_x < 0 or coord_y < 0:
                return
            annotation = f'The selected area ({coord_x}, {coord_y}) is '

            if coord_x < 0 or forest.wildfires[coord_y, coord_x]:
                annotation += "burning."
            else:
                annotation += "not burning."
            annotation += f'The temperature is {forest.get_temperature(coord_x, coord_y)}°F.It is '
            if forest.is_rainshadow(coord_x, coord_y):
                annotation += 'a rainshadow area.There are '
            else:
                annotation += 'not a rainshadow area.There are '
            if forest.is_lightning(coord_x, coord_y):
                annotation += 'lightning strikes in the area.'
            else:
                annotation += 'no lightning strikes in the area.'
            with hold_canvas(self.canvas):
                self.canvas.restore()
                self.canvas.clear_rect(x=50+1100//2, y=0+50, width=800, height=2000//2)
                canvas_width = 1500
                canvas_height = 800//2
                center_align = 400//2


                self.canvas.stroke_line(50+1100//2+1, center_align, 50+1400//2, center_align)
                self.canvas.stroke_line(50+1400//2-10, center_align+10, 50+1400//2, center_align)
                self.canvas.stroke_line(50+1400//2-10, center_align-10, 50+1400//2, center_align)
                self.canvas.fill_style = "#000000"
                self.canvas.font = "14px Comic Sans MS"
                split_annotations = annotation.split('.')
                self.canvas.fill_text(split_annotations[0], 50+1500//2, center_align-30)
                self.canvas.fill_text(split_annotations[1], 50+1500//2, center_align-10)
                self.canvas.fill_text(split_annotations[2], 50+1500//2, center_align+10)
                self.canvas.fill_text(split_annotations[3], 50+1500//2, center_align+30)

        self.canvas.on_mouse_down(handle_mouse_down)
        return self.canvas

    def clr_canvas(self):
        self.canvas.clear()
        self.canvas.fill_style = '#FFFFFF'
        self.canvas.fill_rect(0, 0, width=1500, height=1000//2)


    def draw_canvas_without_controls(self, forest, canvas_size_x = 800//2, canvas_size_y = 800//2, size_x = 20, size_y = 20):
        grid = GridspecLayout(20, 10)
        temperature_input = widgets.FloatSlider(min=0,
                                      max=100,
                                      #description="Probability of Lightning Strike" ,
                                      disabled=False,
                                      orientation='horizontal',
                                      readout=True,
                                      step=1,
                                      value=0,
                                      #style={"handle_color": color[i]},
                                      layout=widgets.Layout(width='200px'))

        lightning_input = widgets.Dropdown(value="No", options=["No", "Yes"], layout=widgets.Layout(width="200px", padding="0px"))
        rain_shadow_input = widgets.Dropdown(value="No", options=["No", "Yes"], layout=widgets.Layout(width="200px", padding="0px"))

        predictions = np.random.randint(2, size=forest.wildfires.shape)
        self.draw_canvas(forest,
                          canvas_size_x=canvas_size_x,
                          canvas_size_y=canvas_size_y,
                          size_x=20,
                          size_y=20,
                          draw_predictions=False,
                          predictions=predictions,
                          lightning_input=lightning_input,
                          temperature_input=temperature_input,
                          rain_shadow_input=rain_shadow_input)

        grid[6:, 1:6] = self.canvas
        display(grid)

        # redraw everything because it doesn't always work when drawing only once :((
        self.canvas.draw_image(self.forest_image)


    def draw_canvas_with_controls(self, forest, canvas_size_x = 800//2, canvas_size_y = 800//2, size_x = 20, size_y = 20,
                                  temperature_value=0, lightning_value="No", rain_shadow_value="No"):
        grid = GridspecLayout(20, 10)
        temperature_input = widgets.FloatSlider(min=0,
                                      max=100,
                                      #description="Probability of Lightning Strike" ,
                                      disabled=False,
                                      orientation='horizontal',
                                      readout=True,
                                      step=1,
                                      value=temperature_value,
                                      #style={"handle_color": color[i]},
                                      layout=widgets.Layout(width='200px'))

        lightning_input = widgets.Dropdown(value=lightning_value, options=["No", "Yes"], layout=widgets.Layout(width="200px", padding="0px"))
        rain_shadow_input = widgets.Dropdown(value=rain_shadow_value, options=["No", "Yes"], layout=widgets.Layout(width="200px", padding="0px"))

        predictions = np.random.randint(2, size=forest.wildfires.shape)
        for i in range(predictions.shape[0]):
            for j in range(predictions.shape[1]):
                if forest.predict_area_on_fire(i, j, lightning_input.value, temperature_input.value, rain_shadow_input.value) != forest.wildfires[i][j]:
                    predictions[i][j] = 1
                else:
                    predictions[i][j] = 0

        self.draw_canvas(forest,
                          canvas_size_x=canvas_size_x,
                          canvas_size_y=canvas_size_y,
                          size_x=20,
                          size_y=20,
                          draw_predictions=True,
                          predictions=predictions,
                          lightning_input=lightning_input,
                          temperature_input=temperature_input,
                          rain_shadow_input=rain_shadow_input)

        grid[6:, 1:6] = self.canvas

        grid[1,1:7] = widgets.HBox(
                [widgets.HTML("<h1>A wildfire will occur if an area meets the following two conditions:</h1>", style={"text_color":"black", "font_weight":"bold", "font_size":"50px"})
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))

        grid[2,1:4] = widgets.HBox(
                [widgets.HTML("<h3>Lightning Strike Occurence: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 lightning_input
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))

        grid[3,1:3] = widgets.HBox(
                [widgets.HTML("<h3>OR</h3>", style={"text_color":"red", "font_weight":"bold", "font_size":"30px"})
                ], layout=widgets.Layout(align_items="center", justify_content="flex-start"))

        grid[4,1:4] = widgets.HBox(
                [widgets.HTML("<h3>Rain-Shadow: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 rain_shadow_input,
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))

        grid[4,4] = widgets.HBox(
                [widgets.HTML("<h3>AND</h3>", style={"text_color":"red", "font_weight":"bold", "font_size":"30px"})
                ], layout=widgets.Layout(align_items="center", justify_content="center"))

        grid[4,5:8] = widgets.HBox(
                [widgets.HTML("<h3>Temperature is greater than: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 temperature_input
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))


        button = widgets.Button(description="Click to anticipate wildfires!")
        def on_button_clicked(b):
            clear_output(wait=True)
            self.clr_canvas()

            self.draw_canvas_with_controls(forest,
                                           temperature_value=temperature_input.value,
                                           lightning_value=lightning_input.value,
                                           rain_shadow_value=rain_shadow_input.value)

        button.on_click(on_button_clicked)
        grid[5,1:4] = button
        display(grid)
        # redraw everything because it doesn't always work when drawing only once :((
        with hold_canvas(self.canvas):
          self.canvas.draw_image(self.forest_image)
          self.canvas.fill_style = "#ff3636"
          self.canvas.roughness = 0
          self.canvas.line_width = 3.0
          self.canvas.rough_fill_style = "solid"

          for i in range(predictions.shape[0]):
              for j in range(predictions.shape[1]):
                  if predictions[i][j]:
                      x, y, scale = self.sprite_locations[str([i, j])]
                      x += 50
                      y += 50
                      self.canvas.scale(scale)
                      self.canvas.fill_rect(x, y, height=15*scale, width=15*scale)
