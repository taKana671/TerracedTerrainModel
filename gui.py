import direct.gui.DirectGuiGlobals as DGG
from panda3d.core import Point3, LColor, Vec4
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib
from direct.gui.DirectGui import DirectEntry, DirectFrame, DirectLabel, DirectButton, DirectRadioButton


class RadioButton(DirectRadioButton):

    def __init__(self, parent, txt, pos, variable, command):
        super().__init__(
            parent=parent,
            pos=pos,
            frameSize=(-2.5, 2.5, -0.5, 0.5),
            frameColor=(1, 1, 1, 0),
            scale=0.06,
            text_align=TextNode.ALeft,
            text=txt,
            text_pos=(-1.5, -0.3),
            text_fg=(1, 1, 1, 1),
            value=[txt],
            variable=variable,
            command=command
        )
        self.initialiseoptions(type(self))


class Button(DirectButton):

    def __init__(self, parent, txt, pos, command):
        super().__init__(
            parent=parent,
            pos=pos,
            relief=DGG.RAISED,
            # frameSize=(-0.28, 0.28, -0.05, 0.05),
            frameSize=(-0.35, 0.35, -0.05, 0.05),
            frameColor=Gui.frame_color,
            borderWidth=(0.01, 0.01),
            text=txt,
            text_fg=Gui.text_color,
            text_scale=Gui.text_size,
            # text_font=self.font,
            text_pos=(0, -0.01),
            command=command
        )
        self.initialiseoptions(type(self))

    def make_deactivate(self):
        self['state'] = DGG.DISABLED

    def make_activate(self):
        self['state'] = DGG.NORMAL


class Label(DirectLabel):

    def __init__(self, parent, txt, pos):
        super().__init__(
            parent=parent,
            pos=pos,
            frameColor=LColor(1, 1, 1, 0),
            text=txt,
            text_fg=Gui.text_color,
            # text_font=self.font,
            # text_scale=Gui.text_size,
            text_scale=0.05,
            text_align=TextNode.ALeft
        )
        self.initialiseoptions(type(self))


class Entry(DirectEntry):

    def __init__(self, parent, pos, txt='', width=4):
        super().__init__(
            parent=parent,
            pos=pos,
            relief=DGG.SUNKEN,
            frameColor=Gui.frame_color,
            text_fg=Gui.text_color,
            # text_scale=Gui.text_size,
            width=width,
            # scale=Gui.text_size * 0.9,
            scale=0.05,
            numLines=1,
            # text_font=self.font,
            initialText=txt,
        )
        self.initialiseoptions(type(self))

    def change_frame_color(self, warning=False):
        if warning:
            self['frameColor'] = LColor(1, 0, 0, 0.3)
        else:
            if self['frameColor'] != Gui.frame_color:
                self['frameColor'] = Gui.frame_color

    def make_deactivate(self):
        self['state'] = DGG.DISABLED

    def make_activate(self):
        self['state'] = DGG.NORMAL

    def is_active(self):
        return self['state'] == DGG.NORMAL


class Gui(DirectFrame):

    frame_color = LColor(0.6, 0.6, 0.6, 1)
    text_color = LColor(1.0, 1.0, 1.0, 1.0)
    text_size = 0.06

    def __init__(self, parent):
        super().__init__(
            parent=parent,
            frameSize=Vec4(-0.6, 0.6, -1., 1.),
            frameColor=Gui.frame_color,
            pos=Point3(0, 0, 0),
            relief=DGG.SUNKEN,
            borderWidth=(0.01, 0.01)
        )
        self.initialiseoptions(type(self))
        self.set_transparency(TransparencyAttrib.MAlpha)

        self.entries = {}
        self.btns = []

        self.terrain_var = []
        self.noise_var = []
        self.theme_var = []



        # self.input_items = {
        #     'scale': float, 'segs_c': int, 'radius': float, 'max_depth': int, 'octaves': int}
        # self.input_items = {
        #     'noise_scale': float, 'segs_c': int, 'radius': float, 'max_depth': int, 'octaves': int}
        self.input_items = {
            'noise_scale': float,
            'segs_c': int,
            'radius': float,
            'terrain_scale': float,
            'max_depth': int,
            'octaves': int,
            'persistence': float,
            'lacunarity': float,
            'amplitude': float,
            'frequency': float
        }

    def create_control_widgets(self):
        self.create_entries(0.2)
        self.create_radios(0.9)
        # self.create_radios(0.85)
        self.create_buttons(-0.7)

    def create_buttons(self, start_z):

        self.btns.append(Button(
            self, 'Reflect Changes', Point3(0, 0, start_z), base.start_terrain_change))
        self.btns.append(Button(
            self, 'Output BamFile', Point3(0, 0, start_z - 0.1), base.output_bam_file))
        self.btns.append(Button(
            self, 'Toggle Wireframe', Point3(0, 0, start_z - 0.2), base.toggle_wireframe))

    def create_entries(self, start_z):
        """Create entry boxes and their labels.
        """
        for i, name in enumerate(self.input_items.keys()):
            # z = start_z - i * 0.1
            z = start_z - i * 0.08
            Label(self, name, Point3(-0.32, 0.0, z))
            entry = Entry(self, Point3(0.07, 0, z))
            self.entries[name] = entry

            if i == 0:
                entry['focus'] = 1

    def create_radios(self, start_z):
        """Create radio buttons to select a noise and a theme.
        """
        # Create terrain type radio buttons
        terrains = ['Flat', 'Sphere']
        self.terrain_var += terrains[:1]
        start_x = -0.18
        radios = []

        for i, name in enumerate(terrains):
            x = start_x + i * 0.25
            pos = (x, 0, start_z)
            radio = RadioButton(self, name, pos, self.terrain_var, self.set_default_values)
            radios.append(radio)

        for r in radios:
            r.setOthers(radios)

        start_z -= 0.06 * 2

        noises = ['SimplexNoise', 'CelullarNoise', 'PerlinNoise']
        # noises = ['PerlinNoise', 'SimplexNoise', 'CelullarNoise']
        # noises = ['CelullarNoise', 'PerlinNoise', 'SimplexNoise']
        themes = ['Mountain', 'SnowMountain', 'Desert', 'Island']
        # self.terrain = terrains[:1]
        self.noise_var += noises[:1]
        self.theme_var += themes[:1]

        items = [
            [noises, self.noise_var, self.set_default_values],
            [themes, self.theme_var, ''],
        ]

        for names, variable, func in items:
            radios = []

            for i, name in enumerate(names):
                z = start_z - i * 0.06
                pos = (-0.18, 0, z)
                radio = RadioButton(self, name, pos, variable, func)
                radios.append(radio)

            for r in radios:
                r.setOthers(radios)

            start_z = z - 0.06 * 2

    # def set_input_values(self, default_values):
    def set_default_values(self):
        if self.terrain_var and self.noise_var:
            default_values = base.create_terrain_generator()

            for k, v in default_values.items():
                entry = self.entries[k]

                if not entry.is_active():
                    entry.make_activate()

                if v is None:
                    entry.enterText('')
                    entry.make_deactivate()
                    continue

                entry.enterText(str(v))

    def validate_input_values(self):
        invalid_values = 0

        for k, data_type in self.input_items.items():
            # entry = self.entries[k]
            if (entry := self.entries[k]).is_active():

                try:
                    data_type(entry.get())
                except ValueError:
                    entry.change_frame_color(warning=True)
                    invalid_values += 1
                else:
                    entry.change_frame_color()

        if invalid_values == 0:
            return True

    def get_input_values(self):
        input_values = {}

        for k, data_type in self.input_items.items():
            if (entry := self.entries[k]).is_active():
                v = data_type(entry.get())
                input_values[k] = v


            # v = data_type(self.entries[k].get())
            # input_values[k] = v

        return input_values

    def get_terrain(self):
        return self.terrain_var[0]
        # return self.terrain[0]

    def get_noise(self):
        return self.noise_var[0]
        # return self.noise[0]

    def get_theme(self):
        # return self.theme_var[0]
        return self.theme_var[0]

    def disable_buttons(self):
        for btn in self.btns:
            btn.make_deactivate()

    def enable_buttons(self):
        for btn in self.btns:
            btn.make_activate()