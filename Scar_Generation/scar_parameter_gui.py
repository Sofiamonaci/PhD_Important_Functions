import gi
import sys

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Set up a class to load up mesh and visualise it in paraview/meshalyzer

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data))


# Class to set up: segment in which scar can be found, whether it is epicardial or endocardial, number of exits and entrances, and length/width of dead tissue
class Parameters(Gtk.Window):

        def __init__(self):

                Gtk.Window.__init__(self, title="Scar Parametrisation")
                self.set_size_request(400,300)
                self.timeout_id = None
                self.set_border_width(20)

########################## Scar Parameters ######################################## 
                # Create outside box
                outerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                self.add(outerbox)

                # Create vertical list alignment
                listbox = Gtk.ListBox()
                listbox.set_selection_mode(Gtk.SelectionMode.NONE)
                outerbox.pack_start(listbox, True, True, 0)

                # Load mesh and load aha file
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)

                self.button_choosefile = Gtk.Button(label="Load mesh", xalign = 0)
                self.button_choosefile.connect("clicked", self.on_file_clicked)
                hbox.pack_start(self.button_choosefile, True, True,0)
                listbox.add(row)


                # Enter whether scar is in RV or LV
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                row.add(hbox)
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                hbox.pack_start(vbox, True, True, 0)

                self.buttonLV = Gtk.RadioButton.new_with_label_from_widget(None, "LV")
                self.buttonLV.connect("toggled", self.on_button_toggled, "1")
                vbox.pack_start(self.buttonLV, False, False, 0)

                self.buttonRV = Gtk.RadioButton.new_with_label_from_widget(self.buttonLV, "RV")
                self.buttonRV.connect("toggled", self.on_button_toggled, "2")
                hbox.pack_start(self.buttonRV, False, True, 0)
                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)

                # Enter position of the scar
                label1 = Gtk.Label(label="Scar Position", xalign = 0)
                hbox.pack_start(label1, True, True,0)

                self.entry = Gtk.Entry()

                if self.buttonLV.get_active():
                    self.entry.set_text("Type here 1-17 (LV segment)")
                else:
                    self.entry.set_text("Type here 18-25 (RV segment)")

                self.entry.connect("activate", self.on_entry_activated)

                hbox.pack_start(self.entry, False, True, 0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)


                # Enter Epicardial vs Endocardial

                label2 = Gtk.Label(label="Type of Scar", xalign=0)
                hbox.pack_start(label2,True, True, 0)

                type = ["Endocardial", "Epicardial"]

                self.scar = Gtk.ComboBoxText()
                self.scar.set_entry_text_column(0)
                self.scar.connect("changed", self.combo_changed, "Type of Scar")
                for i in type:
                    self.scar.append_text(i)
                hbox.pack_start(self.scar, False,True,0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)

                # Number of Exits
                hbox.pack_start(Gtk.Label(label="Exit(s)", xalign=0), True,True,0)
                self.exit = Gtk.ComboBoxText()
                self.exit.set_entry_text_column(0)
                self.exit.connect("changed", self.combo_changed, "Exit(s)")
                for i in ["1","2"]:
                    self.exit.append_text(i)
                hbox.pack_start(self.exit, False,True,0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)
                # Number of entrances
                hbox.pack_start(Gtk.Label(label="Entrance(s)", xalign=0), True, True, 0)
                self.entrance = Gtk.ComboBoxText()
                self.entrance.set_entry_text_column(0)
                self.entrance.connect("changed", self.combo_changed, "Entrance(s)")
                for i in ["1", "2"]:
                    self.entrance.append_text(i)
                hbox.pack_start(self.entrance, False, True, 0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                row.add(hbox)
                # Number of dead ends
                hbox.pack_start(Gtk.Label(label="Dead end(s)", xalign=0), True, True, 0)
                self.d_end = Gtk.ComboBoxText()
                self.d_end.set_entry_text_column(0)
                self.d_end.connect("changed", self.combo_changed, "Dead end(s)")
                for i in ["0","1", "2"]:
                    self.d_end.append_text(i)
                hbox.pack_start(self.d_end, False, True, 0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                row.add(hbox)

                hbox.pack_start(Gtk.Label(label="Isthmus width (mm) ", xalign=0), True,True,0)
                self.scale_w = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(10, 5, 18, 0.01, 0.01, 0))

                self.scale_w.set_value_pos(Gtk.PositionType.BOTTOM)

                self.scale_w.set_hexpand(True)
                #self.scale_w.connect("drag-end", self.scale_moved)
                hbox.pack_start(self.scale_w, False,True,0)

                check_button = Gtk.CheckButton(label="Enter")
                check_button.connect("toggled", self.check_scale, "width")
                check_button.set_active(False)
                hbox.pack_start(check_button, False, True, 0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                row.add(hbox)

                hbox.pack_start(Gtk.Label(label="Isthmus length (mm)", xalign=0), True, True, 0)
                self.scale_l = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                                    adjustment=Gtk.Adjustment(10, 2, 39, 0.01, 0.01, 0))

                self.scale_l.set_value_pos(Gtk.PositionType.BOTTOM)
                self.scale_l.set_hexpand(True)

                hbox.pack_start(self.scale_l, False, True, 0)
                check_button = Gtk.CheckButton(label="Enter")
                check_button.connect("toggled", self.check_scale, "length")
                check_button.set_active(False)
                hbox.pack_start(check_button, False, True,0)

                listbox.add(row)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                row.add(hbox)

                hbox.pack_start(Gtk.Label(label="Trasmural Scar Percentage (%)", xalign=0), True, True, 0)
                self.scale_t = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                                         adjustment=Gtk.Adjustment(60, 1, 100, 1, 1, 0))

                self.scale_t.set_value_pos(Gtk.PositionType.BOTTOM)
                self.scale_t.set_hexpand(True)

                hbox.pack_start(self.scale_t, False, True, 0)
                check_button = Gtk.CheckButton(label="Enter")
                check_button.connect("toggled", self.check_scale, "transmurality")
                check_button.set_active(False)
                hbox.pack_start(check_button, False, True, 0)

                listbox.add(row)

               # Add Final item Button to return all values!
                listbox_2 = Gtk.ListBox()
                listbox_2.set_selection_mode(Gtk.SelectionMode.NONE)
                outerbox.pack_start(listbox_2, True, True,0)

                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
                row.add(hbox)


                self.final_button = Gtk.Button.new_with_label(label="Enter")
                self.final_button.connect("clicked", self.on_clicked)
                self.final_button.set_hexpand(True)
                hbox.pack_start(self.final_button, True, True, 0)

                listbox_2.add(row)

################################ Widget Signal Functions #################################
        def on_file_clicked(self, widget):
            dialog = Gtk.FileChooserDialog(title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN)
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            )

            self.add_filters(dialog)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                print("Open clicked")
                print("File selected: " + dialog.get_filename())
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")

            dialog.destroy()

        def add_filters(self, dialog):
            filter_text = Gtk.FileFilter()
            filter_text.set_name("Text files")
            filter_text.add_mime_type("text/plain")
            dialog.add_filter(filter_text)

            filter_py = Gtk.FileFilter()
            filter_py.set_name("Python files")
            filter_py.add_mime_type("text/x-python") 
            dialog.add_filter(filter_py)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            dialog.add_filter(filter_any)
        
        
        def on_button_toggled(self, button, name):
            if button.get_active():
                state = "on"
                if self.buttonLV.get_active():
                    self.entry.set_text("Type 1-17 (LV) ")
                elif self.buttonRV.get_active():
                    self.entry.set_text("Type 18-25 (RV) ")
            else:
                state = "off"



        def on_entry_activated(self, entry):
                value = self.entry.get_text()
                if isinstance(int(value),int) and (int(value)>=1 and int(value)<=25):
                    print("Scar in segment: " + value)
                    self.entry.set_text(value)
                else:
                    sys.exit('Error! Value entered must be an integer between 1 and 25!')

        def combo_changed(self,event, data="Value"):
            text = event.get_active_text()
            if text is not "Type of Scar":
                print(data + ": "+ text)

        def check_scale(self,event, data):
            if event.get_active():
                if "len" in data:
                    value = self.scale_l.get_value()
                    print("Length isthmus: %s mm" % (value))
                elif "wid" in data:
                    value = self.scale_w.get_value()
                    print("Width isthmus: %s mm" % (value))
                else:
                    value = self.scale_t.get_value()
                    print("Transmural Scar Percentage: %s percent" % (value))

        def on_clicked(self, event):
            print("All Parameters are set! Ready to Proceed")
            # Final parameters to use
            self.segment = int(self.entry.get_text())
            self.type = self.scar.get_active_text()
            self.channels = [int(self.exit.get_active_text()),int(self.entrance.get_active_text()),int(self.d_end.get_active_text())]
            self.length = float(self.scale_l.get_value())
            self.width = float(self.scale_w.get_value())
            self.trans = float(self.scale_t.get_value())
            if self.buttonLV.get_active():
                self.mesh = "LV"
            else:
                self.mesh = "RV"




################################ End Parameter Class ############################################

win = Parameters()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
