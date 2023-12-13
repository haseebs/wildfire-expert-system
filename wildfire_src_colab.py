import numpy as np
import ipywidgets as widgets
from ipywidgets import HBox, Label, Image, Output, interact, interact_manual, GridspecLayout
from ipycanvas import Canvas, hold_canvas
from ipycanvas import RoughCanvas as Canvas
from IPython.display import HTML, display, clear_output

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
        
    def is_raining(self, x_coordinate, y_coordinate):
        return bool(self.rain[y_coordinate, x_coordinate])
        
    def get_temperature(self, x_coordinate, y_coordinate):
        return self.temperature[y_coordinate, x_coordinate]



class Drawer:
    def __init__(self, forest):
        self.sprite_locations  = {}
        self.annotation = ""
        self.forest = forest
        #canvas_size_x = 800
        #canvas_size_y = 800
        #canvas = self.draw_canvas(forest, canvas_size_x=canvas_size_x, canvas_size_y=canvas_size_y, size_x=30, size_y=30)
        #display(canvas)

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
        self.forest = forest
        self.canvas_size_x = canvas_size_x
        self.canvas_size_y = canvas_size_y
        self.size_x = size_x
        self.size_y = size_y
        
        tree_sprite = Image.from_file("sprites/tree1.png")
        fire_sprite = Image.from_file("sprites/fire.png")
        mountain_sprite = Image.from_file("sprites/mountain.png")
        
        sprites = []
        sprites.append(Canvas(width=20, height=20))
        sprites[0].draw_image(tree_sprite, 0, 0, width=20, height=20)
        
        sprites.append(Canvas(width=20, height=20))
        sprites[1].draw_image(fire_sprite, 0, 0, width=20, height=20)
        
        sprites.append(Canvas(width=20, height=20))
        sprites[2].draw_image(mountain_sprite, 0, 0, width=20, height=20)
    
        wildfire_state = forest.wildfires
        
        canvas = Canvas(width=1500, height=1000//2)
        canvas.translate(100//2, 100//2)
        
        canvas.fill_style = "#93cc5e"
        canvas.roughness = 25
        canvas.rough_fill_style = "cross-hatch"
        canvas.fill_rect(0, 0, 1000//2, 800//2)
        
        canvas.fill_style = "#6A9F3A"
        canvas.roughness = 12
        canvas.rough_fill_style = "cross-hatch"
        canvas.fill_rect(0, 0, 1000//2, 800//2)
        
        canvas.rough_fill_style = "zigzag"
        canvas.fill_rect(0, 0, 1000//2, 800//2)
        
        canvas.rough_fill_style = "cross-hatch"
        canvas.roughness = 1
        canvas.fill_rect(0, 0, 1000//2, 800//2)
        canvas.fill_style = "#000000"
        canvas.font = "30px helvetica"
        
        with hold_canvas(canvas):
            center_align = 400//2
            canvas.stroke_line(1100//2+1, center_align, 1400//2, center_align)
            canvas.stroke_line(1400//2-10, center_align+10, 1400//2, center_align)
            canvas.stroke_line(1400//2-10, center_align-10, 1400//2, center_align)
            canvas.fill_style = "#000000"
            canvas.font = "18px Comic Sans MS"
            canvas.fill_text("Click on the forest to view details here", 1500//2, 400//2)
    
        with hold_canvas(canvas):
            for _ in range(1000//2):
                canvas.save()
                sprite = mountain_sprite
        
                # Choose a random sprite position
                pos_x = randint(0, 180//2)
                pos_y = randint(0, 780//2)
        
                # Choose a random rotation angle (but first set the rotation center with `translate`)
                canvas.translate(pos_x, pos_y)
        
                # Choose a random sprite size
                canvas.scale(uniform(0.4, 1.2))
        
                # Restore the canvas center
                canvas.translate(-pos_x, -pos_y)
        
                # Draw the sprite
                canvas.draw_image(sprite, pos_x, pos_y, height=15, width=15)
        
                canvas.restore()
            
            for x in range(size_x):
                for y in range(size_y):
                    canvas.save()
                    if wildfire_state[y,x]:
                        sprite = fire_sprite
                    else:
                        sprite = tree_sprite
                
                    # Choose a random sprite position
                    #pos_x = randint(-10,10) + 200//2+canvas_size_x*x/size_x 
                    #pos_y = randint(-10,10) + canvas_size_y*y/size_y
                    pos_x = 200//2+canvas_size_x*x/size_x 
                    pos_y = canvas_size_y*y/size_y
        
                    # Choose a random rotation angle (but first set the rotation center with `translate`)
                    #canvas.translate(pos_x, pos_y)
            
                    # Choose a random sprite size
                    #scale = uniform(0.6, 1.5)
                    scale=1
                    canvas.scale(scale)
                    self.sprite_locations[str([x,y])] = pos_x, pos_y, scale
            
                    # Restore the canvas center
                    #canvas.translate(-pos_x, -pos_y)

                    # Draw the sprite
                    canvas.draw_image(sprite, pos_x, pos_y, height=15, width=15)
                    #canvas.fill_rect(pos_x, pos_y, height=15, width=15)

                    canvas.restore()
            canvas.fill_style = "#ff3636"
            canvas.roughness = 0
            canvas.line_width = 4.0
            canvas.rough_fill_style = "solid"

            if draw_predictions:
                for i in range(predictions.shape[0]):
                    for j in range(predictions.shape[1]):
                        if forest.predict_area_on_fire(i, j, lightning_input.value, temperature_input.value, rain_shadow_input.value) != forest.wildfires[i][j]:
                            x, y, scale = self.sprite_locations[str([i, j])]
                            canvas.scale(scale)
                            #canvas.draw_image(fire_sprite, x, y, height=15, width=15)
                            canvas.fill_rect(x, y, height=15*scale, width=15*scale)
        

        out = Output()
        @out.capture()
        def handle_mouse_down(x, y):
            x = x-100
            y = y-100
            coord_x = int(size_x*(x-200)/canvas_size_x)
            coord_y = int(size_y*y/canvas_size_y)
            if coord_x > size_x-1 or coord_y > size_y-1 or coord_x < 0 or coord_y < 0:
                return
            annotation = f'The selected area ({coord_x}, {coord_y}) is '
        
            if coord_x < 0 or forest.wildfires[coord_y, coord_x]:
                annotation += "burning."
            else:
                annotation += "not burning."
            annotation += f'The temperature is {forest.get_temperature(coord_x, coord_y)}°C.It is '
            if forest.is_raining(coord_x, coord_y):
                annotation += 'raining.There are '
            else:
                annotation += 'not raining.There are '
            if forest.is_lightning(coord_x, coord_y):
                annotation += 'lightning strikes in the area.'
            else:
                annotation += 'no lightning strikes in the area.'
            with hold_canvas(canvas):
                canvas.restore()
                canvas.clear_rect(x=1100//2, y=0, width=800, height=2000//2)
                canvas_width = 1500
                canvas_height = 800//2
                center_align = 400//2
            
            
                canvas.stroke_line(1100//2+1, center_align, 1400//2, center_align)
                canvas.stroke_line(1400//2-10, center_align+10, 1400//2, center_align)
                canvas.stroke_line(1400//2-10, center_align-10, 1400//2, center_align)
                canvas.fill_style = "#000000"
                canvas.font = "14px Comic Sans MS"
                split_annotations = annotation.split('.')
                canvas.fill_text(split_annotations[0], 1500//2, center_align-30)
                canvas.fill_text(split_annotations[1], 1500//2, center_align-10)
                canvas.fill_text(split_annotations[2], 1500//2, center_align+10)
                canvas.fill_text(split_annotations[3], 1500//2, center_align+30)
    
        canvas.on_mouse_down(handle_mouse_down)
        #display(canvas)
        return canvas

    def draw_canvas_without_controls(self, forest, canvas_size_x = 800//2, canvas_size_y = 800//2, size_x = 20, size_y = 20):
        grid = GridspecLayout(20, 10)
        display(grid)
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
        canvas = self.draw_canvas(forest, 
                                  canvas_size_x=canvas_size_x, 
                                  canvas_size_y=canvas_size_y, 
                                  size_x=20, 
                                  size_y=20, 
                                  draw_predictions=False,
                                  predictions=predictions,
                                  lightning_input=lightning_input,
                                  temperature_input=temperature_input,
                                  rain_shadow_input=rain_shadow_input)

        grid[5:, 1:6] = canvas

    def draw_canvas_with_controls(self, forest, canvas_size_x = 800//2, canvas_size_y = 800//2, size_x = 20, size_y = 20,
                                  temperature_value=0, lightning_value="No", rain_shadow_value="No"):
        grid = GridspecLayout(20, 10)
        display(grid)
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
        canvas = self.draw_canvas(forest, 
                                  canvas_size_x=canvas_size_x, 
                                  canvas_size_y=canvas_size_y, 
                                  size_x=20, 
                                  size_y=20, 
                                  draw_predictions=True,
                                  predictions=predictions,
                                  lightning_input=lightning_input,
                                  temperature_input=temperature_input,
                                  rain_shadow_input=rain_shadow_input)

        grid[5:, 1:6] = canvas
        
        grid[0,1:7] = widgets.HBox(
                [widgets.HTML("<h1>A wildfire will occur if an area meets the following two conditions:</h1>", style={"text_color":"black", "font_weight":"bold", "font_size":"50px"})
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))
        
        grid[1,1:4] = widgets.HBox(
                [widgets.HTML("<h3>Lightning Strike Occurence: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 lightning_input
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))
        
        grid[2,1:3] = widgets.HBox(
                [widgets.HTML("<h3>OR</h3>", style={"text_color":"red", "font_weight":"bold", "font_size":"30px"})
                ], layout=widgets.Layout(align_items="center", justify_content="flex-start"))
        
        grid[3,1:4] = widgets.HBox(
                [widgets.HTML("<h3>Rain-Shadow: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 rain_shadow_input,
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))
        
        grid[3,4] = widgets.HBox(
                [widgets.HTML("<h3>AND</h3>", style={"text_color":"red", "font_weight":"bold", "font_size":"30px"})
                ], layout=widgets.Layout(align_items="center", justify_content="center"))
        
        grid[3,5:8] = widgets.HBox(
                [widgets.HTML("<h3>Temperature is greater than: </h3>", style={"text_color":"black", "font_weight":"bold", "font_size":"20px"}),
                 temperature_input
                ], layout=widgets.Layout(align_items="center", justify_content="space-between"))
        

        button = widgets.Button(description="Click to predict!")
        def on_button_clicked(b):
            clear_output(wait=True)

            self.draw_canvas_with_controls(forest,
                                           temperature_value=temperature_input.value,
                                           lightning_value=lightning_input.value,
                                           rain_shadow_value=rain_shadow_input.value)

        button.on_click(on_button_clicked)
        grid[4,1:4] =button     
        #return grid
