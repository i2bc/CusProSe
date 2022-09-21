# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 16:29:15 2020

@author: nicolas
"""
import os
import glob
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import PIL
from PIL import Image, ImageTk

from prosecda.gui import xml_parser


class Combobox():
    def __init__(self, master, match):
        self.master = master
        self.mainframe = self.master.master
        self.canvasframe = self.mainframe.canvasframe
        self.display_protein = self.canvasframe.display_protein
        self.match = match
        
        # creates combobox for protein matches
        self.label_protein = tk.Label(self.master, text = 'Select a protein')
        self.label_protein.grid(row=1, column=0, sticky='nw')
    
        values = self.match.get_protein_ids()
        self.cbb_protein = ttk.Combobox(self.master, values=values, width=10)
        self.cbb_protein.grid(row=1, column=1, sticky='nwe')
        self.cbb_protein.current(0)
        self.info_protein()
        self.cbb_protein.bind('<<ComboboxSelected>>', self.update_list) 
        
        # combobox for architectures of a selected protein
        self.label_architecture = tk.Label(self.master, text = 'Select an architecture')
        self.label_architecture.grid(row=2, column=0, sticky='nw')
        
        idx_protein = self.match.get_protein_ids().index(self.cbb_protein.get())
        architectures = self.match.proteins[idx_protein].architectures
        values = [ x.id for x in architectures ]

        self.cbb_architecture = ttk.Combobox(self.master, values=values, width=10)
        self.cbb_architecture.current(0)
        self.info_architecture()
        self.display_protein.draw_architecture(architecture=self.current_architecture_instance())
        self.cbb_architecture.bind('<<ComboboxSelected>>', self.show_architecture)
        self.cbb_architecture.grid(row=2, column=1, sticky='nwe')
        
        self.cb_var = tk.IntVar()
        self.cb = tk.Checkbutton(master, text="Show all architectures",
                                 variable=self.cb_var, command=self.show_architectures)
        self.cb.grid(row=3, sticky='w')
        
    def update_list(self, event):
        """
        Updates values of the architecture combobox according to the selected
        protein.        
        """
        # gets architectures'ids of the selected protein
        selected_prot_instance = self.current_protein_instance()
        values = selected_prot_instance.get_arch_ids()
        
        # update values
        self.cbb_architecture.configure(values=values)
        self.cbb_architecture.current(0)
        
        # writes protein and architecture selected in infobox
        self.info_protein()
        self.info_architecture()

        
        # draws currently selected architecture
#        self.canvasframe.draw_architecture(architecture=self.current_architecture_instance())
        if not self.cb_var.get():
            selected_arch_instance = self.info_architecture()
            
            # draws architectures
            self.display_protein.draw_architecture(architecture=selected_arch_instance)
        else:
            self.show_architectures()
        
    def show_architecture(self, event):
        if not self.cb_var.get():
            selected_arch_instance = self.info_architecture()
            
            # draws architectures
            self.display_protein.draw_architecture(architecture=selected_arch_instance)
        else:
            self.show_architectures()
            
    def show_architectures(self):
        if self.cb_var.get():
            selected_prot_instance = self.current_protein_instance()
            
            # draws architectures
            self.display_protein.draw_architectures(protein=selected_prot_instance)
        else:            
            # draws currently selected architecture
            self.display_protein.draw_architecture(architecture=self.current_architecture_instance())   

    def info_protein(self):
        selected_protein_instance = self.current_protein_instance()
        text = '\n- Reading Protein {}\n'.format(selected_protein_instance.id)
        text += '- Length: {}\n'.format(selected_protein_instance.length)
        self.mainframe.infoframe.insert_text(text=text)
        
    def info_architecture(self):
        selected_arch_instance = self.current_architecture_instance()
        text = '  - Architecture {}\n'.format(selected_arch_instance.id)
        text += selected_arch_instance.description()
        self.mainframe.infoframe.insert_text(text=text)
        
        return selected_arch_instance
        
    def current_protein_instance(self):
        return self.match.get_prot_by_id(_id=self.cbb_protein.get())
    
    def current_architecture_instance(self):
        selected_prot_instance = self.current_protein_instance()
        
        return selected_prot_instance.get_arch_by_id(self.cbb_architecture.get())
        

class Optionframe(tk.LabelFrame):
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master, bd=2,
                               text='Options', labelanchor='n')
        self.master = master
        self.initialize()

    def initialize(self):
        self.configure_grid()
        self.grid(sticky='nsew')
        self.grid_propagate(0)
        
    def create_cbb(self, match):    
        self.combobox = Combobox(self, match)
        
    def configure_grid(self):
        for row in range(20):
            self.rowconfigure(row, weight=1)
            
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)        


class Drawing():
    def __init__(self, canvasframe, coef):
        self.canvasframe = canvasframe
        self.root = self.canvasframe.master.master
        self.canvas = self.canvasframe.canvas
        self.coef = coef
        
    def draw_architecture(self, architecture):
        self.canvas.delete('all')
        self.images = []
        self.domains = []

        x0, y0 = 1, 50
        
        # draws the architecture sequence as a line
        self.draw_sequence(x0=x0, y0=y0, width=self.coef)
        
        # gets scaled domains coordinates and draws them
        scaled_domains = architecture.scale_domains(coef=self.coef)
        for scaled_domain in scaled_domains:
            self.draw_domain(x0=x0, y0=y0, scaled_domain=scaled_domain)
            
        self.canvas.update()
        self.bind_domains()        
        
    def draw_architectures(self, protein):
        self.canvas.delete('all')
        self.images = []
        self.domains = []
        
        y0 = 25

        for architecture in protein.architectures:            
            x0 = 1
            y0 += 25
            self.draw_sequence(x0=x0, y0=y0, width=self.coef)
            
            scaled_domains = architecture.scale_domains(coef=self.coef)
            for scaled_domain in scaled_domains:
                self.draw_domain(x0=x0, y0=y0, scaled_domain=scaled_domain)
            
        self.canvas.update()
        self.bind_domains()
        
    def draw_sequence(self, x0, y0, width):
        self.sequence = self.canvas.create_line(x0, y0, width, y0, width=1,
                                                tags='sequence')
        
    def draw_domain(self, x0, y0, scaled_domain):
        x0 = scaled_domain['from']
        width = scaled_domain['length']
        height = 10
        y0 = float(y0 - height/2.)
        color = 'blue'
        name = scaled_domain['name']
        
        self.create_rectangle(x0=x0, y0=y0, width=width, height=height,
                              name=name, fill=color, alpha=.7)
        
    def create_rectangle(self, x0, y0, width, height, name='', **kwargs):
        width = int(width)
        height = int(height)
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.root.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (width, height), fill)
            self.images.append(ImageTk.PhotoImage(image))
            domain = self.canvas.create_image(x0, y0, image=self.images[-1],
                                              anchor='nw',
                                              tags='domain')
        self.canvas.create_rectangle(x0, y0, x0+width, y0+height,
                                              **kwargs)                                          
        self.domains.append(domain)
        
    def bind_domains(self):
        if self.domains:
            for widget_id in self.domains:
                self.canvas.tag_bind(widget_id, '<Enter>', self.enter)
                self.canvas.tag_bind(widget_id, '<Leave>', self.enter)
                
    def enter(self, event):
        global widget
        widget = event.widget
        
        print(widget.winfo_id())
        
        coords = self.canvas.coords(widget.winfo_id())
        self.txt = self.canvas.create_text(100, 100, text=str(123))
        
    def leave(self, event):
        self.canvas.delete(self.txt)

class Canvasframe(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bd=1,
                          highlightbackground='black', highlightthickness=1)
        self.master = master
        self.root = self.master.master
        self.initialize()

    def initialize(self):
        self.configure_grid()
        self.grid_propagate(0)
        
        self.init_canvas()
        
    def configure_grid(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
    def init_canvas(self):
        self.canvas = tk.Canvas(self, bg='white', width=1000, height=600,
                                scrollregion=(0, 0, 1000, 600))
        self.canvas.grid(padx=5, pady=5, sticky='nsew')
        
        self.scrollb_h = tk.Scrollbar(self, orient='horizontal',
                                      command=self.canvas.xview)                                      
        self.scrollb_v = tk.Scrollbar(self, orient='vertical',
                                      command=self.canvas.yview)
                                      
        self.canvas.configure(xscrollcommand=self.scrollb_h.set,
                              yscrollcommand=self.scrollb_v.set)
                              
        self.scrollb_h.grid(row=1, column=0, sticky='nsew')
        self.scrollb_v.grid(row=0, column=1, sticky='nsew')
        
        self.display_protein = Drawing(canvasframe=self, coef=500)
        
#        self.canvas.bind("<Button-1>", self.callback)
#        
#    def callback(self, event):
#        sele = self.canvas.find_closest(event.x, event.y)
#        if sele:
#            print(sele)


class Infoframe(tk.LabelFrame):
    def __init__(self, master):
        tk.LabelFrame.__init__(self, master,
                          text='Message box', labelanchor='n')
        self.master = master
        self.initialize()
        self.create_scrollbar()

    def initialize(self):
        self.configure_grid()
        self.grid_propagate(0)
        
    def configure_grid(self):
        self.rowconfigure(0, weight=1)            
        self.columnconfigure(0, weight=1)
        
    def create_scrollbar(self):
        self.scrollb_v = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollb_v.grid(row=0, column=1, sticky='nsew')
        self.scrollb_h = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scrollb_h.grid(row=1, column=0, sticky='nsew')
        
        self.text = tk.Text(self, yscrollcommand=self.scrollb_v.set,
                            xscrollcommand=self.scrollb_h.set,
                            bg='black', fg='yellow')
        self.text.grid(row=0, column=0, sticky="nsew", padx=(1), pady=1)
        
        self.scrollb_v.config(command=self.text.yview)
        self.scrollb_h.config(command=self.text.xview)
        
    def insert_text(self, text):
        self.text.insert('end', text)
        self.text.see('end')


class MenuBar(tk.Menu):
    initialdir = '/home/nicolas/spyder_workspace/ProSeCDA/prosecda/tests/prosecda_trial/'

    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.master = master
        self.is_file_opened = False
        self.initialize()

        
    def initialize(self):
        self.file_menu = tk.Menu(self.master, tearoff=False)
        self.file_cascade()
        
    def file_cascade(self):        
        self.add_cascade(label="File", underline=0, menu=self.file_menu)
        
        self.file_menu.add_command(label="Open an xml file...", 
                                   underline=0, command=self.open_file)
        self.file_menu.add_command(label="Open an xml directory...",
                                   underline=12, command=self.open_dir)
        self.file_menu.add_command(label="Save as...",
                                   underline=0, command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit",
                                   underline=0, command=self.master.destroy)
        
    def open_file(self):
        if self.is_file_opened:
            sof = '\n'
        else:
            sof = ''
            
        xml_filename = fd.askopenfilename(initialdir=self.initialdir,
                               filetypes=[('XML files', '*.xml')])
                               
        # gets Prosecda_match instance
        match = xml_parser.Prosecda_match(xml_file=xml_filename)

        # writes log in infoframe
        text = sof+match.rule.description()
        self.master.mainframe.infoframe.insert_text(text=text+'\n')
        
        # creates comboboxes for selection
        self.master.mainframe.optionframe.create_cbb(match=match)
        
        self.is_file_opened = True
        
    def open_dir(self):
        self.dirname = fd.askdirectory(initialdir=self.initialdir)+'/'
        
        files = [os.path.basename(f) for f in glob.glob(self.dirname + "*.xml")]
#        if not files:
#            txt = 'No xml files in {}\n'.format(self.dirname)
#            self.text.insert(tk.END, txt)
#        else:        
#            self.create_combobox(values=files)
    
    def save_as(self):
        _file = fd.asksaveasfile(mode="w", defaultextension=".png")
        
#        text = self.rules_framelist.text.get("1.0",'end')
        text = "empty file"
        if _file:
            _file.write(text)
            
        _file.close()

class Mainframe(tk.Frame):
    def __init__(self, master, width, height):
        tk.Frame.__init__(self, master, width=width, height=height)
        self.master = master
        self.initialize()
        self.update()
#        print('Mainframe width: {}'.format(self.winfo_width()))

    def initialize(self):
        self.configure_grid()
        self.grid(sticky='nsew')
        self.grid_propagate(0)
        
        # creates infoframe
        self.infoframe = Infoframe(self)
        self.infoframe.grid(row=12, column=1,
                  rowspan=8, columnspan=1,
                  padx=5, pady=5, sticky='nsew')
        self.infoframe.update()
#        print('Infoframe width: {}'.format(self.infoframe.winfo_width()))
        
        # creates optionframe
        self.optionframe = Optionframe(self)
        self.optionframe.grid(row=0, column=0,
                  rowspan=20, columnspan=1,
                  padx=5, pady=5, sticky='nsew')
        self.optionframe.update()
#        print('Optionframe width: {}'.format(self.optionframe.winfo_width()))
                  
        # creates canvasframe
        self.canvasframe = Canvasframe(self)
        self.canvasframe.grid(row=0, column=1,
                  rowspan=12, columnspan=1,
                  padx=5, pady=5, sticky='nsew')
        self.canvasframe.update()
#        print('Canvasframe width: {}'.format(self.canvasframe.winfo_width()))
                  
                  
    def configure_grid(self):
        for row in range(20):
            self.rowconfigure(row, weight=1)
            
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=5)        
        

class Visual_App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.initialize()
        self.run()
        
    def initialize(self):
        self.title("Visual app for ProSeCDA")
        self.width = 900
        self.height = 600
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.menubar = MenuBar(self)
        self.config(menu=self.menubar)
        
        
    def run(self):      
        self.mainframe = Mainframe(self, width=self.width, height=self.height)
        self.update()
        self.resizable(True, True)
        self.mainloop()


if __name__ == '__main__':     
    app=Visual_App()



#path2run = 'run_2020-04-28T13.28.38.475835/xml_matches/'
#path2xml = '/home/nicolas/spyder_workspace/ProSeCDA/prosecda/tests/prosecda_trial/'+path2run
#
#xml_file = path2xml+'Fusicocadiene_synthase.xml'
#xml_file = path2xml+'NRPS.xml'
#
#
#match = xml_parser.Prosecda_match(xml_file)
#match.get_protein_ids()
#match.match_nb
#
#rule = match.rule
#rule.name
#rule.comment
#rule.mandatories
#rule.forbidden
#    
#inputs = match.inputs
#inputs.domtblout
#inputs.proteome
#inputs.yamlrules
#
#proteins = match.proteins
#protein = proteins[0]
#protein.id
#protein.sequence
#protein.length
#protein.arch_nb
#protein.architectures
#architecture = protein.architectures[0]
#    
#architecture.get_domnames()
#architecture.domains
#domain = architecture.domains[0]
#domain.from_
#domain.to_
#domain.score
#    
    








