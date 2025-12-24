from enum import StrEnum

import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectGui import DirectEntry, DirectFrame, DirectLabel, \
    DirectButton, DirectRadioButton, DirectOptionMenu
from panda3d.core import Point3, LColor, Vec4
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib

from terraced_terrain.themes.themes import themes_sphere, themes_flat


class TerrainTypes(StrEnum):

    FLAT = 'Flat'
    SPHERE = 'Sphere'


class NoiseTypes(StrEnum):

    SIMPLEX = 'SimplexNoise'
    CELULLAR = 'CelullarNoise'
    PERLIN = 'PerlinNoise'


class DropDownMenu(DirectOptionMenu):

    def __init__(self, parent, pos, items, command):
        super().__init__(
            parent=parent,
            pos=pos,
            frameSize=(-3.3, 3.3, -0.7, 0.7),
            frameColor=Gui.frame_color,
            item_frameColor=Gui.frame_color,
            item_text_fg=Gui.text_color,
            scale=Gui.text_size,
            relief=DGG.SUNKEN,
            items=items,
            text_fg=Gui.text_color,
            text_pos=(-3.2, -0.3),
            popupMarker_scale=0.7,
            command=command
        )
        self.initialiseoptions(type(self))


class RadioButton(DirectRadioButton):

    def __init__(self, parent, txt, pos, variable, command):
        super().__init__(
            parent=parent,
            pos=pos,
            frameSize=(-2.5, 2.5, -0.5, 0.5),
            frameColor=(1, 1, 1, 0),
            scale=Gui.text_size,
            text_align=TextNode.ALeft,
            text=txt,
            text_pos=(-1.5, -0.3),
            text_fg=Gui.text_color,
            value=[txt],
            variable=variable,
            command=command
        )
        self.initialiseoptions(type(self))


class Button(DirectButton):

    def __init__(self, parent, txt, pos, size, command):
        super().__init__(
            parent=parent,
            pos=pos,
            relief=DGG.RAISED,
            frameSize=size,
            frameColor=Gui.frame_color,
            borderWidth=(0.01, 0.01),
            text=txt,
            text_fg=Gui.text_color,
            text_scale=Gui.text_size,
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
            text_scale=Gui.text_size,
            text_align=TextNode.ALeft
        )
        self.initialiseoptions(type(self))


class Frame(DirectFrame):

    def __init__(self, parent, frame_size, pos):
        super().__init__(
            parent=parent,
            frameSize=frame_size,
            frameColor=Gui.frame_color,
            pos=pos,
            relief=DGG.SUNKEN,
            borderWidth=(0.01, 0.01)
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
            width=width,
            scale=Gui.text_size,
            numLines=1,
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
    text_size = 0.055

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
        self.theme_menu = None

        self.terrain_var = []
        self.noise_var = []
        self.theme_var = None

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
        Frame(self, Vec4(-0.6, 0.6, -0.22, 0.22), Point3(0, 0, 0.78))
        Frame(self, Vec4(-0.6, 0.6, -0.24, 0.24), Point3(0, 0, -0.76))

        padding = 0.06
        last_z = self.create_radios(0.9, padding)
        last_z = self.create_entries(last_z - padding * 4, padding)
        self.create_buttons(last_z - padding * 4)

        self.set_default_values()

    def create_buttons(self, start_z):
        btn_size = (-0.35, 0.35, -0.05, 0.05)
        btn_half = (-0.175, 0.175, -0.05, 0.05)

        self.btns.append(Button(
            self, 'Reflect Changes', Point3(0, 0, start_z), btn_size, base.start_terrain_change))
        self.btns.append(Button(
            self, 'Output BamFile', Point3(0, 0, start_z - 0.1), btn_size, base.output_bam_file))
        self.btns.append(Button(
            self, 'Wireframe', Point3(btn_half[0], 0, start_z - 0.2), btn_half, base.toggle_wireframe))
        self.btns.append(Button(
            self, 'Rotation', Point3(btn_half[1], 0, start_z - 0.2), btn_half, base.toggle_rotation))

    def create_entries(self, start_z, padding):
        """Create a theme label and entry boxes and their labels.
        """
        self.theme_label = Label(self, 'theme', Point3(-0.32, 0.0, start_z))
        start_z -= padding * 2

        for i, name in enumerate(self.input_items.keys()):
            z = start_z - i * 0.08
            Label(self, name, Point3(-0.32, 0.0, z))
            entry = Entry(self, Point3(0.07, 0, z))
            self.entries[name] = entry

            if i == 0:
                entry['focus'] = 1

        return z

    def set_other_radios(self, radios):
        for r in radios:
            r.setOthers(radios)

    def create_radios(self, start_z, padding):
        # Create radio buttons to select terrain type.
        terrains = [m.value for m in TerrainTypes]
        self.terrain_var += terrains[:1]
        start_x = -0.18
        radios = []

        for i, name in enumerate(terrains):
            x = start_x + i * 0.25
            pos = (x, 0, start_z)
            radio = RadioButton(
                self, name, pos, self.terrain_var, self.set_default_values)
            radios.append(radio)

        self.set_other_radios(radios)

        # Create radio buttons to select noise.
        noises = [m.value for m in NoiseTypes]
        self.noise_var += noises[:1]
        start_z -= padding * 2
        radios = []

        for i, name in enumerate(noises):
            z = start_z - i * padding
            pos = (-0.18, 0, z)
            radio = RadioButton(
                self, name, pos, self.noise_var, self.set_default_values)
            radios.append(radio)

        self.set_other_radios(radios)

        return z

    def set_default_values(self):
        if self.entries:
            default_values = base.get_default_values()

            for k, v in default_values.items():
                entry = self.entries[k]

                if not entry.is_active():
                    entry.make_activate()

                if v is None:
                    entry.enterText('')
                    entry.make_deactivate()
                    continue

                entry.enterText(str(v))

            # Changing the items in DirectOptionMenu causes settings like text
            # within the menu to be lost, so it's good to be recreated each time.
            if self.theme_menu:
                self.theme_menu.destroy()

            themes_dic = themes_sphere if self.get_terrain() == TerrainTypes.SPHERE \
                else themes_flat
            items = [k.title() for k in themes_dic.keys()]

            z = self.theme_label.get_z() + 0.025
            self.thmenu_menu = DropDownMenu(self, (0.07, 0, z), items, self.select_theme)
            self.thmenu_menu.set(items[0])

    def validate_input_values(self):
        invalid_values = 0

        for k, data_type in self.input_items.items():
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

        return input_values

    def select_theme(self, selected_item):
        self.theme_var = selected_item

    def get_terrain(self):
        return self.terrain_var[0]

    def get_noise(self):
        return self.noise_var[0]

    def get_theme(self):
        return self.theme_var

    def disable_buttons(self):
        for btn in self.btns:
            btn.make_deactivate()

    def enable_buttons(self):
        for btn in self.btns:
            btn.make_activate()