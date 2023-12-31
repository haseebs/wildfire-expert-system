
class Drawer:
    def __init__(self, sprite_locations):
        self.sprite_locations  = sprite_locations

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
        
        forest_image = Image.from_file("forest.png")

        canvas = Canvas(width=1500, height=1000//2)

        with hold_canvas(canvas):
            canvas.save()
            canvas.draw_image(forest_image)
            canvas.restore()
            
        with hold_canvas(canvas):
            canvas.fill_style = "#ff3636"
            canvas.roughness = 0
            canvas.line_width = 4.0
            canvas.rough_fill_style = "solid"

            if draw_predictions:
                for i in range(predictions.shape[0]):
                    for j in range(predictions.shape[1]):
                        if predictions[i][j]:
                            x, y, scale = self.sprite_locations[str([i, j])]
                            canvas.scale(scale)
                            #canvas.draw_image(fire_sprite, x, y, height=15, width=15)
                            canvas.fill_rect(x+50, y+50, height=15*scale, width=15*scale)
        

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
            annotation += f'The temperature is {forest.get_temperature(coord_x, coord_y)}°C.It is '
            if forest.is_rainshadow(coord_x, coord_y):
                annotation += 'a rainshadow area.There are '
            else:
                annotation += 'not a rainshadow area.There are '
            if forest.is_lightning(coord_x, coord_y):
                annotation += 'lightning strikes in the area.'
            else:
                annotation += 'no lightning strikes in the area.'
            with hold_canvas(canvas):
                canvas.restore()
                canvas.clear_rect(x=50+1100//2, y=0+50, width=800, height=2000//2)
                canvas_width = 1500
                canvas_height = 800//2
                center_align = 400//2
            
            
                canvas.stroke_line(50+1100//2+1, center_align, 50+1400//2, center_align)
                canvas.stroke_line(50+1400//2-10, center_align+10, 50+1400//2, center_align)
                canvas.stroke_line(50+1400//2-10, center_align-10, 50+1400//2, center_align)
                canvas.fill_style = "#000000"
                canvas.font = "14px Comic Sans MS"
                split_annotations = annotation.split('.')
                canvas.fill_text(split_annotations[0], 50+1500//2, center_align-30)
                canvas.fill_text(split_annotations[1], 50+1500//2, center_align-10)
                canvas.fill_text(split_annotations[2], 50+1500//2, center_align+10)
                canvas.fill_text(split_annotations[3], 50+1500//2, center_align+30)
    
        canvas.on_mouse_down(handle_mouse_down)
        #display(canvas)
        return canvas

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
        display(grid)


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
        display(grid)
        #return grid
