# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:14:00 2020

@author: nicolas
"""
import sys
import tkinter as tk
from tkinter import filedialog as fd


class Framelist(tk.LabelFrame):
    def __init__(self, master, width=150, height=150, bd=1, title=''):
        tk.LabelFrame.__init__(self, master, width=width, height=height, bd=bd,
                          bg='white', relief=tk.FLAT,
                          highlightbackground='black', highlightthickness=2,
                          text=title, labelanchor='n')
        self.master = master
        self.initialize()
        self.create_scrollbar()
        
    def initialize(self):
        # ensure a consistent GUI size
        self.grid_propagate(0)
        
        # implement stretchability
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def create_scrollbar(self):
        self.scrollb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollb.grid(row=0, column=1, sticky='nsew')

        self.text = tk.Text(self, yscrollcommand=self.scrollb.set, bg='white')
        self.text.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        self.scrollb.config(command=self.text.yview)


class Conditionframe(tk.LabelFrame):
    def __init__(self, master, width=300, height=100, bd=2):
        tk.LabelFrame.__init__(self, master, width=width, height=height, bd=bd,
                          bg='white', relief=tk.FLAT,
                          highlightbackground='black', highlightthickness=2,
                          text='Conditions', labelanchor='n')
        self.master = master
        self.grid_propagate(0)
        self.initialize()
        
    def initialize(self):
        self.configure_grid()

        self.entries()
        self.buttons()
        
        self.mandatory_framelist = Framelist(master=self, title='Mandatory list')
        self.mandatory_framelist.grid(row=2, column=1,
                                      padx=2, pady=0,
                                      rowspan=5, columnspan=2,
                                      sticky='nw')
        
        self.forbidden_framelist = Framelist(master=self, title='Forbidden list')
        self.forbidden_framelist.grid(row=2, column=3,
                                      padx=2, pady=0,
                                      rowspan=5, columnspan=2,
                                      sticky='nw')

    def configure_grid(self):
        for i in range(8):
            self.rowconfigure(i, weight=1)
        for i in range(6):
            self.columnconfigure(i, weight=1)
            
    def entries(self):
        self.label_mandatory = tk.Label(self, text='Mandatory:', width=10, relief=tk.GROOVE)
        self.label_mandatory.grid(row=0, column=0, padx=1, pady=0, sticky='n')
        self.entry_mandatory = tk.Entry(self, width=10)
        self.entry_mandatory.grid(row=0, column=1, padx=0, pady=0, sticky='n')
        
        self.label_score = tk.Label(self, text='E-value:', width=10, relief=tk.GROOVE)
        self.label_score.grid(row=0, column=2, padx=1, pady=0, sticky='n')
        self.entry_score = tk.Entry(self, width=10)
        self.entry_score.grid(row=0, column=3, padx=0, pady=0, sticky='n')
        
        self.label_forbidden = tk.Label(self, text='Forbidden:', width=10, relief=tk.GROOVE)
        self.label_forbidden.grid(row=1, column=0, padx=1, pady=0, sticky='n')
        self.entry_forbidden = tk.Entry(self, width=10)
        self.entry_forbidden.grid(row=1, column=1, padx=0, pady=0, sticky='n')
        
    def buttons(self):
        self.insert_mandatory = tk.Button(self, text='Insert',
                                          font=("Helvetica", 11),
                                                command=self.get_mandatory)
        self.insert_mandatory.grid(row=0, column=4, padx=0, sticky='ne')
        
        self.insert_forbidden = tk.Button(self, text='Insert',
                                          font=("Helvetica", 11),
                                                command=self.get_forbidden)
        self.insert_forbidden.grid(row=1, column=4, padx=0, sticky='ne')
        
    def get_mandatory(self):
        entry_mand = self.entry_mandatory.get()
        entry_score = self.entry_score.get()
        text = ''
        
        if entry_mand and entry_score:
            text = '{}, {}\n'.format(entry_mand, entry_score)
        elif entry_mand and not entry_score:
            text = '{}\n'.format(entry_mand)
            
        self.mandatory_framelist.text.insert("end", text)
        
        self.entry_mandatory.delete(0, len(entry_mand))
        self.entry_score.delete(0, len(entry_score))
        
    def get_forbidden(self):
        entry_forb = self.entry_forbidden.get()
        text = ''
        
        if entry_forb:
            text = '{}\n'.format(entry_forb)
            
        self.forbidden_framelist.text.insert("end", text)
        
        self.entry_forbidden.delete(0, len(entry_forb))
        
    def clear(self):
        entry_mand = self.entry_mandatory.get()
        entry_score = self.entry_score.get()
        if len(entry_mand) != 0:
            self.entry_mandatory.delete(0, len(entry_mand))
        if len(entry_score) != 0:
            self.entry_score.delete(0, len(entry_score))
            
        self.mandatory_framelist.text.delete("1.0",'end')
            
        entry_forb = self.entry_forbidden.get()
        if len(entry_forb) != 0:
            self.entry_forbidden.delete(0, len(entry_forb))
            
        self.forbidden_framelist.text.delete("1.0",'end')
        

class Ruleframe(tk.LabelFrame):
    def __init__(self, master, width=400, height=360, bd=2):
        tk.LabelFrame.__init__(self, master, width=width, height=height, bd=bd,
                          bg='white', relief=tk.FLAT,
                          highlightbackground='black', highlightthickness=2,
                          text='Rule definition', labelanchor='n')
        self.master = master
        self.grid_propagate(0)
        self.initialize()
        
    def initialize(self):
        self.configure_grid()

        self.entries()

        self.conditionframe = Conditionframe(master=self)
        self.conditionframe.grid(row=1, column=0, padx=10, pady=2, rowspan=5,
                                 columnspan=6, sticky='nsew')

    def configure_grid(self):
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for i in range(6):
            self.columnconfigure(i, weight=1)

    def entries(self):
        self.label_name = tk.Label(self, text='Name:', width=5, relief=tk.GROOVE)
        self.label_name.grid(row=0, column=1, padx=1, pady=0, sticky='ew')
        self.entry_name = tk.Entry(self, width=6)
        self.entry_name.grid(row=0, column=2, padx=0, pady=0, sticky='ew')

        self.label_comment = tk.Label(self, text='Comment:', width=10, relief=tk.GROOVE)
        self.label_comment.grid(row=0, column=3, padx=1, pady=0, sticky='ew')
        self.entry_comment = tk.Entry(self, width=6)
        self.entry_comment.grid(row=0, column=4, padx=0, pady=0, sticky='ew')

    def get_conditions(self):
        mand_list = self.conditionframe.mandatory_framelist.text.get("1.0",'end-1c')
        forbid_list = self.conditionframe.forbidden_framelist.text.get("1.0",'end-1c')

        return mand_list, forbid_list
        
    def clear(self):
        self.entry_name.delete(0, len(self.entry_name.get()))
        self.entry_comment.delete(0, len(self.entry_comment.get()))
        
        self.conditionframe.clear()      


class Mainframe(tk.LabelFrame):
    def __init__(self, master, width=1000, height=680, bd=2):
        tk.LabelFrame.__init__(self, master, width=width, height=height, bd=bd,
                          bg='white', relief=tk.FLAT,
                          highlightbackground='black', highlightthickness=2,
                          labelanchor='n')
        self.master = master
        self.initialize()

    def initialize(self):
        self.configure_grid()
        self.grid(padx=5, pady=5, sticky='nswe')
        self.grid_propagate(0)

        self.ruleframe = Ruleframe(master=self)
        self.ruleframe.grid(row=0, column=0,
                            padx=2, pady=1,
                            rowspan=4, sticky='nsew')
        self.ruleframe.grid_propagate(0)

        self.rules_framelist = Framelist(master=self, title='Rule list')
        self.rules_framelist.grid(row=2, column=1,
                                      padx=2, pady=1,
                                      rowspan=2, sticky='new')

        self.buttons()
        
    def configure_grid(self):
        for row in range(5):
            self.rowconfigure(row, weight=1)
            
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        
    def buttons(self):
        self.clear_rule = tk.Button(self, text='Clear rule', bg='grey',
                                  fg='white', font=("Helvetica", 11, 'bold'),
                                  command=self.clear)
        self.clear_rule.grid(row=0, column=1, sticky='n')
        
        self.add_rule = tk.Button(self, text='Add rule to the list', bg='grey',
                                  fg='white', font=("Helvetica", 11, 'bold'),
                                  command=self.get_rule)
        self.add_rule.grid(row=1, column=1, sticky='n')
        
        self.save_rules = tk.Button(self, text='Save rules', bg='grey',
                                  fg='white', font=("Helvetica", 11, 'bold'),
                                  command=self.save_as)
        self.save_rules.grid(row=4, column=1, sticky='n')

    def get_rule(self):
        name = self.ruleframe.entry_name.get()
        comment = self.ruleframe.entry_comment.get()
        mand_list, forbid_list = self.ruleframe.get_conditions()
        
        mand_text = '\n'.join([ '  - '+x for x in mand_list.split('\n')[:-1]  ])
        forbid_text = '\n'.join([ '  - '+x for x in forbid_list.split('\n')[:-1]  ])
      
        if name and mand_list:        
            text = '{}:\n'.format(name.strip())
            text += ' COMMENT: {}\n'.format(comment.strip())
            text += ' CONDITION:\n'.format()
            text += '  mandatory:\n{}'.format(mand_text+'\n')
            text += '  forbidden:\n{}'.format(forbid_text+'\n')
    
            self.rules_framelist.text.insert('end', text+'\n')
            
            self.clear()
        
    def clear(self):
        self.ruleframe.clear()
        
    def save_as(self):
        _file = fd.asksaveasfile(mode="w", defaultextension=".yaml")
        
        text = self.rules_framelist.text.get("1.0",'end')
        if _file:
            _file.write(text)
            
        _file.close()


def main():
    master = tk.Tk()
    master.title("Setting rules for ProSeCDA")
    app = Mainframe(master=master)
    app.mainloop()

if __name__ == '__main__':
    sys.exit(main())
    
    




